"""Shared helpers for the SkillGrad plotting utilities."""

from __future__ import annotations

import math


def method_name(run_id: str) -> str:
    """Map a run folder name to a short method label (SkillGrad / Foil)."""
    rid = run_id.lower()
    if rid.startswith("foil") or "foil" in rid.split("_")[0]:
        return "Foil"
    if "skillgrad" in rid:
        return "SkillGrad"
    return run_id


def mean_std(values: list[float]) -> tuple[float, float]:
    """Population mean and std of a list (std=0 for a single value)."""
    if not values:
        return float("nan"), float("nan")
    mean = sum(values) / len(values)
    if len(values) == 1:
        return mean, 0.0
    var = sum((v - mean) ** 2 for v in values) / len(values)
    return mean, math.sqrt(var)
