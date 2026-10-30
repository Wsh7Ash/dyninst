---
name: plan-baseline-capture
description: "Record an uninstrumented run of the same input so every later observation has a control to compare against. Use when you intend to claim that instrumented behaviour differs from normal behaviour"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [plan, baseline, control]
phase: plan
---

# Capture a clean baseline before instrumenting

> Record an uninstrumented run of the same input so every later observation has a control to compare against

**Use when:** you intend to claim that instrumented behaviour differs from normal behaviour

**Avoid when:** the target cannot be run twice, for example a one-shot crash on a live production host

## Procedure

1. Run the target with the exact input you will use under instrumentation, with no probes attached.
2. Record exit code, wall time, stdout and stderr, plus any file or network side effects.
3. Hash the inputs and outputs so the baseline is reproducible rather than remembered.
4. Store the baseline next to the plan and reference it from every later finding.

## Signals

- baseline-run-complete
- baseline-hashed
- control-linked

## Patterns

**1. baseline capture**

```
python -m dyninst plan baseline --target ./server --input case01.bin --out baseline/
```

## Pitfalls

- A baseline captured with different input proves nothing when compared to the instrumented run.
- Instrumentation that changes timing can make a benign race look like a new bug; the baseline must record timing.

## Done when

- A baseline exists for the exact input under test and is hashed.
- Later captures cite the baseline identifier.

## References

- [Frida instrumentation overview](https://frida.re/docs/home/)
