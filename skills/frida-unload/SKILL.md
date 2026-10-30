---
name: frida-unload
description: "Detach listeners, unload the script and prove the process returns to its uninstrumented behaviour before the session closes. Use when the capture window has closed and the same process must keep running"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [teardown, frida, unload]
phase: teardown
---

# Unload a Frida script and leave no hooks behind

> Detach listeners, unload the script and prove the process returns to its uninstrumented behaviour before the session closes

**Use when:** the capture window has closed and the same process must keep running

**Avoid when:** the process is being killed at the end of the test anyway

## Procedure

1. Call detach on every Interceptor listener created by the script and keep the returned handles.
2. Unload the script with session.detach or script.unload and check for an exception.
3. Re-resolve a probe address to confirm the function now points at its original prologue.
4. Record the unload and the verification in the session log.

## Signals

- listeners-detached
- script-unloaded
- prologue-restored

## Patterns

**1. detach listener**

```
const listener = Interceptor.attach(p, callbacks);
// at the end
listener.detach();
```

## Pitfalls

- Unloading the script without detaching listeners leaves trampolines in the target's code.
- Assuming detach restored the prologue without checking the first bytes at the address.

## Done when

- Every listener is detached and the script is unloaded.
- The probe address shows the original code again.

## References

- [Frida Interceptor detach](https://frida.re/docs/javascript-api/#interceptor)
