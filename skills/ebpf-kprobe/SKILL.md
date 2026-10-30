---
name: ebpf-kprobe
description: "Observe kernel-side function entry with a kprobe and read the arguments from the register context, without loading a kernel module. Use when the behaviour you need is inside the kernel and user-space hooks cannot see it"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [ebpf, kprobe, kernel]
phase: kernel
---

# Attach an eBPF kprobe to a kernel function

> Observe kernel-side function entry with a kprobe and read the arguments from the register context, without loading a kernel module

**Use when:** the behaviour you need is inside the kernel and user-space hooks cannot see it

**Avoid when:** the kernel is built without BTF or the symbol you need is inlined and has no probe point

## Procedure

1. Confirm the target symbol exists in /proc/kallsyms and is not inlined away.
2. Attach a kprobe with bpftrace or a small BCC program and read arguments from the pt_regs context.
3. Bound every kernel memory read with bpf_probe_read_user or bpf_probe_read_kernel and check the return.
4. Detach the probe and verify with bpftool that no program remains attached.

## Signals

- symbol-present
- kprobe-attached
- probe-detached

## Patterns

**1. kprobe one-liner**

```
bpftrace -e 'kprobe:vfs_open { printf("%s %d\n", comm, pid); }'
```

## Pitfalls

- Dereferencing kernel pointers directly in the probe fails; use the bounded read helpers.
- A kprobe on an inlined or renamed symbol never fires, which looks identical to a quiet system.

## Done when

- The probe fires on a real event and arguments are captured.
- bpftool confirms no program is left attached.

## References

- [bpftrace kprobes](https://bpftrace.org/)
- [BPF helpers](https://docs.kernel.org/bpf/helper-bpf-probe-read-kernel.html)
