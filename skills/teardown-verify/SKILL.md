---
name: teardown-verify
description: "Confirm that every hook, breakpoint and preloaded library is removed and that the process behaves as it did before the session. Use when the session is ending and the target must keep running normally"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [teardown, verify, cleanup]
phase: teardown
---

# Verify the target is clean after instrumentation

> Confirm that every hook, breakpoint and preloaded library is removed and that the process behaves as it did before the session

**Use when:** the session is ending and the target must keep running normally

**Avoid when:** the process is being deliberately terminated as part of the test

## Procedure

1. Detach every listener and confirm the count of active hooks is zero.
2. Compare the module list against the pre-session snapshot to prove no injected library remains.
3. Re-run the baseline input and compare the result with the stored baseline.
4. Record the teardown evidence, including any difference that could not be removed.

## Signals

- hooks-zero
- modules-match-baseline
- behaviour-matches

## Patterns

**1. teardown check**

```
session.detach()
# then compare Process.enumerateModules() with the pre-session snapshot
```

## Pitfalls

- Assuming detach removed a hook that was installed by a preloaded library; preload survives until process exit.
- Declaring the target clean without re-running the baseline, which is the only behavioural proof.

## Done when

- Hook count is zero and the module list matches the pre-session snapshot.
- The baseline input produces the baseline result again.

## References

- [Frida Session.detach](https://frida.re/docs/javascript-api/#session-detach)
