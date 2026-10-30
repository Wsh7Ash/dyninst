# Architecture

dyninst is three layers and one rule: the corpus is data, the renderer is pure, and the
validator is the only thing allowed to decide whether a skill is acceptable.

```
corpus/part1..part3.py   authored dicts
        |
        v  skill_from_dict (model.py)
      Skill objects  -----> validate.py -----> issues
        |
        v  render_skill (render.py)
   skills/<slug>/SKILL.md, pack.json, results/catalog.md
```

## Layer 1 — corpus

Skills are authored as plain dicts with a fixed set of required keys. Authoring in dicts keeps
the diff for a new skill small and makes the corpus easy to review, while the loader
(`skill_from_dict`) is the only place that has to care about shape.

`Skill` is a frozen dataclass. Steps, signals, pitfalls, done-when items and references are
tuples of strings; patterns are tuples of `(label, code)` pairs. Nothing downstream mutates a
skill, which is what makes the renderer a pure function.

## Layer 2 — validation

`validate_skill` applies nine rules to one skill; `validate_pack` adds the package rules
(exactly 50 skills, all phases represented, unique slugs, titles and summaries).

The floors are constants, not configuration, because a pack whose floors can be lowered per run
is a pack whose floors mean nothing. If a skill cannot meet the floor honestly, the skill is
rewritten — that is the intended pressure.

Phase is a closed set of 13 values. A skill that does not fit any phase is a sign the phase list
should be discussed and changed deliberately, not that an arbitrary phase string should be
accepted.

## Layer 3 — rendering

`render_skill` is deterministic: the same `Skill` and pack always produce byte-identical output.
Front-matter is a fixed key order, and JSON string escaping is used for the description so that a
summary containing quotes cannot break the YAML block.

`build_pack` returns an ordered mapping of relative path to text. Passing `root` also writes the
files. Returning the mapping is what lets the tests compare a committed artifact with a fresh
render without touching disk, and lets `build` report the word total it produced.

## Why the artifacts are committed

The `skills/` tree, `pack.json` and the catalog are generated *and* committed. That is deliberate:

- a user can install the pack from a checkout without running a build step;
- drift between the corpus and the artifacts becomes a test failure rather than a silent
  inconsistency;
- `pack.json` digests pin what was published.

The test suite enforces all three by re-rendering every skill and comparing bytes, then
re-hashing every committed file against the manifest.

## CLI surface

The CLI is intentionally thin: it loads the corpus, calls the same functions the tests call, and
prints. There is no second implementation of validation or rendering inside the CLI, so a CLI
result cannot disagree with a test result.

Exit codes are meaningful: `0` success, `1` validation failed, `2` usage error. A caller can
therefore gate a CI step on `dyninst validate` without parsing text.

## Non-goals

- dyninst does not attach to anything. It produces and checks procedures.
- It does not manage a process lifecycle; process control belongs to the operator's tooling.
- It does not store evidence. Where a skill produces evidence, the skill says where to put it and
  what makes it tamper-evident; the repository does not implement a store.
