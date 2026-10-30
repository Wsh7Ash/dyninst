---
name: scope-validate-imports
description: "Compare every module the plan resolves against the scope list so a probe cannot silently land in a vendor library that is out of scope. Use when the target loads third-party or vendor libraries that the engagement excludes"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [scope, modules, validation]
phase: scope
---

# Check that instrumentation only touches in-scope modules

> Compare every module the plan resolves against the scope list so a probe cannot silently land in a vendor library that is out of scope

**Use when:** the target loads third-party or vendor libraries that the engagement excludes

**Avoid when:** every loaded module is in scope by definition

## Procedure

1. Enumerate the modules the plan will touch after resolution, not the ones you intended to touch.
2. Compare the resolved module paths against the scope list and list every mismatch.
3. Drop or refuse any probe that resolves into an excluded module, and record the refusal.
4. Store the resolved-to-scope mapping with the capture so the boundary is auditable.

## Signals

- modules-resolved
- scope-compared
- refusals-recorded

## Patterns

**1. import check**

```
python -m dyninst scope imports --plan plan.yml --scope scope.json
```

## Pitfalls

- Resolving by symbol name and landing in a vendor copy of the library that is excluded.
- Recording only the intended modules rather than the ones the symbol resolution actually selected.

## Done when

- Every resolved module is checked against scope and mismatches are refused.
- The mapping is stored with the capture.

## References

- [PTES scoping](https://www.pentest-standard.org/index.php/Scoping)
