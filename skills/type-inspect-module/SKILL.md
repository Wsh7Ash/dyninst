---
name: type-inspect-module
description: "Read the runtime type information for a module so hook signatures and struct layouts come from the target rather than from a header you assumed. Use when you are about to decode arguments and need the real runtime layout"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [inspect, types, layout]
phase: inspect
---

# Inspect a module's type environment

> Read the runtime type information for a module so hook signatures and struct layouts come from the target rather than from a header you assumed

**Use when:** you are about to decode arguments and need the real runtime layout

**Avoid when:** the binary is fully stripped and carries no debug or BTF type information

## Procedure

1. Locate the module base address and its path with Module.findBaseAddress and Module.load.
2. Enumerate the exported symbols and record the ones matching your probe set.
3. For struct-shaped arguments, resolve field offsets from the runtime table instead of hardcoding them.
4. Store the resolved offsets next to the capture so a reviewer can check the decoding.

## Signals

- module-base-found
- symbols-enumerated
- offsets-recorded

## Patterns

**1. module inspect**

```
const m = Process.getModuleByName('libparse.so');
send({base: m.base, size: m.size, path: m.path});
send({exports: m.enumerateExports().filter(e => e.type === 'function').map(e => e.name)});
```

## Pitfalls

- Hardcoding struct offsets from a source header that does not match the shipped build.
- Assuming ABI-stable layout across compiler versions and optimisation levels.

## Done when

- The module base, path and relevant exports are recorded.
- Every decoded field offset is traceable to a runtime observation.

## References

- [Frida Module API](https://frida.re/docs/javascript-api/#module)
