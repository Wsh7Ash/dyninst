---
name: ldpreload-net-intercept
description: "Hook connect and getaddrinfo to record every destination a process tries to reach, which is evidence a network claim needs. Use when you need to show where a process connects, including failed attempts"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [intercept, ldpreload, network]
phase: intercept
---

# Intercept outbound connections with a preload hook

> Hook connect and getaddrinfo to record every destination a process tries to reach, which is evidence a network claim needs

**Use when:** you need to show where a process connects, including failed attempts

**Avoid when:** the target issues raw syscalls or uses a statically linked resolver

## Procedure

1. Interpose connect and getaddrinfo, resolving the originals with dlsym RTLD_NEXT.
2. Decode the sockaddr by family: IPv4, IPv6 and unix sockets each need different handling.
3. Record the destination and the result, including errno, so failed attempts are visible.
4. Cross-check against a packet capture or ss output to prove the hook's coverage.

## Signals

- connect-hooked
- destinations-recorded
- coverage-cross-checked

## Patterns

**1. connect hook**

```
int connect(int fd, const struct sockaddr *addr, socklen_t len) {
  log_sockaddr(addr, len);
  int rc = real_connect(fd, addr, len);
  log_result(rc, errno);
  return rc;
}
```

## Pitfalls

- Casting every sockaddr to sockaddr_in without checking sa_family, which misreports IPv6 and unix sockets.
- Logging only successful connections, which hides the blocked destinations that often matter most.

## Done when

- Every connect attempt is recorded with family-correct decoding and result.
- Coverage is checked against an independent observation.

## References

- [connect(2)](https://man7.org/linux/man-pages/man2/connect.2.html)
- [getaddrinfo(3)](https://man7.org/linux/man-pages/man3/getaddrinfo.3.html)
