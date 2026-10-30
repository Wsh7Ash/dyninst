---
name: plan-generate
description: "Declare the target, attachment method, probe points, emitter backend and cleanup step in one artifact that the rest of the run is checked against. Use when you are about to instrument a process and no written plan exists yet"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [plan, design, scope]
phase: plan
---

# Write an instrumentation plan before touching the target

> Declare the target, attachment method, probe points, emitter backend and cleanup step in one artifact that the rest of the run is checked against

**Use when:** you are about to instrument a process and no written plan exists yet

**Avoid when:** the engagement is a throwaway smoke test on a process you own and a plan would be pure overhead

## Procedure

1. Name the target precisely: binary path, build id, PID or core file, and the host it runs on.
2. Pick the attachment method that the target actually permits: Frida attach, GDB attach, LD_PRELOAD at launch, or an eBPF probe.
3. List every probe point as a symbol plus an offset or line, not as a vague area of interest.
4. Name the emitter that will produce the capture script and the retention rule for what it records.
5. Write the teardown step, then sign and store the plan next to the evidence it will justify.

## Signals

- plan-committed
- attachment-selected
- probe-list-closed

## Patterns

**1. plan skeleton**

```
target: /opt/app/bin/server (build-id abc123)
attachment: frida -p <pid>
probes:
  - parse_header@libparse.so
  - recv@libc.so.6
emitter: frida-script
teardown: session.detach() + signal handler restored
```

## Pitfalls

- A plan written after the capture is a justification, not a plan; write it first and date it.
- Probe names that do not resolve against the loaded module waste the whole attachment window.

## Done when

- The plan names a target, a method, every probe and a teardown.
- The plan is stored with the capture it produced.

## References

- [Frida JavaScript API](https://frida.re/docs/javascript-api/)
- [GDB documentation](https://sourceware.org/gdb/documentation/)
