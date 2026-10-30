---
name: emitter-gdb-macro
description: "Emit a GDB batch file that sets the planned breakpoints, captures the planned state and detaches, so a capture is one reproducible command. Use when the capture must be reproducible by a reviewer with the same binary"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [capture, emitter, gdb]
phase: capture
---

# Generate a GDB command file from the plan

> Emit a GDB batch file that sets the planned breakpoints, captures the planned state and detaches, so a capture is one reproducible command

**Use when:** the capture must be reproducible by a reviewer with the same binary

**Avoid when:** the session needs interactive judgement at each stop

## Procedure

1. Emit set pagination off and set confirm off so the batch file cannot block on a prompt.
2. Emit one break per planned probe and a commands block that captures the declared state and continues.
3. Emit a final detach so the run leaves the process alive, not killed.
4. Record the GDB version with the emitted file, because command syntax varies between releases.

## Signals

- batch-file-emitted
- state-capture-encoded
- detach-emitted

## Patterns

**1. gdb batch**

```
set pagination off
set confirm off
break parse_header
commands
  silent
  printf "len=%d\n", $rsi
  continue
end
run
detach
```

## Pitfalls

- Omitting set confirm off makes the batch file stop on a confirmation prompt and hang.
- A commands block that does not continue stops at the first hit and captures nothing further.

## Done when

- The batch file runs to completion without prompting.
- The emitted file is stored with the capture it produced.

## References

- [GDB command files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Command-Files.html)
