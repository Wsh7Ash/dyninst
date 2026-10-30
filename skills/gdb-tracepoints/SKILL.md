---
name: gdb-tracepoints
description: "Sample values at chosen points without halting the program, then read the trace buffer back, which suits hot paths a breakpoint cannot survive. Use when a breakpoint per hit would stall the target but you still need values from those points"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [gdb, tracepoint, sampling]
phase: trace
---

# Collect data with GDB tracepoints instead of stopping

> Sample values at chosen points without halting the program, then read the trace buffer back, which suits hot paths a breakpoint cannot survive

**Use when:** a breakpoint per hit would stall the target but you still need values from those points

**Avoid when:** the trace buffer would wrap before the interesting event occurs

## Procedure

1. Create a tracepoint at the address with trace, and attach actions that save only the values you need.
2. Size the trace buffer for the expected event count, or accept wrapping and record that it wrapped.
3. Run the program, then inspect collected samples with tfind and tdump.
4. Export the samples and state the sampling window, because a tracepoint set is not a complete log.

## Signals

- tracepoint-created
- samples-collected
- window-stated

## Patterns

**1. tracepoint**

```
gdb -q ./target -batch -ex 'trace parse_header' -ex 'actions' -ex 'collect $rdi, $rsi' -ex 'end' -ex 'tstart' -ex 'run' -ex 'tstop' -ex 'tdump'
```

## Pitfalls

- Presenting tracepoint samples as a complete record of every call, when the buffer may have wrapped.
- Collecting large memory regions at a hot tracepoint fills the buffer almost immediately.

## Done when

- Samples are collected and exported with the sampling window stated.
- Buffer wrapping is recorded if it happened.

## References

- [GDB tracepoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Tracepoints.html)
