---
name: scope-merge-two-plans
description: "Combine plans from two sessions into one and fail when the union exceeds either authorised scope, instead of silently inheriting the larger one. Use when two teams or two sessions produced plans for the same target and they must run together"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [scope, merge, authorisation]
phase: scope
---

# Merge two instrumentation plans without widening scope

> Combine plans from two sessions into one and fail when the union exceeds either authorised scope, instead of silently inheriting the larger one

**Use when:** two teams or two sessions produced plans for the same target and they must run together

**Avoid when:** the plans were authorised under the same scope and a merge cannot add anything

## Procedure

1. Load both plans with their scope references and compute the union of probes and targets.
2. Check the union against the intersection of the two scopes, since a merge cannot widen what was authorised.
3. Fail with the specific out-of-scope entries rather than producing a merged plan that quietly exceeds scope.
4. Record both source plan revisions and the merged revision in the result.

## Signals

- plans-loaded
- intersection-checked
- revision-recorded

## Patterns

**1. merge check**

```
python -m dyninst scope merge --a plan-a.yml --b plan-b.yml --scope-a sa.json --scope-b sb.json
```

## Pitfalls

- Unioning the scopes as well as the probes, which authorises work neither engagement covered.
- Merging without recording the source revisions, so the merged plan cannot be traced back.

## Done when

- The merged plan is checked against the scope intersection and refuses on excess.
- Source and merged revisions are recorded.

## References

- [PTES scoping](https://www.pentest-standard.org/index.php/Scoping)
