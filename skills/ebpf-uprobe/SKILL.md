---
name: ebpf-uprobe
description: "Probe a function inside a specific binary from the kernel side, which works when attaching a debugger to the process is not permitted. Use when ptrace is restricted but the kernel permits uprobes on the target binary"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [ebpf, uprobe, user-space]
phase: kernel
---

# Attach an eBPF uprobe to a user-space function

> Probe a function inside a specific binary from the kernel side, which works when attaching a debugger to the process is not permitted

**Use when:** ptrace is restricted but the kernel permits uprobes on the target binary

**Avoid when:** the target binary is replaced frequently, because uprobes are bound to an inode and offset

## Procedure

1. Resolve the symbol offset in the on-disk binary, since the probe binds to a file offset, not a runtime address.
2. Attach the uprobe with the full path to the binary so the probe binds to the right inode.
3. Read user-space strings with bpf_probe_read_user_str and check the truncated length.
4. Detach and confirm removal, then record the binary hash the probe was bound to.

## Signals

- offset-resolved
- uprobe-attached
- binary-hashed

## Patterns

**1. uprobe attach**

```
bpftrace -e 'uprobe:/opt/app/bin/server:parse_header { printf("%s\n", str(arg1)); }'
```

## Pitfalls

- Binding to a symlink or a relative path can attach to the wrong inode after an upgrade.
- User-space reads from an unmapped page return an error; treat zero-length results as a read failure, not an empty string.

## Done when

- The probe fires on a real call in the named binary.
- The binary hash and probe offset are recorded.

## References

- [bpftrace uprobes](https://bpftrace.org/)
