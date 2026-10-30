# Security

## Scope

This repository contains procedures and generated documents. It ships no network service, no
daemon and no privileged helper.

## Intended use

These skills describe instrumenting processes you are authorised to instrument. Attaching a
debugger, preloading a library or loading an eBPF program on a host you do not own or have written
permission to test may be unlawful and is outside the intent of this pack. The `scope` phase
exists specifically to make that boundary checkable before the first attach.

## Reporting a problem

If you find a defect in a skill — a pattern that is wrong, a procedure that corrupts a target, or
a teardown step that leaves state behind — open an issue with the slug and the observed
behaviour. Please include the tool version and the target platform.

## Known limitations

- Nothing in this repository attaches to a live target during tests.
- Code patterns are reviewed against documentation, not executed in CI.
- No claim is made that the skills cover every platform; they target Linux and Android, with
  macOS support limited to what Frida documents.
