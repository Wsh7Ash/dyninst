---
name: probe-function-return
description: "Capture the return value and the error branch so a claim about failure handling is backed by the value the function actually returned. Use when success and failure are distinguished by a return code or an out-parameter"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [trace, return, errors]
phase: trace
---

# Observe function return and error paths

> Capture the return value and the error branch so a claim about failure handling is backed by the value the function actually returned

**Use when:** success and failure are distinguished by a return code or an out-parameter

**Avoid when:** the function returns through multiple epilogues that the hook does not cover

## Procedure

1. Hook onLeave and read retval with the declared return type rather than as a raw integer.
2. For out-parameter style APIs, read the output struct in onLeave after the callee has filled it.
3. Record errno or the last-error value immediately on leave, before any other call can clobber it.
4. Pair the record with its entry sequence number so return values are matched to the right call.

## Signals

- return-observed
- errno-captured
- call-paired

## Patterns

**1. return record**

```
Interceptor.attach(addr, {
  onEnter() { this.seq = ++n; },
  onLeave(ret) { send({seq: this.seq, ret: ret.toInt32(), err: errnoValue()}); }
});
```

## Pitfalls

- Reading errno after another libc call in the hook has already overwritten it.
- A function with an early return and a normal return can look identical if only the value is captured, not the epilogue address.

## Done when

- Return values and error codes are captured per call.
- Each return record pairs with exactly one entry record.

## References

- [Frida onLeave](https://frida.re/docs/javascript-api/#interceptor-attach)
