---
name: frida-stalker-trace
description: "Follow a thread's real instruction stream to see which basic blocks executed, without setting a breakpoint on every one. Use when you need coverage of an unknown code path rather than a check at known symbols"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [frida, stalker, coverage]
phase: trace
---

# Trace executed code with Frida Stalker

> Follow a thread's real instruction stream to see which basic blocks executed, without setting a breakpoint on every one

**Use when:** you need coverage of an unknown code path rather than a check at known symbols

**Avoid when:** the target is timing sensitive, because Stalker slows execution by an order of magnitude

## Procedure

1. Follow the thread of interest with Stalker.follow and a transform that records block entry addresses.
2. Keep the transform minimal: append a call to a logging stub rather than inlining heavy JavaScript.
3. Store block addresses in a set and resolve them to symbols after the run, not inside the transform.
4. Unfollow the thread and stop the Stalker session before doing any analysis.

## Signals

- stalker-following
- blocks-recorded
- unfollowed

## Patterns

**1. stalker follow**

```
const blocks = new Set();
Stalker.follow(tid, {
  transform(iterator) {
    let ins;
    while ((ins = iterator.next()) !== null) {
      if (ins.address in seen) continue;
      blocks.add(ins.address);
    }
  }
});
```

## Pitfalls

- Doing heavy work inside the transform turns a slow trace into a hung process.
- Following every thread at once produces an unusable interleaving; follow one and say which.

## Done when

- Executed blocks are recorded for one named thread.
- Stalker is unfollowed and the process returns to normal speed.

## References

- [Frida Stalker](https://frida.re/docs/javascript-api/#stalker)
