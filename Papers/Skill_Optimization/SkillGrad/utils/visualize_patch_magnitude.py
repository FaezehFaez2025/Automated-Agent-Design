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


def list_skill_files(xlsx_dir: Path) -> dict[str, Path]:
    """Map relative path -> absolute path for every file under xlsx/."""
    files = {}
    if not xlsx_dir.is_dir():
        return files
    for path in xlsx_dir.rglob("*"):
        if path.is_file():
            files[str(path.relative_to(xlsx_dir))] = path
    return files


def file_words(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    return WORD_RE.findall(text)


def word_diff(before: list[str], after: list[str]) -> tuple[int, int]:
    """Return (n_added, n_removed) via SequenceMatcher opcodes."""
    added = removed = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        a=before, b=after, autojunk=False
    ).get_opcodes():
        if tag == "insert":
            added += j2 - j1
        elif tag == "delete":
            removed += i2 - i1
        elif tag == "replace":
            removed += i2 - i1
            added += j2 - j1
    return added, removed


def diff_skill_trees(before_dir: Path, after_dir: Path) -> tuple[int, int]:
    """Diff two xlsx/ trees file-by-file; sum added / removed words."""
    before_files = list_skill_files(before_dir)
    after_files = list_skill_files(after_dir)
    total_added = total_removed = 0
    for key in set(before_files) | set(after_files):
        before_w = file_words(before_files[key]) if key in before_files else []
        after_w = file_words(after_files[key]) if key in after_files else []
        a, r = word_diff(before_w, after_w)
        total_added += a
        total_removed += r
    return total_added, total_removed


def patch_magnitudes_for_run(run_dir: Path) -> dict[int, tuple[int, int]]:
    """{iteration: (added, removed)} for one run (1-indexed)."""
    versions = collect_snapshot_dirs(run_dir / "train")
    if len(versions) < 2:
        return {}
    out = {}
    for i in range(len(versions) - 1):
        out[i + 1] = diff_skill_trees(versions[i], versions[i + 1])
    return out


