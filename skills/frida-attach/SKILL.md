---
name: frida-attach
description: "Connect to a live PID, confirm the session, load a script and prove the probe resolves before recording anything. Use when the process is already running and you have permission and ptrace rights to instrument it"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [frida, attach, live]
phase: attach
---

# Attach Frida to an already running process

> Connect to a live PID, confirm the session, load a script and prove the probe resolves before recording anything

**Use when:** the process is already running and you have permission and ptrace rights to instrument it

**Avoid when:** the process is protected by anti-debug or the host forbids ptrace for your user

## Procedure

1. Confirm the PID is the process you mean to instrument, not a parent supervisor or a worker pool sibling.
2. Attach with frida -p PID -l script.js and read the console for a session confirmation line.
3. Resolve each probe with Module.findExportByName and log its address before installing any hook.
4. Keep the session attached for the declared window, then detach explicitly and record the detach time.

## Signals

- session-established
- probe-resolved
- session-detached

## Patterns

**1. attach and resolve**

```
frida -p 4711 -l probes.js
// probes.js
const addr = Module.findExportByName('libparse.so', 'parse_header');
console.log('parse_header @', addr);
```

## Pitfalls

- Attaching to a worker sibling instead of the process that handles the request under test.
- Leaving the session attached after the capture, which perturbs later measurements.

## Done when

- The session is confirmed and every probe resolves to a non-null address.
- The detach is explicit and timestamped.

## References

- [Frida attach mode](https://frida.re/docs/modes/#attach)
- [Frida Module.findExportByName](https://frida.re/docs/javascript-api/#module-findexportbyname)
