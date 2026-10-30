"""dyninst corpus: pack metadata plus 50 authored instrumentation skills.

Skills are authored as plain dicts in ``part1``..``part3`` and loaded once
into the validated :class:`~dyninst.model.Skill` shape.
"""

from __future__ import annotations

from typing import Any

from ..model import skill_from_dict
from .part1 import SKILLS as PART1
from .part2 import SKILLS as PART2
from .part3 import SKILLS as PART3

PACK: dict[str, Any] = {
    "name": "dyninst",
    "version": "1.0.0",
    "category": "dynamic-instrumentation",
    "license": "MIT",
    "runtime": "Claude Code, opencode, or any agent runtime that loads SKILL.md files",
    "description": (
        "50 validated skills for instrumenting a live target: Frida, GDB, "
        "LD_PRELOAD and eBPF probes, post-mortem capture, teardown that leaves "
        "no traces, and scope checks that refuse out-of-bounds work."
    ),
    "expected_skills": 50,
}

SKILLS: list[Any] = [skill_from_dict(raw) for raw in (*PART1, *PART2, *PART3)]
BY_SLUG: dict[str, Any] = {skill.slug: skill for skill in SKILLS}

__all__ = ["PACK", "SKILLS", "BY_SLUG"]