# Usage

## Install

```bash
python -m pip install -e .
dyninst --version
```

Or run without installing, from the repository root:

```bash
PYTHONPATH=src python -m dyninst validate
```

## Pick skills for a session

The pack is organised by phase, so a session reads left to right.

```bash
dyninst list --phase plan       # write the plan, baseline and symbol map
dyninst list --phase attach     # choose and perform attachment
dyninst list --phase trace      # observe what the plan said to observe
dyninst list --phase teardown   # leave the process clean
```

Read one skill in full before acting on it:

```bash
dyninst show frida-spawn
```

## Worked example: proving an argument reached a parser

1. **Plan the probes.** `dyninst show plan-probe-map` walks the symbol resolution. Resolve
   `parse_header` in `libparse.so` and record its address.
2. **Take a baseline.** `dyninst show plan-baseline-capture`. Run the target with
   `--input case01.bin` and store the exit code, output and timing.
3. **Attach from the first instruction** if the bug is in startup:
   `dyninst show frida-spawn`. The script installs hooks, then resumes, so the first call is not
   missed.
4. **Observe entry with typed arguments.** `dyninst show probe-function-entry`. Read the length
   argument, bound the pointer read, and emit a sequence number.
5. **Check your overhead claim.** `dyninst show emitter-benchmark` and
   `dyninst show overhead-control-run`. Five runs per condition, median plus spread, and a no-op
   hook variant so attachment cost is separated from logging cost.
6. **Tear down and verify.** `dyninst show teardown-verify`. Detach every listener, compare the
   module list with the pre-session snapshot, and re-run the baseline input.
7. **Confine the work to scope.** `dyninst show scope-enforce-plan` and
   `dyninst show scope-validate-imports`, so a probe cannot land in an excluded vendor module.

The output of steps 3–5 is what a report cites. A claim that "attacker input reached the parser"
is only worth writing once step 4 produced an entry record with a bounded read and a sequence
number that matches the return record from `probe-function-return`.

## Working with the corpus

Validate after any edit:

```bash
dyninst validate
```

If you add a skill, add it to one of `corpus/part1..part3.py`, then:

```bash
dyninst validate     # must be 50/50
dyninst build        # rewrites skills/, pack.json, results/catalog.md
python -m pytest -q  # artifact drift and CLI checks
```

Removing a skill means removing it from the corpus *and* rebuilding, or `test_committed_skills_match_a_fresh_render`
will fail on the leftover directory — which is the intended behaviour.

## Using the skills from an agent runtime

Point the runtime at `skills/`. Each file begins with YAML front-matter:

```yaml
---
name: gdb-watchpoint
description: "Trap the exact instruction that mutates a field ... Use when a value changes unexpectedly"
pack: dyninst
version: 1.0.0
category: dynamic-instrumentation
tags: [gdb, watchpoint, memory]
phase: debug
---
```

A runtime that selects skills by description will match on the summary plus the `use_when`
clause, so those two fields are the ones worth reading first when choosing a skill.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | validation failed; issues are printed |
| 2 | usage error: unknown command or unknown slug |
