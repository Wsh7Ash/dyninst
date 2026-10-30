---
name: frida-enumerate-modules
description: "List every module with base, size and path so a probe cannot silently attach to a different copy of a library than the one you audited. Use when several copies of a library could be loaded, for example system and bundled versions"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [inspect, modules, mapping]
phase: inspect
---

# Enumerate loaded modules to confirm what is mapped

> List every module with base, size and path so a probe cannot silently attach to a different copy of a library than the one you audited

**Use when:** several copies of a library could be loaded, for example system and bundled versions

**Avoid when:** the process maps more than a few thousand modules and a full dump would be noise

## Procedure

1. Call Process.enumerateModules and write the list to a file outside the process.
2. Sort by base address and check for duplicate names with different paths.
3. Confirm the module your probes target by path and base address, not by name alone.
4. Compare this list against /proc/PID/maps for the same moment as a cross-check.

## Signals

- modules-listed
- duplicates-checked
- maps-cross-checked

## Patterns

**1. enumerate**

```
Process.enumerateModules().forEach(m => send([m.base.toString(), m.size, m.path]));
```

## Pitfalls

- Resolving a probe by name when two modules share the name, which picks an arbitrary copy.
- Comparing a module list from one moment against maps from another after modules were loaded or unloaded.

## Done when

- The module list is captured with base, size and path.
- The target module is identified by path and base, not name.

## References

- [Frida Process.enumerateModules](https://frida.re/docs/javascript-api/#process-enumeratemodules)
