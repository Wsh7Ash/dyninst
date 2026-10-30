"""dyninst: dynamic-instrumentation tooling for Frida, GDB, LD_PRELOAD and eBPF."""

from __future__ import annotations

from .cli import main
from .model import Skill, skill_from_dict
from .render import (
    build_pack,
    render_catalog,
    render_description,
    render_skill,
    sha256_of,
    word_count,
)
from .validate import (
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_WORDS,
    validate_pack,
    validate_skill,
)

__all__ = [
    "main",
    "Skill",
    "skill_from_dict",
    "build_pack",
    "render_catalog",
    "render_description",
    "render_skill",
    "sha256_of",
    "word_count",
    "validate_pack",
    "validate_skill",
    "MIN_STEPS",
    "MIN_SIGNALS",
    "MIN_PATTERNS",
    "MIN_PITFALLS",
    "MIN_WORDS",
]