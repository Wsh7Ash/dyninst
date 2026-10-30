---
name: teardown-force-detach
description: "Detach from a process whose script has hung or whose hook recursed, using the least destructive step that restores normal execution. Use when the target is unresponsive because instrumentation is stuck"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [teardown, recovery, hung]
phase: teardown
---

# Recover a wedged session without killing the target

> Detach from a process whose script has hung or whose hook recursed, using the least destructive step that restores normal execution

**Use when:** the target is unresponsive because instrumentation is stuck

**Avoid when:** the process is already dead, where recovery is pointless

## Procedure

1. Check whether the target is stopped in the debugger or spinning in a hook before choosing a recovery step.
2. For a GDB stop, issue detach which resumes the process; for a Frida hang, kill only the agent session.
3. If the hook recursed, unload the script rather than detaching the whole session so other probes survive.
4. Confirm recovery by observing a normal request complete, then record what was recovered and what was lost.

## Signals

- state-diagnosed
- least-destructive-recovery
- recovery-confirmed

## Patterns

**1. recover gdb stop**

```
gdb -p 4711 -batch -ex 'detach'
# or from an existing session: detach
```

## Pitfalls

- Killing the process to recover from a hung hook destroys the bug site and any unsaved evidence.
- Detaching without diagnosing leaves the root cause in place for the next run.

## Done when

- The target is running normally again and the recovery step is recorded.
- Evidence lost by the recovery is stated explicitly.

## References

- [GDB detach](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Attach.html)
