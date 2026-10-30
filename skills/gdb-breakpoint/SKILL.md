---
name: gdb-breakpoint
description: "Halt at a chosen function or line and capture registers, arguments and the call stack at the exact moment the code runs. Use when you need to inspect state at a known point and the program can tolerate being paused"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [gdb, breakpoint, stop]
phase: debug
---

# Stop execution at a function with a GDB breakpoint

> Halt at a chosen function or line and capture registers, arguments and the call stack at the exact moment the code runs

**Use when:** you need to inspect state at a known point and the program can tolerate being paused

**Avoid when:** the function is called at a rate where a breakpoint per call would stall the target

## Procedure

1. Set the breakpoint by symbol, file:line, or address, preferring symbol plus offset.
2. Run or continue until the breakpoint reports a stop, and confirm the stopped frame is the one you asked for.
3. Capture info args, info locals, info registers and bt before stepping anywhere.
4. Delete the breakpoint or continue, and record how many times it was hit.

## Signals

- breakpoint-set
- stop-confirmed
- state-captured

## Patterns

**1. break and capture**

```
gdb -q ./target -batch -ex 'break parse_header' -ex 'run' -ex 'info args' -ex 'bt 5'
```

## Pitfalls

- A breakpoint on an inlined function may never report a stop, because there is no call to break on.
- With optimisation on, info args and info locals can be optimised out entirely.

## Done when

- The stop is confirmed on the intended frame.
- Arguments, locals and backtrace are captured as evidence.

## References

- [GDB breakpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Breakpoints.html)
