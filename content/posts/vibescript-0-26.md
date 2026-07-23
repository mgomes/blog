---
title: Vibescript v0.26.2
date: '2026-03-08'
tags:
- ai
- vibe coding
- vibescript
description: Vibescript v0.26.2 ships a working interpreter, a REPL, gradual typing,
  editor tooling, and a companion website.
url: "/vibescript-v0-26-2/"
---

Back in November I [introduced Vibescript](/posts/introducing-vibescript) as an embeddable scripting language for constrained, AI-friendly environments. Four months later, it works end-to-end. Version 0.26.2 ships a fully functional interpreter, a rich REPL, gradual typing, editor tooling, and [a companion website](https://vibescript.mauriciogomes.com).

## The REPL

Run `vibes repl` and you land in terminal UI with tab completion for built-ins, keywords, and your own variables. Arrow keys navigate command history. Toggle `:help` or `ctrl+k` for a shortcut reference, `:vars` or `ctrl+v` to inspect live bindings, `:functions` to list what you can call.

A quick session:

```ruby
vibes> scores = [3, 10, 7, 10, 5]
=> [3, 10, 7, 10, 5]
vibes> scores.select { |s| s >= 7 }
=> [10, 7, 10]
vibes> :vars
scores = [3, 10, 7, 10, 5]
```

## Gradual typing

Type annotations are optional. Add them where they help, skip them where they don't. The interpreter checks at runtime and raises clear errors on mismatches.

```ruby
enum Status
  Draft
  Published
  Archived
end

def publish(article: hash, status: Status) -> string
  assert(article[:title], "title required")
  article[:status] = status
  "Published: " + article[:title]
end

publish({ title: "Hello" }, :draft)  # symbol auto-coerces to Status::Draft
```

Nullable types use `?`. Keyword arguments work at call sites. Enums carry identity — `Status::Draft` is not the same as `ReviewState::Draft`, even though both coerce from `:draft`.

```ruby
def maybe_increment(value: int?, step: int = 1) -> int?
  if value == nil
    nil
  else
    value + step
  end
end

maybe_increment(nil)           # => nil
maybe_increment(3, step: 10)   # => 13
```

## Time, duration, and money

These ship as built-in types. The goal with Vibescript is ensure the language supports common user scenarios (like money). Duration literals read like English (thanks [ActiveSupport::Duration](https://api.rubyonrails.org/classes/ActiveSupport/Duration.html)) and compose with arithmetic:

```ruby
timeout = 2.hours + 30.minutes      # 9000 seconds
scaled = 10.seconds * 3             # 30 seconds
ratio = 10.seconds / 4.seconds      # 2.5

deadline = 2.hours.after(Time.now)
cutoff = 5.minutes.ago(Time.now)
```

Time objects format with Go-style layouts and expose day-of-week predicates:

```ruby
t = Time.utc(2026, 3, 8)
t.format("2006-01-02")   # "2026-03-08"
t.saturday?               # true
```

Money tracks cents and currency, prevents cross-currency mistakes or float-rounding footguns:

```ruby
gross = money("50.00 USD") + money("12.50 USD")
net = gross - money("1.75 USD")
```

## Safety tightened

The [intro post](/posts/introducing-vibescript) covered the philosophy: the host controls what scripts can do. Now the knobs exist. Configure step quotas, recursion limits, memory caps, and strict effects mode at the engine level:

```go
engine, err := vibes.NewEngine(vibes.Config{
    StepQuota:        20_000,
    MemoryQuotaBytes: 256 << 10,  // 256 KiB
    RecursionLimit:   32,
    StrictEffects:    true,
})
```

Hit a limit and the interpreter raises a runtime error. No silent runaway loops, no unbounded allocations.

## Editor and tooling

A [tree-sitter grammar](https://github.com/mgomes/tree-sitter-vibescript) powers syntax highlighting. A [Zed extension](https://zed.dev/extensions/vibescript) bundles highlighting and LSP support. On the command line: `vibes fmt` formats code, `vibes analyze` catches unreachable statements, and `vibes lsp` speaks Language Server Protocol over stdio for hover, completion, and diagnostics.

## Website and docs

The companion site at [vibescript.mauriciogomes.com](https://vibescript.mauriciogomes.com) hosts runnable examples pulled from the repo. Pick an example, read the source, hit run, see the output. The [GitHub repo](https://github.com/mgomes/vibescript) has full documentation under `docs/` covering typing, enums, durations, time, and integration.

## What's next

Vibescript started as a sketch. Now it runs real scripts, catches type errors, formats its own code, and has a home on the web. The next stretch is richer host integrations — background jobs, events, and deeper capability adapters. If you embed scripting in Go, [give it a look](https://github.com/mgomes/vibescript).

Reach out if you have any questions or run into any bugs! This project has been extremely fun.
