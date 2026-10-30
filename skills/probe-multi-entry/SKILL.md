---
name: probe-multi-entry
description: "Hook a set of related functions and merge their events into a single sequence so ordering between them is visible instead of guessed. Use when a bug depends on the order in which several functions run, not on any single one"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [trace, timeline, ordering]
phase: trace
---

# Trace several functions as one ordered timeline

> Hook a set of related functions and merge their events into a single sequence so ordering between them is visible instead of guessed

**Use when:** a bug depends on the order in which several functions run, not on any single one

**Avoid when:** the functions run on multiple threads and a total order would be fabricated rather than measured

## Procedure

1. Declare the probe set with a stable name per function and one shared sequence counter.
2. Install every hook before resuming the process so the first call is not missed.
3. Record thread id with each event so cross-thread ordering is not invented.
4. Sort by sequence within a thread and by timestamp across threads, and state which ordering the report uses.

## Signals

- probe-set-installed
- events-merged
- threads-separated

## Patterns

**1. multi-probe**

```
const probes = {parse_header: a1, parse_body: a2, dispatch: a3};
for (const [name, addr] of Object.entries(probes)) {
  Interceptor.attach(addr, { onEnter() { send({seq: ++n, fn: name, tid: tid()}); } });
}
```

## Pitfalls

- Interleaving events from several threads into one list and presenting it as a causal order.
- Installing probes one at a time after the process runs, so the earliest calls never appear.

## Done when

- Every probe in the set is installed before execution.
- Events carry a thread id and the ordering rule is stated.

## References

- [Frida ThreadId](https://frida.re/docs/javascript-api/#process-getcurrentthreadid)
