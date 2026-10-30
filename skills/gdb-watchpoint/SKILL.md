---
name: gdb-watchpoint
description: "Trap the exact instruction that mutates a field or buffer so you can attribute an unexpected value to the writer instead of guessing. Use when a value changes unexpectedly and you need the writing instruction, not just the bad value"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [gdb, watchpoint, memory]
phase: debug
---

# Catch a write to memory with a GDB watchpoint

> Trap the exact instruction that mutates a field or buffer so you can attribute an unexpected value to the writer instead of guessing

**Use when:** a value changes unexpectedly and you need the writing instruction, not just the bad value

**Avoid when:** the watched region is written on every iteration, which makes the watchpoint unusable

## Procedure

1. Resolve the address of the field or buffer with print &obj.field, and note the byte width.
2. Set a watchpoint on that address with watch *(int*)0xADDR sized to the field.
3. Continue and capture the stack at the stop, which is the writer you were looking for.
4. Remove the watchpoint and record the writer's frame, function and source line.

## Signals

- watchpoint-armed
- write-caught
- writer-frame-captured

## Patterns

**1. hardware watchpoint**

```
watch *(unsigned int*)0x7fffffffe2a0
continue
bt
```

## Pitfalls

- Watching a stack address across a function return, after which the address refers to unrelated data.
- Software watchpoints are extremely slow; prefer hardware watchpoints where they are available.

## Done when

- The writing instruction is identified with a stack and source line.
- The watchpoint is removed before the run continues.

## References

- [GDB watchpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Set-Watchpoints.html)
