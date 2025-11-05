Date: November 4, 2025
Tags: ai, vibe coding
Summary: Introducing Vibescript, a Ruby-like scripting language designed to be easy to read and easy for AI to vibe code.

# Introducing Vibescript

As vibe coding grows in popularity, there are domains where we want to narrow what users can build. Instead of giving a blank canvas, we can offer an opinionated set of well-defined primitives that combine into predictable, safe applications. Think of it less like traditional software development and more like HyperCard: flexible, but within bounds.

Even in these constrained environments, non-technical users still need a way to express custom logic. That is the problem Vibescript tries to solve. Vibescript is a Ruby-like scripting language designed to be easy to read and easy for AI to vibe code. The interpreter is written in Go and can be embedded directly into any Go application.

![Vibescript sample](/_Images/vibescript.png)

## What Vibescript is

Vibescript is an embeddable language with a small, practical standard library. It favors readability, predictable evaluation, and host-controlled capabilities. You decide which actions the script can perform. The script stays in its lane.

The language looks like Ruby at a glance: methods, blocks, symbols, arrays, and hashes. It borrows the parts that make everyday automation feel natural, without pulling in a sprawling runtime.

## A tiny tour

**Functions**

```ruby
def total_with_fee(amount)
  amount + 1
end

total_with_fee(99) # => 100
```

**Literals and collections**

```ruby
# numbers, strings, symbols
5
"hello"
:signed

# arrays
[1, 2, 3].map { |n| n * n } # => [1, 4, 9]

# hashes with symbol keys
user = { :id => 42, :name => "Ava" }
user[:name] # => "Ava"
```

**Blocks and enumerable helpers**

```ruby
# select, map, reduce
scores = [3, 10, 7, 10, 5]

top = scores.select { |s| s >= 7 } # => [10, 7, 10]
sum = scores.reduce(0) { |acc, s| acc + s } # => 35
avg = sum / scores.length # integer math for now
```

**Control flow**

```ruby
def fib(n)
  if n <= 1
    n
  else
    fib(n - 1) + fib(n - 2)
  end
end
```

**Ranges and loops**

```ruby
1..5 # inclusive range
(1..5).each { |n| print(n) } # prints 12345
```

**Durations and money**

```ruby
# examples focus on readable business logic
2.hours.to_seconds # planned helpers for derived values
money_cents(1299) + 200 # => 1499
```

[The repo](https://github.com/mgomes/vibescript) ships categorized examples for basics, collections, control flow, blocks, hashes, loops, ranges, money, durations, errors, and more in `examples/`. Some directories sketch future features and background jobs to track interpreter progress.

## The safety model: capabilities you control

Vibescript does not reach outside the sandbox unless you let it. The host app passes data and capabilities into a call. Scripts use what they are handed and nothing else.

At the API level, you compile a script, then call functions with `CallOptions`. You can seed `Globals` for pure values or register typed adapters through `Capabilities`. The README's quick start shows the basic shape and explains this integration point.

## Embedding in Go

```go
package main

import (
    "context"
    "fmt"

    "vibescript/vibes"
)

func main() {
    engine := vibes.NewEngine(vibes.Config{})

    // Compile inline or load from a .vibe file
    script, err := engine.Compile(`
    def greet(name)
      "Hello, #{name}"
    end
    `)
    if err != nil {
        panic(err)
    }

    // Call a function with arguments and optional capabilities
    res, err := script.Call(
        context.Background(),
        "greet",
        []vibes.Value{vibes.NewString("world")},
        vibes.CallOptions{
            // Globals: map[string]vibes.Value{...}
            // Capabilities: map[string]any{...}  // host adapters
        },
    )
    if err != nil {
        panic(err)
    }

    fmt.Println(res.String()) // Hello, world
}
```

This is the pattern: compile, pass in values and capabilities, call a named function, get a strongly-typed result back.

## Blocks as the core mechanic

A lot of useful automation is enumerable work: filter a collection, transform items, reduce into a report. Blocks make that feel compact. The language leans on readable block forms for day-to-day data shaping.

```ruby
orders = [
  { :id => 1, :cents => 1299, :status => :paid },
  { :id => 2, :cents => 499, :status => :void },
  { :id => 3, :cents => 2599, :status => :paid }
]

paid = orders
  .select { |o| o[:status] == :paid }
  .map { |o| o[:cents] }
  .reduce(0) { |acc, c| acc + c }

money_cents(paid) # => 3898
```

## Errors as validation

Use `assert` for simple guardrails. Fail fast and keep scripts honest.

```ruby
def apply_discount(cents, pct)
  assert(pct >= 0 && pct <= 100, "discount must be 0..100")
  cents - (cents * pct / 100)
end
```

## Policy hooks and "safe by design"

The vision is to pair readable scripts with host-level policies. The host declares what is allowed: which capabilities exist, which inputs are trusted, and which operations require a check. Scripts remain simple. The platform stays safe.

You can see the direction in the [`examples/policies/`](https://github.com/mgomes/vibescript/tree/master/examples/policies) and [`examples/capabilities/`](https://github.com/mgomes/vibescript/tree/master/examples/capabilities) folders, along with notes pointing to future background jobs and events as host integrations mature.

## Where Vibescript fits

Vibescript thrives when you need:

- A readable, AI-friendly way to customize a product without unbounded power.
- Business logic that product managers and ops can read without decoding a framework.
- Deterministic execution with a small, testable surface area.
- A guardrail-first integration story where the host is in control.

It is not trying to be a general purpose language with a giant package ecosystem. It is a tool for shaping small automations inside bigger systems.

## Getting started

[The README](https://github.com/mgomes/vibescript) has a quick start with a tiny Go program. Scripts can live in `.vibe` files or be embedded inline. Examples are grouped by topic under `examples/`. Long-form guides live in `docs/` and cover arrays, hashes, control flow, blocks, and integration.

```bash
# run tests and linters in the repo
just test
just lint
```

## Roadmap

The repository keeps stretch examples around to guide development. That includes background jobs, events, richer duration helpers, and more complete money handling. Those examples exist to keep the interpreter honest as features land.

## Closing

Vibescript is a small language with a specific goal: let people shape useful behavior inside safe bounds. If that sounds like the missing layer between your product and your users, try it in a small corner of your app and grow from there.

---

## Links

- The repo with documentation and more examples: [https://github.com/mgomes/vibescript](https://github.com/mgomes/vibescript)
