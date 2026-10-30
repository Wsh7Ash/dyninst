---
name: cross-arch-normalize
description: "Convert register and calling-convention details into a common record shape so an x86-64 capture and an arm64 capture can be compared directly. Use when the same bug must be evidenced on more than one architecture"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [benchmark, portability, normalisation]
phase: benchmark
---

# Normalise captures across architectures

> Convert register and calling-convention details into a common record shape so an x86-64 capture and an arm64 capture can be compared directly

**Use when:** the same bug must be evidenced on more than one architecture

**Avoid when:** only one architecture is in scope, where normalisation adds indirection for nothing

## Procedure

1. Record the architecture and ABI with every capture, including pointer width and endianness.
2. Map argument registers to positional argument names before analysis rather than after.
3. Convert addresses to module-relative offsets so ASLR does not make two runs look different.
4. Keep the raw registers alongside the normalised record so the mapping can be audited.

## Signals

- arch-recorded
- args-positional
- offsets-relative

## Patterns

**1. normalise**

```
send({arch: Process.arch, ptr: Process.pointerSize, fn: 'parse_header', off: addr.sub(base), args: [a0, a1]});
```

## Pitfalls

- Comparing absolute addresses across runs where ASLR changed the base and calling the difference a bug.
- Assuming x86-64 argument order on arm64, where the registers and vararg rules differ.

## Done when

- Every record names its architecture and uses module-relative offsets.
- Raw register values are preserved beside the normalised form.

## References

- [Frida Process.arch](https://frida.re/docs/javascript-api/#process-arch)
