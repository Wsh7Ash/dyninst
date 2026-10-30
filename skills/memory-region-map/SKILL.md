---
name: memory-region-map
description: "Enumerate readable, writable and executable ranges so a fault or a read can be attributed to a specific mapping such as heap, stack or module. Use when you need to explain why an address was valid, invalid or unexpectedly writable"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [inspect, memory, mapping]
phase: inspect
---

# Map memory regions to classify an access

> Enumerate readable, writable and executable ranges so a fault or a read can be attributed to a specific mapping such as heap, stack or module

**Use when:** you need to explain why an address was valid, invalid or unexpectedly writable

**Avoid when:** the region set is changing so fast that any snapshot is stale before it is written

## Procedure

1. Enumerate ranges with Process.enumerateRanges and record base, size and protection per range.
2. Classify the address under test by looking up the range that contains it.
3. Compare the protection against the access type, since a write to a read-only range is a different bug from an unmapped read.
4. Snapshot with the timestamp and note that later allocations are not represented.

## Signals

- ranges-enumerated
- address-classified
- snapshot-timestamped

## Patterns

**1. range lookup**

```
const r = Process.findRangeByAddress(ptr('0x7f0000123000'));
send(r ? {base: r.base, size: r.size, prot: r.protection} : {unmapped: true});
```

## Pitfalls

- Treating a region snapshot as current after the program has mapped or unmapped memory.
- Confusing an unmapped read with a permission violation; si_code distinguishes them and the range must too.

## Done when

- The address is classified against a timestamped range snapshot.
- The protection is compared with the access type.

## References

- [Frida Process.enumerateRanges](https://frida.re/docs/javascript-api/#process-enumerateranges)
