Date: June 6, 2026
Tags: ai, vibe coding, vibescript, go
Summary: Vibescript v0.40.0 adds Tasks, a small structured-concurrency API backed by bounded Go goroutines.

# Vibescript v0.40.0

[Vibescript v0.40.0](https://github.com/mgomes/vibescript/releases/tag/v0.40.0) is out. The main addition is `Tasks`, a small structured-concurrency API for scripts that need bounded fanout.

The common case is pretty simple. You have a list of things, each thing needs the same independent operation, and the host is fine running a few of those operations at once:

```ruby
scores = Tasks.map(users, with: :score_user)
```

That is the whole pitch. Not fibers, not arbitrary threads, not a second scheduler hidden inside the language. Just a scoped way to say: these named function calls can run concurrently, and they should all finish before the script leaves this block.

{{more}}

## Tasks

`Tasks.map` is for the straightforward collection case. It preserves input order, even if individual calls finish in a different order:

```ruby
def score_user(user)
  user[:score] * user[:weight]
end

def score_users(users)
  Tasks.map(users, max: 4, with: :score_user)
end
```

`Tasks.run` is for cases where the script wants to start different functions and combine the results manually:

```ruby
def prepare_user(user)
  "prepared:" + user[:id]
end

def prepare_pair(first, second)
  Tasks.run(max: 2) do |tasks|
    left = tasks.spawn(:prepare_user, first)
    right = tasks.spawn(:prepare_user, second)

    [left.value, right.value]
  end
end
```

`Tasks.run` returns the block value. It also waits automatically at scope exit, so `tasks.wait` is not cleanup ceremony. It is only needed when later code inside the same block needs an explicit barrier:

```ruby
Tasks.run do |tasks|
  tasks.spawn(:warm_cache)
  tasks.wait

  use_cache()
end
```

That was one of the design constraints from the beginning. A task cannot outlive the `Tasks.run` or `Tasks.map` scope that created it.

## Does this map to goroutines?

Yes, but not one goroutine per item.

Vibescript is written in Go, and each task scope creates a bounded worker group backed by goroutines. If you write:

```ruby
scores = Tasks.map(users, max: 8, with: :score_user)
```

the runtime creates a worker group sized to eight and feeds the input items through it. If `users` has 10,000 entries, that still means eight task workers, not 10,000 goroutines. `max:` is fanout.

`Tasks.run` uses the same shape. `tasks.spawn` queues named function calls into the scoped worker group, and the group waits before the block returns.

The host controls the defaults:

```go
engine, err := vibes.NewEngine(vibes.Config{
    DefaultTaskConcurrency: 4,
    MaxTaskConcurrency:     16,
})
```

`DefaultTaskConcurrency` defaults to `4`. `MaxTaskConcurrency` defaults to `64`. If the host sets a lower cap, the implicit default follows that lower cap.

If a script asks for a `max:` above the host cap, Vibescript raises a runtime error. I considered silently clamping, but an explicit error is clearer. A script that asks for `max: 100` and gets `max: 16` is not running with the settings it requested.

## Boundaries

The important part of this feature was not starting goroutines. Go makes that easy.

The important part was preserving Vibescript's containment model. Each task call gets fresh execution state. Arguments are cloned. Keyword arguments are cloned. Return values are cloned. Mutable globals inherited from the host call are cloned per task.

Task inputs and results must be data-only: scalars, arrays, hashes, objects, and other non-callable values. Functions, blocks, builtins, capabilities, and cyclic structures cannot cross the task boundary.

This means `Tasks` is less general than fibers or closures. That is intentional. A hosted scripting language has different constraints than a general-purpose language. The host owns capabilities, quotas, cancellation, module policy, strict effects, and the maximum amount of fanout it is willing to allow. The script should be able to describe independent work without taking over those boundaries.

## How synctest changed the tests

Concurrent tests often end up with sleeps in them. Sleep long enough for the worker to start. Sleep a little longer and hope it has not finished. It works until CI is slow or the scheduler makes a different choice.

Go's [`testing/synctest`](https://go.dev/blog/testing-time) is a good fit for this. It runs concurrent code inside a controlled bubble and lets the test wait until goroutines in that bubble are blocked. The earlier [Go blog post on synctest](https://go.dev/blog/synctest) has the broader motivation.

For `Tasks`, `synctest` let us test the behavior we actually cared about:

- `Tasks.run` does not return before spawned work finishes.
- `Tasks.map` respects the default concurrency limit.
- `tasks.wait` is a real barrier inside the block.
- A task failure is preserved even when the parent is still trying to enqueue more work.

No sleeps. No timing guesses.

We also added a Go 1.26 [`goroutineleak` profile](https://go.dev/doc/go1.26#goroutineleak-profiles) check for the runtime tests. That is a useful backstop for this feature: if task scopes are supposed to wait for their work, the test suite should catch leaked goroutines.

That made the implementation easier to keep small. The tests can observe the concurrency shape directly, so the code does not need extra delays, knobs, or special cases just to make tests pass.

## Keeping it small

The other design choice was what not to add.

I looked at a more fiber-like API. I also thought about letting scripts spawn arbitrary blocks. Both are appealing, but they make ownership harder to explain. Can a spawned block mutate a local from the parent function? Does it capture a capability? What happens to a handle after the parent scope exits? How much interpreter state is now shared across goroutines?

Those are solvable problems, but solving them would make Vibescript larger in the wrong place.

The goal with Vibescript has always been to keep the language small enough for a host application to reason about. `Tasks.map` says "run this named operation over this collection." `Tasks.run` says "within this scope, start these named operations and wait before leaving."

That covers the use case without turning Vibescript into a concurrency runtime with a scripting language attached.
