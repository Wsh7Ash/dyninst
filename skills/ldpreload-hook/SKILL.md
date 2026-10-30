---
name: ldpreload-hook
description: "Override a library call, forward to the real implementation with dlsym RTLD_NEXT, and log or mutate arguments without breaking the process. Use when you need to observe or alter a library call and you control process launch"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [ldpreload, hook, libc]
phase: intercept
---

# Interpose a libc function with an LD_PRELOAD hook

> Override a library call, forward to the real implementation with dlsym RTLD_NEXT, and log or mutate arguments without breaking the process

**Use when:** you need to observe or alter a library call and you control process launch

**Avoid when:** the call is resolved internally by the binary, for example a statically linked helper

## Procedure

1. Declare a function with the same signature as the target symbol and resolve the original with dlsym(RTLD_NEXT, name).
2. Log the arguments before forwarding, using a write-safe path that cannot recurse into the hook.
3. Forward to the original, then log the return value and errno.
4. Guard re-entrancy with a thread-local flag so a log call cannot call the hooked function again.

## Signals

- original-resolved
- args-logged
- return-logged

## Patterns

**1. interpose write**

```
static ssize_t (*real_write)(int, const void *, size_t);
ssize_t write(int fd, const void *buf, size_t n) {
  if (!real_write) real_write = dlsym(RTLD_NEXT, "write");
  log_call(fd, n);
  return real_write(fd, buf, n);
}
```

## Pitfalls

- Logging with printf inside a hook for write causes infinite recursion; use write directly with a recursion guard.
- Symbol versioning can make dlsym return the wrong implementation for versioned symbols.

## Done when

- The original is resolved and every call is forwarded.
- The process completes without recursion or crashes.

## References

- [dlsym RTLD_NEXT](https://man7.org/linux/man-pages/man3/dlsym.3.html)
- [LD_PRELOAD hooks](https://man7.org/linux/man-pages/man8/ld.so.8.html)
