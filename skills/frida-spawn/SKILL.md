---
name: frida-spawn
description: "Start the process suspended under Frida so hooks are installed before the first user instruction runs, catching early-init bugs that attach misses. Use when the bug you are chasing happens during startup, argument parsing or constructor execution"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [frida, spawn, startup]
phase: attach
---

# Spawn the target under Frida from the first instruction

> Start the process suspended under Frida so hooks are installed before the first user instruction runs, catching early-init bugs that attach misses

**Use when:** the bug you are chasing happens during startup, argument parsing or constructor execution

**Avoid when:** the target is already running with state you cannot recreate by respawning it

## Procedure

1. Launch with frida -f ./target --no-pause=false and a script that resumes the process only after hooks are installed.
2. Install every hook in the script body, then call Java.perform or resume the thread as appropriate.
3. Pass the real argv through the spawn call so startup parsing sees the intended input.
4. Record the spawned PID in the evidence bundle so the run can be tied to a process identity.

## Signals

- spawned-suspended
- hooks-installed-pre-entry
- process-resumed

## Patterns

**1. spawn with argv**

```
frida -f ./server -l startup.js --args --config ./conf.yml
// startup.js installs hooks, then calls Process.resume()
```

## Pitfalls

- Resuming before hooks are installed, which puts you back in the attach race you were trying to avoid.
- Forgetting that spawn gives the target a different environment than your shell, which changes startup paths.

## Done when

- Hooks are installed before the first user instruction is observed.
- The spawned PID and argv are recorded with the capture.

## References

- [Frida spawn mode](https://frida.re/docs/modes/#spawn)
- [Frida Process.resume](https://frida.re/docs/javascript-api/#process-resume)
