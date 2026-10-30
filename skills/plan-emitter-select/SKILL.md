---
name: plan-emitter-select
description: "Decide between a Frida script, a GDB macro file and an LD_PRELOAD library by checking what the target allows before writing any of them. Use when several instrumentation backends are available and the wrong choice wastes the engagement window"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [plan, emitter, constraints]
phase: plan
---

# Choose the emitter that fits the target constraints

> Decide between a Frida script, a GDB macro file and an LD_PRELOAD library by checking what the target allows before writing any of them

**Use when:** several instrumentation backends are available and the wrong choice wastes the engagement window

**Avoid when:** the engagement mandates one backend, in which case the choice is already made for you

## Procedure

1. Check whether the target ships a Frida agent or permits ptrace; a hardened container may forbid both.
2. Check whether the binary is static, stripped, or built without frame pointers, which changes what GDB can show.
3. Check whether the process can be launched by you, which is the precondition for LD_PRELOAD.
4. Record the rejected options and the reason, so a later reviewer can see the decision was constrained, not arbitrary.

## Signals

- constraints-recorded
- emitter-chosen
- rejections-documented

## Patterns

**1. constraint check**

```
cat /proc/sys/kernel/yama/ptrace_scope
file ./target | grep -E 'static|not stripped'
ldd ./target
```

## Pitfalls

- Assuming ptrace works because it works on your workstation; check the actual host.
- Picking LD_PRELOAD for a statically linked binary, where it silently does nothing.

## Done when

- One emitter is chosen with a recorded reason.
- Every rejected emitter has a recorded reason.

## References

- [Frida gadget and injection modes](https://frida.re/docs/modes/)
- [ld.so preload semantics](https://man7.org/linux/man-pages/man8/ld.so.8.html)
