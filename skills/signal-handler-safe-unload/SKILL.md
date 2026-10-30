---
name: signal-handler-safe-unload
description: "Order the teardown so a fault signal cannot arrive while the hook is being removed, which would otherwise crash the process during cleanup. Use when the instrumentation installs a signal handler and also hooks code that can fault"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [teardown, signal, race]
phase: teardown
---

# Remove a hook without racing its own signal handler

> Order the teardown so a fault signal cannot arrive while the hook is being removed, which would otherwise crash the process during cleanup

**Use when:** the instrumentation installs a signal handler and also hooks code that can fault

**Avoid when:** no signal handler is involved and a plain detach is enough

## Procedure

1. Block the relevant signals on all threads before beginning removal, using pthread_sigmask.
2. Remove the hooks, then restore the original handler, then unblock the signals.
3. Check that no signal was delivered while blocked by reading the pending set before unblocking.
4. Record the ordering used, because the reverse order reintroduces the race.

## Signals

- signals-blocked
- teardown-ordered
- pending-checked

## Patterns

**1. block then teardown**

```
sigset_t s; sigemptyset(&s); sigaddset(&s, SIGSEGV);
pthread_sigmask(SIG_BLOCK, &s, NULL);
/* remove hooks, restore handler */
pthread_sigmask(SIG_UNBLOCK, &s, NULL);
```

## Pitfalls

- Restoring the handler before removing the hook, so a fault in the hook calls the default action.
- Blocking signals only on the calling thread while other threads keep faulting into the hook.

## Done when

- Signals are blocked on all threads across the removal window.
- The ordering is recorded and the pending set was empty at unblock.

## References

- [pthread_sigmask(3)](https://man7.org/linux/man-pages/man3/pthread_sigmask.3.html)
