# dyninst

**50 validated skills for instrumenting a live target — Frida, GDB, LD_PRELOAD and eBPF — plus a CLI that validates, renders and catalogs them.**

Every skill is a self-contained procedure with a written procedure, observable signals, a code pattern, the pitfalls that waste an engagement, completion criteria and at least one HTTPS reference. The pack is checked by a validator with hard floors, and the generated `SKILL.md` files are verified against a fresh render on every test run.

```
$ dyninst validate
50/50 skills valid

$ dyninst list --phase kernel
ebpf-kprobe       kernel   Attach an eBPF kprobe to a kernel function
ebpf-tracepoint   kernel   Use a stable tracepoint instead of a raw kprobe
ebpf-uprobe       kernel   Attach an eBPF uprobe to a user-space function
3 skill(s)
```

## Why this pack exists

Instrumentation work fails in predictable ways, and most of them are not about not knowing the API:

- a probe is written before the target's constraints are checked, so it never attaches;
- the capture is real but there is no baseline, so nothing can be compared;
- the hook fires but the argument decoding is wrong, so the finding says the opposite of the truth;
- the session is detached but a listener survives, and the next measurement is polluted;
- the process is instrumented outside the authorised scope because scope was checked once, at the start.

Each skill here is written against one of those failure modes. The pack covers the full session: `plan` → `attach` → `debug`/`intercept`/`trace`/`kernel` → `post-mortem`/`signal`/`capture` → `inspect` → `benchmark` → `teardown`, with `scope` gates on both ends.

## Install

```bash
python -m pip install -e .
dyninst validate
```

No runtime dependencies. Python 3.10+.

## Commands

| Command | What it does |
|---|---|
| `dyninst validate [--json]` | Run every corpus rule; exit 1 with the specific issues if any fail |
| `dyninst list [--phase P]` | List skills, optionally filtered by one of the 13 phases |
| `dyninst show SLUG` | Print one fully rendered `SKILL.md` |
| `dyninst render` | Regenerate `skills/<slug>/SKILL.md` for all 50 |
| `dyninst catalog` | Regenerate `results/catalog.md` |
| `dyninst build` | Regenerate skills, `pack.json` and the catalog in one pass |

## Use as agent skills

Each rendered skill is a `SKILL.md` with YAML front-matter (`name`, `description`, `pack`, `version`, `category`, `tags`, `phase`) and a markdown body. Point Claude Code, opencode or any runtime that loads skill directories at `skills/`:

```
skills/frida-attach/SKILL.md
skills/gdb-watchpoint/SKILL.md
skills/ebpf-uprobe/SKILL.md
...
```

`dyninst show <slug>` prints exactly the file that a runtime would load, so you can preview a skill before installing it.

## The validator is the point

Nine rules, enforced for all 50 skills:

1. at least 3 procedure steps;
2. at least 2 observable signals;
3. at least 1 code pattern;
4. at least 2 pitfalls;
5. a declared phase from the fixed set of 13;
6. at least one HTTPS-labelled reference;
7. a summary long enough to be useful (>= 20 characters);
8. an `avoid_when` clause long enough to be specific (>= 10 characters);
9. at least 80 rendered words, measured after stripping front-matter.

Package-level rules add: exactly 50 skills, all 13 phases present, unique slugs, unique case-insensitive titles, unique summaries.

```
$ python -c "<drop the pitfalls from one skill>"
issues: ['plan-generate: pitfalls: need >= 2, got 0']
```

## Phases and counts

| Phase | Skills | Focus |
|---|---|---|
| `plan` | 4 | target, baseline, emitter choice, symbol resolution |
| `attach` | 5 | Frida attach/spawn, GDB local/remote, LD_PRELOAD launch |
| `debug` | 4 | breakpoints, watchpoints, single-step, conditions |
| `intercept` | 6 | libc/native/Java/network interposition |
| `trace` | 5 | entry/return, multi-probe timelines, Stalker, tracepoints |
| `kernel` | 3 | kprobe, uprobe, tracepoint |
| `post-mortem` | 4 | core analysis, backtraces, signal decoding, live snapshots |
| `signal` | 1 | in-process fault capture |
| `capture` | 5 | script reload, and three emitters (Frida, GDB, LD_PRELOAD) |
| `inspect` | 4 | type environment, modules, prototypes, memory ranges |
| `teardown` | 4 | clean detach, wedged-session recovery, signal-safe unload |
| `benchmark` | 3 | overhead measurement, no-op control, cross-arch normalisation |
| `scope` | 3 | target check, module check, plan merge without widening scope |

## Repository layout

```
src/dyninst/
  model.py       immutable Skill shape and dict loader
  validate.py    the 9 per-skill rules and the package rules
  render.py      deterministic SKILL.md, catalog and manifest rendering
  cli.py         validate / list / show / render / catalog / build
  corpus/        50 authored skills in part1..part3
skills/          50 generated SKILL.md files, byte-identical to a fresh render
results/
  catalog.md     generated index
  demo_transcript.txt  real command output
pack.json        manifest of 50 slugs with sha256 digests
tests/           28 tests: corpus rules, artifact drift, manifest digests, CLI
```

## Guarantees the tests actually check

- `validate_pack(PACK, SKILLS) == []`.
- Every committed `skills/<slug>/SKILL.md` equals a fresh render, byte for byte.
- Every digest in `pack.json` equals the sha256 of the committed file.
- `build_pack` is deterministic: two builds produce identical mappings.
- An out-of-range CLI argument exits 2; an unknown slug exits 2 with a message.
- The CLI reports exactly `50/50 skills valid` and `--json` is machine-readable.

## Limits

- **Nothing here attaches to a real target in CI.** The skills are procedures, not drivers; the repository ships no Frida agent, no GDB session and no eBPF program.
- The code patterns are reviewed for correctness against the cited documentation, but they are not executed in the test suite.
- eBPF skills assume a kernel with BTF and tracefs available; they do not cover kernels where bpftrace is unavailable.
- Phone-side Frida (`frida-java-hook`) assumes a debuggable build or a rooted device.

## License

MIT.
