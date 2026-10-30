---
name: gdb-attach
description: "Take control of a live process with GDB, confirm the stop is the thread you expect and capture registers before changing any state. Use when you need register-level inspection or a precise stop inside a running service"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [gdb, attach, ptrace]
phase: attach
---

# Attach GDB to a running process and stop it safely

> Take control of a live process with GDB, confirm the stop is the thread you expect and capture registers before changing any state

**Use when:** you need register-level inspection or a precise stop inside a running service

**Avoid when:** the process must not be paused, for example a latency-sensitive production endpoint

## Procedure

1. Attach with gdb -p PID and confirm GDB reports the stop and the loaded shared libraries.
2. Run info threads and confirm which thread stopped; select the thread that serves the request under test.
3. Capture info registers, bt and the current instruction pointer before setting any breakpoint.
4. Detach with detach rather than quit so the process continues instead of being killed.

## Signals

- attached-and-stopped
- thread-identified
- registers-captured

## Patterns

**1. attach and inspect**

```
gdb -p 4711 -batch -ex 'info threads' -ex 'info registers' -ex 'bt' -ex 'detach'
```

## Pitfalls

- Quitting GDB instead of detaching kills the instrumented process and destroys the bug site.
- Inpecting a worker thread that never handles the request you are testing.

## Done when

- A thread is identified and its registers and backtrace are captured.
- The process is detached and still running afterwards.

## References

- [GDB attach to a process](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Attach.html)
