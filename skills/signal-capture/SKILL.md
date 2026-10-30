---
name: signal-capture
description: "Install a handler that records the signal, address and backtrace before the default action terminates the process, then re-raises. Use when the crash is not producing a usable core and you need in-process evidence"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [signal, handler, in-process]
phase: signal
---

# Capture fault signals from inside the process

> Install a handler that records the signal, address and backtrace before the default action terminates the process, then re-raises

**Use when:** the crash is not producing a usable core and you need in-process evidence

**Avoid when:** the process already installs its own handler that you must not displace

## Procedure

1. Install a handler for SIGSEGV, SIGBUS and SIGABRT with SA_SIGINFO to receive siginfo and ucontext.
2. In the handler, write the signal, si_addr, and a short backtrace to a pre-opened descriptor using async-signal-safe calls only.
3. Restore the default disposition and re-raise the signal so the process still dies with the correct status.
4. Verify the handler ran by reading the log and confirming the exit status matches the signal.

## Signals

- handler-installed
- signal-recorded
- status-preserved

## Patterns

**1. sa_siginfo handler**

```
struct sigaction sa = {0};
sa.sa_sigaction = on_fault;
sa.sa_flags = SA_SIGINFO | SA_RESTART;
sigaction(SIGSEGV, &sa, NULL);
```

## Pitfalls

- Calling printf or malloc in a signal handler is undefined behaviour and can deadlock the crash path.
- Swallowing the signal instead of re-raising changes the exit status and hides the crash from tooling.

## Done when

- The handler records signal, address and a backtrace using safe calls only.
- The process still terminates with the original signal status.

## References

- [sigaction(2)](https://man7.org/linux/man-pages/man2/sigaction.2.html)
- [signal-safety(7)](https://man7.org/linux/man-pages/man7/signal-safety.7.html)
