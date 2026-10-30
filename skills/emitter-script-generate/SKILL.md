---
name: emitter-script-generate
description: "Emit a runnable Frida script whose probes, argument decoding and teardown come from the instrumentation plan rather than ad-hoc editing. Use when the plan is settled and the capture script should match it exactly"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [capture, emitter, frida]
phase: capture
---

# Generate a Frida capture script from the plan

> Emit a runnable Frida script whose probes, argument decoding and teardown come from the instrumentation plan rather than ad-hoc editing

**Use when:** the plan is settled and the capture script should match it exactly

**Avoid when:** the target needs hand-written decoding that the emitter cannot express

## Procedure

1. Read the probe list and module names from the plan, refusing to emit when a probe is unresolved.
2. Emit one Interceptor.attach block per probe with arguments decoded by declared type.
3. Emit the teardown block that detaches every listener and flushes the log.
4. Hash the emitted script and store the hash beside the plan revision it came from.

## Signals

- script-emitted
- probes-matched-plan
- script-hashed

## Patterns

**1. emitter output**

```
// generated from plan rev 3
const P = Module.findExportByName('libparse.so', 'parse_header');
if (P === null) throw new Error('probe unresolved: parse_header');
Interceptor.attach(P, { onEnter(a) { send({fn: 'parse_header', n: a[1].toInt32()}); } });
```

## Pitfalls

- Emitting a script with an unresolved probe and letting it throw at runtime instead of refusing at generation time.
- Editing the generated script by hand afterwards, which makes the hash meaningless.

## Done when

- The emitted script matches the plan's probe list exactly.
- Generation refuses when a probe cannot be resolved.

## References

- [Frida scripting](https://frida.re/docs/quickstart/)
