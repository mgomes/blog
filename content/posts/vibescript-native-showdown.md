---
title: Vibescript in the Native Showdown
date: '2026-07-08'
tags:
- vibescript
- go
- performance
- benchmarks
description: Optimizing Vibescript performance in the march toward 1.0.
url: "/vibescript-in-the-native-showdown/"
---

Mario Arias runs a series called [Comparing Programming Languages](https://marioarias.hashnode.dev/comparing-programming-languages-xii-the-native-showdown). He has written the same interpreter, the [Monkey language](https://interpreterbook.com/) from Thorsten Ball's book, in a whole pile of languages, and every so often he lines them up and makes them race. The twelfth post is a native showdown. He took the implementations that compile to a native binary, handed each one the same tiny Monkey program, and timed them.

The program is naive recursive Fibonacci:

```javascript
let fibonacci = fn(x) {
  if (x < 2) { return x; }
  else { fibonacci(x - 1) + fibonacci(x - 2); }
};
fibonacci(35);
```

I will just call it `fib(35)`. It is a genuinely mean little benchmark: no clever math, no memoization, just about 29.8 million function calls stacked on top of each other. It is a pure test of how fast an interpreter can walk its own tree.

As it happens, the [Vibescript](https://github.com/mgomes/vibescript) runtime is itself a tree-walking interpreter, written in Go. So when I read Mario's post I thought I'd run the same benchmark ahead of Vibescript's 1.0 release.

<!--more-->

## Why it's a fair fight

The first thing to get straight is what is actually being measured, because "native showdown" sounds like it should be C and Rust doing `fib(35)` in forty milliseconds. It is not. Every entry in Mario's table is a tree-walking interpreter reading the Monkey program and evaluating it node by node. The native part is that the interpreter itself is compiled. A fast entry means a fast interpreter, not a fast Fibonacci.

That is exactly the shape of Vibescript, which is what makes it a fair fight. Here is the same function in Vibescript's Ruby-flavored syntax:

```ruby
def fib(n)
  if n < 2
    n
  else
    fib(n - 1) + fib(n - 2)
  end
end

fib(35)
```

Mario ran his benchmarks on an M5. I unfortuntately don't have one of those. I do have access to an M4 Mac Mini, and the machine I am typing on is an older M1 Max. The table below shows the results of each test and the corresponding chip that powered it through.

| Interpreter (Monkey unless noted) | Chip   | fib(35) (s) | RAM (MB) |
| --------------------------------- | ------ | ----------- | -------- |
| Crystal                           | M5     | 3.23        | 3.9      |
| Kotlin (Graal)                    | M5     | 4.80        | 59.0     |
| Go                                | M5     | 6.00        | 27.8     |
| **Vibescript**                    | M4     | ~6.7        | ~8.2     |
| **Vibescript**                    | M1 Max | ~10.5       | ~8.8     |
| Scala Native (continuations)      | M5     | 14.77       | 7.3      |
| Kotlin Native (inline)            | M5     | 16.40       | 15.0     |
| Kotlin Native                     | M5     | 17.75       | 14.9     |
| Scala (Graal)                     | M5     | 23.88       | 59.2     |
| Scala Native                      | M5     | 165.12      | 7.5      |

Vibescript is not winning any medals, but it is sitting comfortably mid-pack, a hair behind the Go Monkey and ahead of every Kotlin and Scala native build, and it does it in under 10 MB, a seventh of the memory the Graal builds need. That is a decent place to be. I would also expect a small performance boost if we were to run the Vibescript test on a similar M5 machine.

## What the sandbox is protecting

Monkey is a teaching interpreter. It runs the program and trusts it. Vibescript does not get to trust the program, because it is built to be embedded inside a host application and handed scripts the host did not write. So it carries a sandbox: a step quota that stops runaway loops, a recursion limit, a capability system so a script can only touch the host functions it was explicitly granted, static type checking before anything runs, cancellation through a context, and the interesting one, a memory quota that bounds how much heap a script is allowed to retain.

That last one is where "doing more work" turns into a real cost for Vibescript. To enforce a memory quota we need to know, at every moment, how much memory the script is holding. Vibescript works this out by walking the reachable object graph and adding up what it finds: the whole environment stack, every loaded module, and the running task state. Call it the accounting layer.

The catch is that this number is a security boundary. If the estimate comes out too high, no harm done, the script hits its limit a little early. If it comes out too low, a script can quietly retain more memory than it is allowed, which is a sandbox escape. So the accounting has to be close to exact.

## The accounting used to cost everything

When I first tried to run `fib(35)` under a memory quota, it wouldn't even finish. With the quota cranked way up it took minutes. I profiled it expecting to find a slow path in the evaluator, and instead found something funny: the memory accounting was 97% of the runtime cost. The interpreter was fine. The safety check wrapped around the sandbox was dragging it down like an anchor.

Inside the accounting layer, there was a quadratic hiding. The accounting walked the entire live stack on every check, and there is roughly a check per step, so a recursion 35 frames deep paid for that depth over and over. `O(depth)` work, done `O(depth)` times, is `O(depth squared)`. On `fib` that squared term ate everything.

The most impactful fix started from one observation. A stack frame that holds only an immutable scalar, an integer or a boolean, cannot grow and cannot secretly share memory with anything else. So you can add those frames up once, as they pile on, and on later checks re-examine only the small active tip of the stack. For pure recursion like `fib`, that drops the per-check cost from `O(depth)` back to nearly constant. The moment a script does something trickier, a block or a closure that could reach back and mutate an older frame, the whole scheme gives up and does the slow exact walk again. `fib` never does anything tricky, so it stays on the fast path all the way down. Along the way, recycling the per-call environment and pooling argument slices took `fib(20)` from about 65,700 allocations down to 82.

Because a wrong number here is a security hole, we had to pack the life preservers. I built the faster accounting path under a differential oracle: a debug mode, off in anything that ships, where every check also computes the slow exact answer and crashes if the two disagree. Under it I ran the whole test suite, the race detector, and millions (8.4M to be exact) of fuzzer-generated programs, plus several more campaigns on the block-iteration one. It found no disagreemnts. The optimization itself ships always-on. I kept the oracle flag in, though, and each night when the fuzzer runs millions of programs it's looking for disagreements.

The same quadratic turned up twice more wearing different hats. Sizing a large hash rebuilt its contents from scratch on every check, so a 600-key `tally` was allocating 54 MB per call for a histogram that should cost kilobytes. And iterating a collection with a block, the single most common thing real scripts do, re-walked the whole collection on every step: `group_by` over 600 rows took 210 ms under a quota against 0.3 ms without, a 700x tax for the privilege of being sandboxed. Both had the same fix as `fib`. Find the part that cannot have changed, and stop re-measuring it. `group_by` is now 0.94 ms. The lesson I keep relearning is that a safety check which measures the whole world on every step is always one big object away from turning linear work quadratic. There will probably be a next one.

## Where it landed

These benchmarks were run via the Vibescript CLI, whose default sandbox profile is `xhigh` (the code-based runtime defaults to `low`). The `xhigh` profile does not set a memory quota at all, so the accounting is switched off entirely. That 10.5 seconds of fib(35) on my M1 Max is pure tree-walking, not much of it is the sandbox tax. Turn memory quota on and the same fib(35) takes about 50 seconds on this machine (~5x slower) and 28 seconds on the M4 (~4x slower), while its actual memory footprint never budges from about 5 MB. The 4-5x is the accounting layer, and the whole push above is what turned it from “minutes, or would not run at all” into “4-5 times slower”.

The instruction counts tell the cleanest version of the comparison. My M4 and this M1 Max both retire about 152 billion instructions to compute `fib(35)`, within a rounding error of each other. Same work. The M4 just gets through it faster, because it is a newer core. None of the wall-clock gap between my two machines is Vibescript. All of it is silicon. And against Mario's M5 lineup, a sandboxed, statically typed Vibescript on an M4 lands right next to a bare Go Monkey, which is more than I expected when I started.

Vibescript is [very close to 1.0](/posts/vibescript-structured-concurrency) now, and performance tweaks like these are the biggest things that remain. It is a strange kind of fun, spending a week optimizing an accounting layer. I had a lot of it. The code is [on GitHub](https://github.com/mgomes/vibescript) if you want to poke at it.

PS, Vibescript has a new domain! [https://vibescript-lang.org](https://vibescript-lang.org)
