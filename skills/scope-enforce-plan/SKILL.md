---
name: scope-enforce-plan
description: "Check the plan's target against a written scope document before any attach, so an out-of-scope process is never instrumented by accident. Use when the engagement has a written scope and several targets are available on the host"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [scope, authorisation, guard]
phase: scope
---

# Refuse instrumentation outside the authorised scope

> Check the plan's target against a written scope document before any attach, so an out-of-scope process is never instrumented by accident

**Use when:** the engagement has a written scope and several targets are available on the host

**Avoid when:** the target is your own test binary and scope is not a concept that applies

## Procedure

1. Write the scope as a machine-readable list of host and binary identifiers before starting.
2. Check the resolved target against that list and abort with a clear message when it does not match.
3. Record the scope revision and the check result in the evidence bundle.
4. Re-check after any respawn or redeploy, because the identifier can change while the name stays the same.

## Signals

- scope-loaded
- target-checked
- check-recorded

## Patterns

**1. scope check**

```
python -m dyninst scope check --plan plan.yml --scope scope.json || exit 1
```

## Pitfalls

- Matching by process name alone, which can select a different binary with the same name.
- Checking scope once at the start and never again after a redeploy changed the build.

## Done when

- An out-of-scope target is refused before any attach.
- The scope revision and check result are recorded.

## References

- [PTES scoping](https://www.pentest-standard.org/index.php/Scoping)
