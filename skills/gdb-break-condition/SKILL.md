---
name: gdb-break-condition
description: "Attach a condition to a breakpoint so a high-frequency function stops on the triggering argument instead of thousands of benign calls. Use when the target function is called constantly and only one call shape matters"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [gdb, conditional, filter]
phase: debug
---

# Break only on the call you care about

> Attach a condition to a breakpoint so a high-frequency function stops on the triggering argument instead of thousands of benign calls

**Use when:** the target function is called constantly and only one call shape matters

**Avoid when:** the distinguishing value is not available in a form GDB can evaluate at the breakpoint

## Procedure

1. Set the breakpoint normally and let it hit once to learn the argument layout.
2. Add a condition that matches the triggering shape, for example length > 512 or a magic header value.
3. Confirm the condition evaluates without errors by printing it at a stop.
4. Record the condition text with the capture so the filter is reproducible.

## Signals

- condition-set
- condition-evaluates
- targeted-stop

## Patterns

**1. conditional break**

```
break parse_header if len > 512
condition 1 strcmp(header, "MAGIC") == 0
```

## Pitfalls

- A condition that calls a function can change program state or crash inside GDB.
- Conditions evaluate slowly; a condition on a hot function can still stall the target.

## Done when

- The breakpoint stops only on the intended call shape.
- The condition text is recorded with the capture.

## References

- [GDB conditions](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Conditions.html)
