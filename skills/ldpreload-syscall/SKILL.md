---
name: ldpreload-syscall
description: "Hook the libc wrapper so both direct calls and library callers are covered, and know exactly which paths the hook cannot see. Use when you need to observe file, network or process syscalls from a dynamically linked target"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [ldpreload, syscall, coverage]
phase: intercept
---

# Intercept a syscall wrapper rather than raw system calls

> Hook the libc wrapper so both direct calls and library callers are covered, and know exactly which paths the hook cannot see

**Use when:** you need to observe file, network or process syscalls from a dynamically linked target

**Avoid when:** the target issues raw syscalls with inline assembly, which bypasses libc entirely

## Procedure

1. Identify the libc wrapper for the syscall, for example open, openat, connect or execve.
2. Interpose the wrapper and forward with dlsym RTLD_NEXT, recording arguments and the returned errno.
3. Note that Go binaries and some hardened runtimes issue raw syscalls that never reach the wrapper.
4. Cross-check coverage against strace for the same run and explain any syscall the hook missed.

## Signals

- wrapper-hooked
- calls-recorded
- coverage-compared

## Patterns

**1. interpose openat**

```
int openat(int dirfd, const char *path, int flags, ...) {
  va_list ap; va_start(ap, flags);
  mode_t mode = va_arg(ap, mode_t); va_end(ap);
  syslog_call(path, flags);
  return real_openat(dirfd, path, flags, mode);
}
```

## Pitfalls

- Reading a variadic argument unconditionally passes garbage when the flag does not include O_CREAT.
- Reporting full syscall coverage when the target uses raw syscalls is a false claim; verify against strace.

## Done when

- The wrapper hook is installed and forwards correctly for both variadic and fixed calls.
- Coverage is compared against an independent tracer.

## References

- [openat(2)](https://man7.org/linux/man-pages/man2/openat.2.html)
- [strace](https://strace.io/)
