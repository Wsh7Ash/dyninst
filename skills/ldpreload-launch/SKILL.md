---
name: ldpreload-launch
description: "Start the process yourself with a preload library so interception is in place before the first call, and prove the library actually loaded. Use when you control how the target is launched and need interception without an external debugger"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [ldpreload, launch, interposition]
phase: attach
---

# Launch a target with an LD_PRELOAD interposer

> Start the process yourself with a preload library so interception is in place before the first call, and prove the library actually loaded

**Use when:** you control how the target is launched and need interception without an external debugger

**Avoid when:** the target is statically linked, setuid, or already running

## Procedure

1. Build the interposer as a shared object with -shared -fPIC and record its hash.
2. Launch with LD_PRELOAD=./hook.so ./target and pass the real arguments through.
3. Prove the library loaded by logging from a constructor or by reading /proc/PID/maps for the .so path.
4. Record the environment the process actually saw, including the full LD_PRELOAD value.

## Signals

- interposer-built
- library-observed-in-maps
- constructor-ran

## Patterns

**1. preload launch**

```
gcc -shared -fPIC -o hook.so hook.c -ldl
LD_PRELOAD=./hook.so ./target --input case01.bin
```

## Pitfalls

- setuid binaries ignore LD_PRELOAD, so a successful launch proves nothing about interception.
- A relative LD_PRELOAD path breaks after the process changes directory; use an absolute path.

## Done when

- The library appears in the process maps and its constructor ran.
- The exact LD_PRELOAD value is recorded with the capture.

## References

- [ld.so preload](https://man7.org/linux/man-pages/man8/ld.so.8.html)
- [dlsym RTLD_NEXT](https://man7.org/linux/man-pages/man3/dlsym.3.html)
