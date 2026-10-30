"""CLI entry point for dyninst."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .corpus import BY_SLUG, PACK, SKILLS
from .render import build_pack, render_catalog, render_skill, word_count
from .validate import (
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_WORDS,
    validate_pack,
)

ROOT = Path(__file__).resolve().parents[2]
VERSION = PACK["version"]

USAGE = """\
dyninst - dynamic-instrumentation skills

Usage: dyninst <command> [options]

Commands:
  validate [--json]   Check every skill against the corpus rules
  list [--phase P]    List skills, optionally filtered by phase
  show SLUG           Print one rendered SKILL.md
  render              Write skills/<slug>/SKILL.md for every skill
  catalog             Write results/catalog.md
  build               Write the whole pack (skills, pack.json, catalog)
  --version           Print the version
"""


def _cmd_validate(args: list[str]) -> int:
    issues = validate_pack(PACK, SKILLS)
    if "--json" in args:
        payload = {
            "pack": PACK["name"],
            "version": VERSION,
            "expected": PACK["expected_skills"],
            "valid": len(SKILLS) - len({i.split(":")[0] for i in issues}),
            "total": len(SKILLS),
            "passed": not issues,
            "floors": {
                "min_steps": MIN_STEPS,
                "min_signals": MIN_SIGNALS,
                "min_patterns": MIN_PATTERNS,
                "min_pitfalls": MIN_PITFALLS,
                "min_words": MIN_WORDS,
            },
            "issues": issues,
        }
        print(json.dumps(payload, indent=2))
        return 0 if not issues else 1

    if issues:
        for issue in issues:
            print(f"  ISSUE: {issue}")
        print(f"{len(SKILLS) - len({i.split(':')[0] for i in issues})}/{len(SKILLS)} skills valid")
        return 1
    print(f"{len(SKILLS)}/{len(SKILLS)} skills valid")
    return 0


def _cmd_list(args: list[str]) -> int:
    phase = None
    if "--phase" in args:
        index = args.index("--phase")
        if index + 1 < len(args):
            phase = args[index + 1]
    rows = [s for s in SKILLS if phase is None or s.meta_get("phase") == phase]
    for skill in sorted(rows, key=lambda s: s.slug):
        print(f"{skill.slug:34s} {skill.meta_get('phase'):12s} {skill.title}")
    print(f"{len(rows)} skill(s)")
    return 0


def _cmd_show(args: list[str]) -> int:
    if not args:
        print("usage: dyninst show SLUG", file=sys.stderr)
        return 2
    skill = BY_SLUG.get(args[0])
    if skill is None:
        print(f"unknown slug: {args[0]}", file=sys.stderr)
        return 2
    print(render_skill(PACK, skill), end="")
    return 0


def _cmd_render() -> int:
    files = build_pack(ROOT, PACK, SKILLS)
    rendered = sum(1 for rel in files if rel.startswith("skills/"))
    print(f"Rendered {rendered} skills to {ROOT / 'skills'}")
    return 0


def _cmd_catalog() -> int:
    path = ROOT / "results" / "catalog.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_catalog(PACK, SKILLS), encoding="utf-8")
    print(f"Catalog written to {path}")
    return 0


def _cmd_build() -> int:
    files = build_pack(ROOT, PACK, SKILLS)
    words = sum(word_count(text) for rel, text in files.items() if rel.startswith("skills/"))
    print(f"Built {len(files)} artifacts, {words} rendered skill words")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args or args[0] in {"-h", "--help", "help"}:
        print(USAGE, end="")
        return 0
    if args[0] in {"--version", "-V"}:
        print(f"dyninst {VERSION}")
        return 0

    command, rest = args[0], args[1:]

    if command == "validate":
        return _cmd_validate(rest)
    if command == "list":
        return _cmd_list(rest)
    if command == "show":
        return _cmd_show(rest)
    if command == "render":
        return _cmd_render()
    if command == "catalog":
        return _cmd_catalog()
    if command == "build":
        return _cmd_build()

    print(f"Unknown command: {command}", file=sys.stderr)
    print(USAGE, end="", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())