---
name: ldpreload-constructor
description: "Use an attribute constructor to install hooks, read configuration and open a log before the target's own initialisation runs. Use when the behaviour you need to observe happens in constructors or before main"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [ldpreload, constructor, startup]
phase: intercept
---

# Run setup code before main with a constructor

> Use an attribute constructor to install hooks, read configuration and open a log before the target's own initialisation runs

**Use when:** the behaviour you need to observe happens in constructors or before main

**Avoid when:** the process's own constructors must run first because your setup depends on their state

## Procedure

1. Mark the setup function with __attribute__((constructor)) and keep it free of allocations that may not be ready yet.
2. Open the log with a raw open and write descriptor rather than stdio, which may not be initialised.
3. Record the process start time and the preload library path from the constructor.
4. Flush and close in a destructor marked __attribute__((destructor)).

## Signals

- constructor-ran
- log-opened-early
- destructor-flushed

## Patterns

**1. constructor**

```
__attribute__((constructor)) static void setup(void) {
  log_fd = open("/tmp/hook.log", O_WRONLY | O_CREAT | O_APPEND, 0600);
}
```

## Pitfalls

- Calling malloc or stdio in a constructor can deadlock before the allocator or stdio is initialised.
- Constructor order across libraries is not guaranteed, so do not depend on another preload library's setup.

## Done when

- The constructor runs and the log is opened before main.
- A destructor flushes and closes the log.

## References

- [GCC function attributes](https://gcc.gnu.org/onlinedocs/gcc/Function-Attributes.html)
