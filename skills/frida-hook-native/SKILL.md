---
name: frida-hook-native
description: "Install onEnter and onLeave hooks on an exported native function and capture arguments, return value and caller, then restore the original. Use when you need argument and return visibility without stopping the process"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [frida, interceptor, native]
phase: intercept
---

# Replace a native function with Frida Interceptor

> Install onEnter and onLeave hooks on an exported native function and capture arguments, return value and caller, then restore the original

**Use when:** you need argument and return visibility without stopping the process

**Avoid when:** the function is called on a hot path where per-call JavaScript would change behaviour

## Procedure

1. Resolve the export with Module.findExportByName and assert it is not null before attaching.
2. Attach with onEnter and onLeave, reading arguments with the declared signature rather than guessing types.
3. Read the return value in onLeave with retval and record the caller from this.returnAddress.
4. Call listener.detach() at the end of the window and confirm no hooks remain.

## Signals

- export-resolved
- onenter-fired
- detached-clean

## Patterns

**1. native hook**

```
const p = Module.findExportByName('libparse.so', 'parse_header');
Interceptor.attach(p, {
  onEnter(args) { send({ev: 'enter', len: args[1].toInt32()}); },
  onLeave(ret) { send({ev: 'leave', ret: ret.toInt32()}); }
});
```

## Pitfalls

- Reading a pointer argument as a string without bounding the read can crash on unterminated buffers.
- Hooking an export that is also called by the hook's own logging path creates recursion.

## Done when

- Enter and leave events are captured with typed arguments.
- The listener is detached and the target is unmodified afterwards.

## References

- [Frida Interceptor](https://frida.re/docs/javascript-api/#interceptor)
