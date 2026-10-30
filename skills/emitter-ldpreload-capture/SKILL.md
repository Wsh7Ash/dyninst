---
name: emitter-ldpreload-capture
description: "Emit C source for an interposer that logs the planned calls and forwards to the real symbols, with a build command that is part of the output. Use when the capture must run without an external debugger attached"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [capture, emitter, ldpreload]
phase: capture
---

# Generate an LD_PRELOAD capture library from the plan

> Emit C source for an interposer that logs the planned calls and forwards to the real symbols, with a build command that is part of the output

**Use when:** the capture must run without an external debugger attached

**Avoid when:** the target is statically linked or setuid, where preloading has no effect

## Procedure

1. Emit one wrapper per planned function with the correct declared signature.
2. Emit dlsym RTLD_NEXT resolution guarded by a static pointer and a recursion flag.
3. Emit the gcc command line that builds the library with -shared -fPIC and the required libraries.
4. Compile the emitted source as part of the build step, so a non-compiling emitter fails loudly.

## Signals

- source-emitted
- compile-succeeds
- forwards-correctly

## Patterns

**1. emitter build**

```
dyninst emit ldpreload --plan plan.yml --out capture.c
gcc -shared -fPIC -o capture.so capture.c -ldl
```

## Pitfalls

- Emitting a wrapper with the wrong signature silently breaks the calling convention for that function.
- Shipping an emitter that was never compiled; compile the output in the build step instead of trusting the template.

## Done when

- The emitted C compiles without warnings that affect behaviour.
- The resulting library forwards calls and logs them.

## References

- [dlsym(3)](https://man7.org/linux/man-pages/man3/dlsym.3.html)
