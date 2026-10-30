---
name: gdb-stepi
description: "Advance one machine instruction at a time around a suspicious branch so the observed path is the path you report, not an approximation. Use when source stepping jumps over the interesting branch or the code has no debug info"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [gdb, stepi, branch]
phase: debug
---

# Single-step instructions to follow a branch precisely

> Advance one machine instruction at a time around a suspicious branch so the observed path is the path you report, not an approximation

**Use when:** source stepping jumps over the interesting branch or the code has no debug info

**Avoid when:** the region is thousands of instructions long or inside a tight loop with no exit condition

## Procedure

1. Stop at the branch instruction and record its address, mnemonic and current flags.
2. Step one instruction at a time with stepi, logging the program counter and flags after each step.
3. Stop at the first deviation from the expected path and capture the registers that decided it.
4. Write down the branch decision as address, condition and observed flag values.

## Signals

- branch-address-recorded
- single-step-trace
- divergence-captured

## Patterns

**1. step loop**

```
gdb -q ./target -batch -ex 'break *0x4011a0' -ex 'run' -ex 'x/3i $pc' -ex 'stepi' -ex 'info registers eflags'
```

## Pitfalls

- Stepping into a syscall instruction can move you into the kernel and lose the user-space context.
- A branch whose flags were set far earlier will not show the cause at the branch itself; capture backwards too.

## Done when

- The branch address, condition and observed flags are recorded.
- The divergence point is tied to a register value.

## References

- [GDB stepping](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Continuing-and-Stepping.html)
