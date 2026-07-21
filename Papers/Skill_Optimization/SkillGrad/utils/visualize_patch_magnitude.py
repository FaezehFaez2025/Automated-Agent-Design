from __future__ import annotations

import argparse
import difflib
import re
from pathlib import Path

from plot_common import mean_std, method_name


WORD_RE = re.compile(r"\S+")


# ---------------------------------------------------------------------------
# 1. Diff consecutive skill snapshots
# ---------------------------------------------------------------------------

def collect_snapshot_dirs(train_dir: Path) -> list[Path]:
    """
    Ordered skill versions for consecutive diffs:
    [snapshot_iter_1, snapshot_iter_2, ..., final_skill].
    """
    snaps = []
    for p in train_dir.glob("snapshot_iter_*"):
        xlsx = p / "xlsx"
        if xlsx.is_dir():
            snaps.append((int(p.name.split("_")[-1]), xlsx))
    snaps.sort(key=lambda x: x[0])
    versions = [xlsx for _, xlsx in snaps]

    final = train_dir / "final_skill" / "xlsx"
    if final.is_dir() and versions:
        versions.append(final)
    return versions


