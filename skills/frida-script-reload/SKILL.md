---
name: frida-script-reload
description: "Replace a running script with an updated one in the same session so a probe fix does not cost you the attachment window. Use when the first script has a bug or needs a new probe and the process state is expensive to recreate"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [capture, frida, iteration]
phase: capture
---

# Swap a Frida script without losing the session

> Replace a running script with an updated one in the same session so a probe fix does not cost you the attachment window

**Use when:** the first script has a bug or needs a new probe and the process state is expensive to recreate

**Avoid when:** the script installs hooks whose removal is unsafe, in which case a fresh attach is cleaner

## Procedure

1. Detach every listener the old script installed and confirm no hooks remain.
2. Load the new script into the same session and verify it evaluates without exceptions.
3. Re-resolve probe addresses, because module load order can differ from the first script's assumptions.
4. Record both script versions and their hashes with the capture so the evidence names what ran.

## Signals

- old-hooks-removed
- new-script-loaded
- versions-hashed

## Patterns

**1. reload**

```
session.create_script(new_source)
# after load(): script.exports.install()
```

## Pitfalls

- Reloading without detaching old listeners doubles every event and corrupts the counts.
- Reusing cached probe addresses across a reload can point at unmapped memory if a module was unloaded.

## Done when

- The new script runs with no leftover hooks from the old one.
- Both script hashes are recorded with the capture.

## References

- [Frida Session API](https://frida.re/docs/javascript-api/#session)
