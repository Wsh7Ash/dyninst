---
name: gdb-remote-target
description: "Debug a process on another host through gdbserver, keeping the binary and symbol files local so the capture is attributable to a known build. Use when the target runs on a host you cannot run a debugger on directly"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [attach, gdb, remote]
phase: attach
---

# Attach GDB to a remote target through gdbserver

> Debug a process on another host through gdbserver, keeping the binary and symbol files local so the capture is attributable to a known build

**Use when:** the target runs on a host you cannot run a debugger on directly

**Avoid when:** the network path to the target is not authorised or not encrypted

## Procedure

1. Start gdbserver on the target host bound to a specific interface and port, and record both.
2. Copy the exact binary and its debug symbols to the analysis host and confirm the build-id matches.
3. Connect with target remote host:port and verify the reported architecture and thread list.
4. Capture state, then detach so the remote process continues instead of being killed.

## Signals

- gdbserver-bound
- build-id-matched
- remote-detached

## Patterns

**1. remote attach**

```
gdbserver 127.0.0.1:2345 --attach 4711
# locally
gdb -q ./server -ex 'target remote 127.0.0.1:2345' -ex 'info threads' -ex 'detach'
```

## Pitfalls

- Binding gdbserver to all interfaces exposes an unauthenticated debug port to the network.
- Debugging with symbols from a different build produces frame names that are confidently wrong.

## Done when

- gdbserver is bound to an authorised interface and the build-id matches the local binary.
- The remote process continues after detach.

## References

- [gdbserver](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Server.html)
