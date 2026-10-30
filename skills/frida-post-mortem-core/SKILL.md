---
name: frida-post-mortem-core
description: "Dump module ranges and thread state from a live Frida session so a later crash can be tied to the exact loaded layout it ran under. Use when the process is crashing and you want a layout snapshot before it disappears"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [post-mortem, frida, snapshot]
phase: post-mortem
---

# Capture a Frida snapshot before the process is torn down

> Dump module ranges and thread state from a live Frida session so a later crash can be tied to the exact loaded layout it ran under

**Use when:** the process is crashing and you want a layout snapshot before it disappears

**Avoid when:** the process is already gone, in which case only a core file helps

## Procedure

1. From the attached session, enumerate modules with their base address, size and path.
2. Snapshot thread ids and their current instruction pointers.
3. Write the snapshot to a file outside the target's memory so it survives the crash.
4. After the crash, compare the snapshot's module base addresses against the core or the new process.

## Signals

- modules-snapshotted
- threads-snapshotted
- snapshot-persisted

## Patterns

**1. module snapshot**

```
const mods = Process.enumerateModules().map(m => ({n: m.name, b: m.base, s: m.size, p: m.path}));
send({snapshot: mods, tids: Process.enumerateThreads().map(t => t.id)});
```

## Pitfalls

- Storing the snapshot only in the target's memory means the crash destroys the evidence.
- A snapshot taken after a module was unloaded looks complete but describes the wrong layout.

## Done when

- A module and thread snapshot is persisted outside the target.
- The snapshot is compared against the post-crash layout.

## References

- [Frida Process.enumerateModules](https://frida.re/docs/javascript-api/#process-enumeratemodules)
