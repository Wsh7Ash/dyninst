---
name: gdb-frame-capture
description: "Record a backtrace with frame arguments and source lines so a reviewer can follow the same path without re-running the crash. Use when the backtrace is the main evidence for a reachability claim"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [post-mortem, backtrace, evidence]
phase: post-mortem
---

# Capture a backtrace that survives review

> Record a backtrace with frame arguments and source lines so a reviewer can follow the same path without re-running the crash

**Use when:** the backtrace is the main evidence for a reachability claim

**Avoid when:** the stack is corrupted, in which case say so instead of presenting a plausible-looking trace

## Procedure

1. Capture bt full so frame arguments and locals are included with each frame.
2. Check for frames marked as corrupted or as question marks and record them as unknown rather than dropping them.
3. Resolve each frame to a function plus file and line where debug info allows.
4. Save the raw backtrace text, not a reformatted table, so it can be compared later.

## Signals

- backtrace-captured
- corruption-checked
- frames-resolved

## Patterns

**1. full backtrace**

```
gdb -q ./server core -batch -ex 'set print frame-arguments all' -ex 'bt full'
```

## Pitfalls

- A corrupted stack can produce a confident chain of frames that never ran.
- Trimming frames to make a path look shorter is misrepresentation; keep every frame and mark unknowns.

## Done when

- A full backtrace is saved with arguments and unknowns marked.
- Every frame is either resolved or explicitly marked unresolved.

## References

- [GDB backtrace](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Backtrace.html)
