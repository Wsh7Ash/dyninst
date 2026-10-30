---
name: plan-probe-map
description: "Resolve every planned probe against the target's symbol tables so the attachment window is spent observing rather than debugging names. Use when the probe list is written but its symbols have not been checked against the actual binary"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [plan, symbols, recon]
phase: plan
---

# Map probe points to real symbols before attaching

> Resolve every planned probe against the target's symbol tables so the attachment window is spent observing rather than debugging names

**Use when:** the probe list is written but its symbols have not been checked against the actual binary

**Avoid when:** the target is fully stripped and you have already accepted address-based probes instead of symbols

## Procedure

1. Dump dynamic symbols with nm -D or readelf --dyn-syms and store the output as evidence.
2. Match each planned probe against an exported or debug symbol and record its address and module.
3. For probes that only exist in debug info, confirm the debug file or build-id link is reachable.
4. Rewrite the plan with resolved addresses, and drop probes that cannot be resolved instead of hoping.

## Signals

- symbols-dumped
- probes-resolved
- unresolved-dropped

## Patterns

**1. symbol resolution**

```
readelf --dyn-syms -W ./libparse.so | grep -E 'FUNC.*(parse_header|parse_body)'
```

## Pitfalls

- Resolving against the build host's library instead of the one actually loaded in the target.
- Trusting a stale symbol dump after the binary was rebuilt; rebuild invalidates every address.

## Done when

- Every surviving probe maps to a symbol or address in the target.
- Dropped probes and their reasons are recorded.

## References

- [readelf manual](https://man7.org/linux/man-pages/man1/readelf.1.html)
- [Frida Module API](https://frida.re/docs/javascript-api/#module)
