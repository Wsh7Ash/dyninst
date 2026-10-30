---
name: ebpf-tracepoint
description: "Attach to a documented tracepoint whose ABI the kernel maintains, so the probe does not break when internal function signatures change. Use when a tracepoint exists for the event you care about and you want a probe that survives kernel updates"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [ebpf, tracepoint, stability]
phase: kernel
---

# Use a stable tracepoint instead of a raw kprobe

> Attach to a documented tracepoint whose ABI the kernel maintains, so the probe does not break when internal function signatures change

**Use when:** a tracepoint exists for the event you care about and you want a probe that survives kernel updates

**Avoid when:** no tracepoint covers the event and only an internal function does

## Procedure

1. List available tracepoints from /sys/kernel/tracing/events and choose the one matching the event.
2. Read the tracepoint's format file to learn the field offsets the probe will read.
3. Attach and read only the documented fields rather than poking at adjacent memory.
4. Record the kernel version and tracepoint name so the capture can be reproduced.

## Signals

- tracepoint-selected
- format-read
- kernel-version-recorded

## Patterns

**1. tracepoint attach**

```
bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args.filename)); }'
```

## Pitfalls

- Reading a field that the format file marks as a different type produces plausible garbage.
- Assuming tracepoint field offsets are stable across kernel versions; re-read the format file per host.

## Done when

- The tracepoint fires and documented fields are read correctly.
- Kernel version and tracepoint name are recorded.

## References

- [tracefs events](https://docs.kernel.org/trace/events.html)
