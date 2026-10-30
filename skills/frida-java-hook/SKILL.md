---
name: frida-java-hook
description: "Attach to a Java method through the runtime's reflection layer and capture arguments and return values without patching the APK. Use when the app is Java or Kotlin running on ART and you have a debuggable or rooted target"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [frida, java, android]
phase: intercept
---

# Hook a Java method with Frida on Android

> Attach to a Java method through the runtime's reflection layer and capture arguments and return values without patching the APK

**Use when:** the app is Java or Kotlin running on ART and you have a debuggable or rooted target

**Avoid when:** the method is inlined or the app uses a hardened runtime that blocks Frida

## Procedure

1. Wrap the hook in Java.perform so it runs after the VM is ready.
2. Use Java.use on the class name and override the method with an implementation that calls this.method.overload(...).call(this, args).
3. Log arguments and return value, then return the original result unchanged unless mutation is the goal.
4. Keep a reference to the implementation so it can be reverted, and confirm the class was not loaded twice.

## Signals

- java-perform-ran
- method-wrapped
- result-returned

## Patterns

**1. java hook**

```
Java.perform(function () {
  const C = Java.use('com.example.Api');
  C.login.implementation = function (u, p) {
    send({u: u, plen: p.length});
    return this.login(u, p);
  };
});
```

## Pitfalls

- Overloading resolution fails when the signature is ambiguous; use .overload with explicit types.
- Hooking before the class is loaded throws; retry after the class loader has run.

## Done when

- The method wrapper fires on a real call with typed arguments.
- The original behaviour is preserved unless mutation was intended.

## References

- [Frida Java API](https://frida.re/docs/javascript-api/#java)
