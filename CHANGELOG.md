# Changelog

## 1.0.0 — 2026-10-30

Initial release.

- 50 authored skills across 13 phases: plan, attach, debug, intercept, trace, kernel,
  post-mortem, signal, capture, inspect, teardown, benchmark, scope.
- `dyninst validate` with nine per-skill rules and six package rules, `--json` output and
  meaningful exit codes.
- `dyninst list`, `show`, `render`, `catalog`, `build`.
- Deterministic renderer; committed `skills/`, `pack.json` and `results/catalog.md` are verified
  against a fresh render by the test suite.
- 28 tests covering corpus shape, floors, artifact drift, manifest digests and the CLI surface.
