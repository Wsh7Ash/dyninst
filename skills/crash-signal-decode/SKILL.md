---
name: crash-signal-decode
description: "Turn SI_CODE, the faulting address and the signal number into a precise fault classification instead of calling everything a segfault. Use when you need to distinguish a null dereference from a wild pointer, a stack overflow or a deliberate abort"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [post-mortem, signal, classification]
phase: post-mortem
---

# Decode the crash signal and faulting address

> Turn SI_CODE, the faulting address and the signal number into a precise fault classification instead of calling everything a segfault

**Use when:** you need to distinguish a null dereference from a wild pointer, a stack overflow or a deliberate abort

**Avoid when:** the signal was delivered by another thread or by raise rather than by the faulting instruction

## Procedure

1. Read the signal number and si_code from the siginfo structure, which distinguishes SEGV_MAPERR from SEGV_ACCERR.
2. Record the faulting address from si_addr and compare it to the mapping that should have contained it.
3. Check whether the faulting instruction is a load, store or execute, since the classification depends on it.
4. Write the classification as a sentence with the evidence, for example a read of an unmapped address.

## Signals

- siginfo-read
- fault-classified
- mapping-compared

## Patterns

**1. siginfo decode**

```
gdb -q ./server core -batch -ex 'p $_siginfo' -ex 'p $_siginfo.si_code' -ex 'p $_siginfo._sifields._sigfault.si_addr'
```

## Pitfalls

- Calling every SIGSEGV a null dereference when si_addr is non-zero and points into an unmapped region.
- Ignoring SIGABRT, which is a deliberate abort and not a memory fault at all.

## Done when

- The signal, si_code and faulting address are recorded together.
- The classification names the access type and the mapping state.

## References

- [signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)
- [sigaction(2)](https://man7.org/linux/man-pages/man2/sigaction.2.html)
