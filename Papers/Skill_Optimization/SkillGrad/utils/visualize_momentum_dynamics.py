"""
Momentum state dynamics (SkillGrad paper Figure 5 style)
=====================================================

Reads ``train/iter_*/momentum_memory.md`` (pattern record ``M_t``) and plots:

  * Cumulative patterns (purple line)
  * New patterns (red bars)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from plot_common import mean_std, method_name


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


def aggregate_runs(
    per_run: list[dict[int, tuple[int, int]]],
) -> tuple[list[int], list[float], list[float], list[float]]:
    """Average cumulative / new counts across seeds for each iteration."""
    all_iters = {it for d in per_run for it in d}
    iterations = list(range(min(all_iters), max(all_iters) + 1)) if all_iters else []
    mean_cum, std_cum, mean_new = [], [], []
    for it in iterations:
        cums, news = [], []
        for d in per_run:
            # Forward-fill: cumulative at the latest iteration ≤ it.
            prior_iters = [i for i in d if i <= it]
            cums.append(float(d[max(prior_iters)][0]) if prior_iters else 0.0)
            news.append(float(d[it][1]) if it in d else 0.0)
        mc, sc = mean_std(cums)
        mn, _ = mean_std(news)
        mean_cum.append(mc)
        std_cum.append(sc)
        mean_new.append(mn)
    return iterations, mean_cum, std_cum, mean_new


# ---------------------------------------------------------------------------
# 2. Plotting only
# ---------------------------------------------------------------------------

def plot_momentum_dynamics(
    iterations: list[int],
    mean_cum: list[float],
    std_cum: list[float],
    mean_new: list[float],
    *,
    method: str,
    n_seeds: int,
    out: Path,
) -> None:
    """Draw the dual-axis momentum chart and save it to ``out``."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    purple = "#7b6bb0"
    purple_band = "#b8a9d4"
    red = "#f4a3a0"

    fig, ax_cum = plt.subplots(figsize=(8.0, 4.2))
    ax_new = ax_cum.twinx()
    xs = list(range(len(iterations)))

    # Red bars: new patterns (right axis).
    ax_new.bar(
        xs, mean_new, width=0.55, color=red, edgecolor="#de7068",
        alpha=0.85, label="New patterns", zorder=1,
    )

    # Purple band around the cumulative line.
    # ≥2 seeds → ±1 std; 1 seed → thin illustrative band (layout only).
    if n_seeds > 1:
        lo = [m - s for m, s in zip(mean_cum, std_cum)]
        hi = [m + s for m, s in zip(mean_cum, std_cum)]
        band_note = "±1 std across seeds"
    else:
        half = 0.45
        lo = [max(0.0, m - half) for m in mean_cum]
        hi = [m + half for m in mean_cum]
        band_note = "illustrative band (1 seed)"
        print(
            "  Note: shaded band is illustrative with a single seed. "
            "Pass multiple --runs (paper: 3 seeds) for a real ±std band."
        )

    ax_cum.fill_between(
        xs, lo, hi, color=purple_band, alpha=0.45, zorder=2, linewidth=0,
    )

    # Purple line: cumulative patterns (left axis).
    ax_cum.plot(
        xs, mean_cum, color=purple, lw=2.2, zorder=3,
        marker="o", markersize=7,
        markerfacecolor="white", markeredgecolor=purple, markeredgewidth=1.8,
        label="Cumulative patterns",
    )

    ax_cum.set_xlabel("Iteration")
    ax_cum.set_ylabel("Cumulative patterns", color=purple)
    ax_new.set_ylabel("New patterns", color="#c45c55")
    ax_cum.tick_params(axis="y", colors=purple)
    ax_new.tick_params(axis="y", colors="#c45c55")
    ax_cum.set_xticks(xs)
    ax_cum.set_xticklabels([str(it) for it in iterations])

    # Use the SAME numeric y-limits on both axes so a bar of height 3
    # lines up with "3" on the left axis too (avoids dual-axis optical illusion).
    y_max = max(
        max(hi) if hi else 0.0,
        max(mean_new) if mean_new else 0.0,
        1.0,
    ) * 1.25
    ax_cum.set_ylim(0, y_max)
    ax_new.set_ylim(0, y_max)

    # Label each bar with its count so the value is unambiguous.
    for x, val in zip(xs, mean_new):
        if val > 0:
            ax_new.text(
                x, val + y_max * 0.02, f"{val:g}",
                ha="center", va="bottom", fontsize=8, color="#c45c55",
            )

    ax_cum.set_title(f"Momentum state dynamics — {method}")
    ax_cum.grid(True, axis="y", ls=":", alpha=0.35)
    ax_cum.spines["top"].set_visible(False)
    ax_new.spines["top"].set_visible(False)

    h1, l1 = ax_cum.get_legend_handles_labels()
    h2, l2 = ax_new.get_legend_handles_labels()
    band_proxy = Patch(
        facecolor=purple_band, alpha=0.45, edgecolor="none",
        label=f"Band ({band_note})",
    )
    ax_cum.legend(
        h1 + h2 + [band_proxy],
        l1 + l2 + [f"Band ({band_note})"],
        frameon=False, loc="upper left",
    )

    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160, bbox_inches="tight")
    print(f"  Saved → {out}")


# ---------------------------------------------------------------------------
# 3. CLI: load data, then call the plotter
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Plot momentum pattern dynamics.")
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path("results/runs"),
        help="Directory that contains run folders (default: results/runs).",
    )
    parser.add_argument("--runs", nargs="+", help="Run folder names under results/runs/.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/momentum_dynamics.png"),
    )
    args = parser.parse_args()

    if not args.runs:
        raise SystemExit("Pass at least one folder with --runs FOLDER [FOLDER ...]")

    missing = [name for name in args.runs if not (args.runs_root / name).is_dir()]
    if missing:
        raise SystemExit(f"Unknown run folder(s) under {args.runs_root}: {missing}")

    # --- load each requested folder ---
    per_run: list[dict[int, tuple[int, int]]] = []
    used_ids: list[str] = []
    for folder in args.runs:
        dyn = dynamics_for_run(args.runs_root / folder)
        if not dyn:
            print(f"  [skip] {folder}: no momentum_memory.md found")
            continue
        print(f"  {method_name(folder)} ({folder}):")
        for it in sorted(dyn):
            cum, new = dyn[it]
            print(f"    iter {it:>2}: cumulative={cum}  new={new}")
        per_run.append(dyn)
        used_ids.append(folder)

    if not per_run:
        raise SystemExit("No usable runs (none had momentum_memory.md).")

    # --- aggregate across the selected folders ---
    method = " / ".join(dict.fromkeys(method_name(r) for r in used_ids))
    iterations, mean_cum, std_cum, mean_new = aggregate_runs(per_run)

    # --- plot ---
    plot_momentum_dynamics(
        iterations, mean_cum, std_cum, mean_new,
        method=method,
        n_seeds=len(per_run),
        out=args.out,
    )


if __name__ == "__main__":
    main()
