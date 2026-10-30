---
name: core-dump-analyze
description: "Open a core file with the matching binary, identify the faulting frame and capture the state that supports the crash claim. Use when the process already crashed and a core file was preserved"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [post-mortem, core, crash]
phase: post-mortem
---

# Analyse a core dump for the crashing instruction

> Open a core file with the matching binary, identify the faulting frame and capture the state that supports the crash claim

**Use when:** the process already crashed and a core file was preserved

**Avoid when:** the core was produced from a different build than the binary you have

## Procedure

1. Confirm the core matches the binary by build-id or by a recorded checksum before opening it.
2. Load with gdb ./binary core and capture bt, info registers and the faulting instruction.
3. Identify the fault type from the signal and the faulting address, and record both.
4. Save the GDB session transcript as the evidence rather than a retyped summary.

## Signals

- core-matched
- fault-frame-captured
- transcript-saved

## Patterns

**1. core analysis**

```
gdb -q ./server core.4711 -batch -ex 'bt 20' -ex 'info registers' -ex 'x/4i $pc' -ex 'info signal SIGSEGV'
```

## Pitfalls

- Analysing a core against a rebuilt binary produces a confident but wrong backtrace.
- Optimised builds can lose the innermost frame, so state that rather than inventing a caller.

## Done when

- The core is proven to match the binary and the faulting frame is captured.
- The transcript is stored with the finding.

## References

- [GDB core files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Core-File-Generation.html)
