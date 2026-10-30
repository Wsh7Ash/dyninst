---
name: overhead-control-run
description: "Instrument with hooks that capture nothing so the cost of attachment itself is separated from the cost of the observations. Use when overhead is high and you need to know whether the hook or the logging dominates"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [benchmark, control, overhead]
phase: benchmark
---

# Run a no-op control to separate hook cost from probe cost

> Instrument with hooks that capture nothing so the cost of attachment itself is separated from the cost of the observations

**Use when:** overhead is high and you need to know whether the hook or the logging dominates

**Avoid when:** the overhead is already negligible relative to the noise floor

## Procedure

1. Build a variant of the script that attaches the same probes but records nothing.
2. Run the no-op variant and the full-capture variant with the same input and repetition count.
3. Compare the two against the baseline to attribute cost to attachment versus logging.
4. Report all three timings so the attribution is visible rather than asserted.

## Signals

- noop-variant-built
- three-way-compared
- attribution-reported

## Patterns

**1. noop hook**

```
Interceptor.attach(p, { onEnter(args) { /* record nothing */ } });
```

## Pitfalls

- Skipping the no-op control and blaming logging for cost that attachment already imposes.
- Letting the compiler optimise away the no-op path in a way that makes it not comparable.

## Done when

- Three timings exist: baseline, no-op hook and full capture.
- The attribution between attachment and logging is stated with numbers.

## References

- [Frida performance notes](https://frida.re/docs/performance/)
