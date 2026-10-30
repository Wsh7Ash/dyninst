---
name: probe-function-entry
description: "Record arguments at entry with their declared types so a later claim about what reached the function is backed by observed values. Use when you need to prove which input reached a function rather than inferring it from output"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [trace, entry, arguments]
phase: trace
---

# Observe function entry with typed arguments

> Record arguments at entry with their declared types so a later claim about what reached the function is backed by observed values

**Use when:** you need to prove which input reached a function rather than inferring it from output

**Avoid when:** the function is called so often that per-call capture changes the timing you are measuring

## Procedure

1. Resolve the symbol and select the calling convention so argument registers are read correctly.
2. Decode each argument with its declared type: integer width, pointer plus bounds, or struct layout.
3. Bound every pointer read and record the actual length read alongside the value.
4. Emit one record per entry with a monotonically increasing sequence number.

## Signals

- entry-observed
- args-typed
- sequence-contiguous

## Patterns

**1. entry record**

```
Interceptor.attach(addr, {
  onEnter(args) {
    const len = args[1].toInt32();
    send({seq: ++n, len: len, buf: len > 0 && len < 4096 ? args[0].readUtf8(len) : null});
  }
});
```

## Pitfalls

- Reading a pointer as a C string when the callee takes a length can run past the buffer and crash.
- Capturing only the first call hides the interesting call in a batch; keep a sequence counter.

## Done when

- Entries are recorded with typed arguments and bounded reads.
- The sequence numbering shows no gaps in the captured window.

## References

- [Frida NativePointer](https://frida.re/docs/javascript-api/#nativepointer)
