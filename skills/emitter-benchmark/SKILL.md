---
name: emitter-benchmark
description: "Time the instrumented run against the baseline so overhead is a number you report rather than an assumption you make. Use when the finding depends on timing or throughput and instrumentation could distort it"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [benchmark, overhead, timing]
phase: benchmark
---

# Measure the cost of an emitter before trusting its captures

> Time the instrumented run against the baseline so overhead is a number you report rather than an assumption you make

**Use when:** the finding depends on timing or throughput and instrumentation could distort it

**Avoid when:** the capture is purely structural and timing is irrelevant to the claim

## Procedure

1. Run the baseline and the instrumented run at least five times each with the same input.
2. Record wall time, CPU time and event count for every run, then report median and spread.
3. Compute the overhead ratio and state whether the claim survives that distortion.
4. Keep the raw timings, not only the summary, so the measurement can be re-checked.

## Signals

- runs-repeated
- timings-recorded
- overhead-reported

## Patterns

**1. timing loop**

```
for i in 1 2 3 4 5; do /usr/bin/time -f '%e %U %S' ./target --input case01.bin; done
```

## Pitfalls

- Comparing a single instrumented run to a single baseline run and calling the difference overhead.
- Reporting a speedup or slowdown without the spread, which hides that the runs overlapped.

## Done when

- At least five runs per condition are recorded with median and spread.
- The overhead ratio is stated with the effect on the claim.

## References

- [time(1)](https://man7.org/linux/man-pages/man1/time.1.html)
