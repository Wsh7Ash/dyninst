# Results

Reproducible evidence for the claims in `README.md`.

## Environment

- OS: Windows (MSYS2 shell), Python 3.14
- Runtime: Python 3.10+ standard library only; `pytest` as a dev dependency
- Network: not required at any point

## Gates that were run

### 1. Corpus validation

```
$ PYTHONPATH=src python -m dyninst validate
50/50 skills valid
```

Machine-readable form reports the enforced floors and an empty issue list:

```
$ PYTHONPATH=src python -m dyninst validate --json
{
  "pack": "dyninst",
  "version": "1.0.0",
  "expected": 50,
  "valid": 50,
  "total": 50,
  "passed": true,
  "floors": {"min_steps": 3, "min_signals": 2, "min_patterns": 1,
             "min_pitfalls": 2, "min_words": 80},
  "issues": []
}
```

### 2. Test suite

```
$ python -m pytest -q
............................                                             [100%]
```

28 tests, all passing. They cover:

- 50/50 corpus shape, unique slugs, unique case-insensitive titles, unique summaries;
- all 13 phases present, every phase populated;
- per-skill floors (steps, signals, patterns, pitfalls, rendered words);
- every reference is an HTTPS-labelled markdown link;
- kebab-case slugs, no duplicate steps inside a skill;
- committed `skills/<slug>/SKILL.md` equals a fresh render byte for byte;
- `pack.json` lists 50 skills, each digest is 64 hex chars and matches the committed file's sha256;
- `build_pack` is deterministic and produces exactly 52 artifacts;
- the catalog lists every slug;
- CLI: `validate` reports `50/50`, `--json` parses, `list` counts 50 and filters phase `kernel` to 3, `show` prints front-matter and the right title, unknown slug exits 2, unknown command exits 2, `--version` prints `dyninst 1.0.0`, and `render`/`catalog`/`build` all succeed.

### 3. Build output

```
$ PYTHONPATH=src python -m dyninst build
Built 52 artifacts, 11042 rendered skill words
```

11042 words across 50 skills is a mean of 221 rendered words per skill, against a floor of 80.

### 4. Negative controls

The validator must be able to say no. Both checks below were run against in-memory copies of
the corpus, so the committed files were never degraded:

```
$ python -c "<drop the pitfalls from skill 0>"
issues: ['plan-generate: pitfalls: need >= 2, got 0']

$ python -c "<give skill 1 skill 0's slug>"
issues: ['duplicate titles in pack: ["capture a clean baseline before instrumenting"]',
         'duplicate summaries in pack']
```

The second check demonstrates that a slug rename which leaves the title and summary in place is
still rejected, because uniqueness is enforced on all three fields rather than the slug alone.

## Full transcript

`results/demo_transcript.txt` contains the verbatim output of `validate`, `list --phase kernel`,
`show gdb-watchpoint` (first 28 lines) and both negative controls.

## What was not run

- **No target was instrumented.** There is no Frida session, GDB session, LD_PRELOAD library or
  eBPF program executed by this suite. The skills are procedures and code patterns; the repository
  does not ship a driver.
- **The code patterns were not executed.** They are reviewed against the cited documentation but
  are not compiled or attached in CI.
- **No cross-platform check.** Frida and GDB behaviour on macOS and arm64 Linux was not exercised;
  the skills that describe them are written from the documented interface.
