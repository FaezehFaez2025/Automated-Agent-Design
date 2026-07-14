"""
Momentum state dynamics (SkillGrad paper Figure 5 style)
=====================================================

Reads ``train/iter_*/momentum_memory.md`` (pattern record ``M_t``) and plots:

  * Cumulative patterns (purple line)
  * New patterns (red bars)
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


PATTERN_RE = re.compile(r"^###\s+(\S+)\s*\|", re.MULTILINE)


# ---------------------------------------------------------------------------
# 1. Data: read momentum memories and count patterns
# ---------------------------------------------------------------------------

def parse_pattern_slugs(memory_path: Path) -> set[str]:
    """Pattern ids from headings: ``### <id> | kind | description``."""
    text = memory_path.read_text(encoding="utf-8")
    return set(PATTERN_RE.findall(text))


def dynamics_for_run(run_dir: Path) -> dict[int, tuple[int, int]]:
    """
    {iteration: (cumulative, n_new)} for one run.

    Cumulative = |union of all pattern ids seen up to this iteration|
    (never decreases). New = ids that appear for the first time here.
    """
    train = run_dir / "train"
    iter_dirs = sorted(
        (p for p in train.glob("iter_*") if (p / "momentum_memory.md").exists()),
        key=lambda p: int(p.name.split("_")[1]),
    )
    if not iter_dirs:
        return {}

    ever_seen: set[str] = set()
    out: dict[int, tuple[int, int]] = {}
    for d in iter_dirs:
        iteration = int(d.name.split("_")[1])
        slugs = parse_pattern_slugs(d / "momentum_memory.md")
        new = slugs - ever_seen
        ever_seen |= slugs
        out[iteration] = (len(ever_seen), len(new))
    return out


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    mean = sum(values) / len(values)
    if len(values) == 1:
        return mean, 0.0
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, math.sqrt(var)


def method_name(run_id: str) -> str:
    rid = run_id.lower()
    if rid.startswith("foil") or "foil" in rid.split("_")[0]:
        return "Foil"
    if "skillgrad" in rid:
        return "SkillGrad"
    return run_id


def aggregate_runs(
    per_run: list[dict[int, tuple[int, int]]],
) -> tuple[list[int], list[float], list[float], list[float]]:
    """Average cumulative / new counts across seeds for each iteration."""
    iterations = sorted({it for d in per_run for it in d})
    mean_cum, std_cum, mean_new = [], [], []
    for it in iterations:
        cums = [float(d[it][0]) for d in per_run if it in d]
        news = [float(d[it][1]) for d in per_run if it in d]
        mc, sc = mean_std(cums)
        mn, _ = mean_std(news)
        mean_cum.append(mc)
        std_cum.append(sc)
        mean_new.append(mn)
    return iterations, mean_cum, std_cum, mean_new


