---
name: frida-types-from-module
description: "Ask Frida for a function's declared prototype so argument reading uses the real signature and varargs are handled deliberately. Use when the function takes structs or varargs and guessing types would produce garbage"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [inspect, types, signature]
phase: inspect
---

# Resolve a function's type from the runtime

> Ask Frida for a function's declared prototype so argument reading uses the real signature and varargs are handled deliberately

**Use when:** the function takes structs or varargs and guessing types would produce garbage

**Avoid when:** no type information is present and all decoding must be done from disassembly

## Procedure

1. Use Module.getExportByName plus DebugSymbol.getFunctionByName to reach the typed symbol.
2. Read the prototype and record argument types and the return type verbatim.
3. For varargs, record how many variadic arguments you actually read and why.
4. Fall back to manual decoding only with the disassembly stored alongside as justification.

## Signals

- prototype-resolved
- types-recorded
- fallback-justified

## Patterns

**1. typed symbol**

```
const f = DebugSymbol.getFunctionByName('parse_header');
send({name: f.name, addr: f.address});
```

## Pitfalls

- Reading a vararg that was not passed for this call shape produces a plausible but wrong value.
- DebugSymbol lookups fail on stripped binaries; record the failure rather than silently switching to guesses.

## Done when

- The prototype is recorded from the runtime or its absence is documented.
- Vararg reads are enumerated and justified.

## References

- [Frida DebugSymbol](https://frida.re/docs/javascript-api/#debugsymbol)
