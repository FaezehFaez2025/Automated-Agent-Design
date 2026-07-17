import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval_metrics import extract_metrics
from plot_common import mean_std

# Metrics to aggregate, with display formatting: (key, label, is_percent).
METRICS = [
    ("hard_full", "Hard accuracy (full set)", True),
    ("cell_full", "Cell accuracy (full set)", True),
    ("hard_graded", "Hard accuracy (graded)", True),
    ("cell_graded", "Cell accuracy (graded)", True),
    ("n_passed", "Passed tasks", False),
    ("n_graded", "Graded tasks", False),
    ("n_retry", "Retry needed", False),
    ("cost_usd", "API cost ($)", False),
    ("elapsed_s", "Wall time (s)", False),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate eval metrics across runs.")
    parser.add_argument("--runs", nargs="+", required=True,
                        help="Run folder names under results/runs/.")
    parser.add_argument("--runs-root", type=Path, default=Path("results/runs"),
                        help="Directory that contains run folders (default: results/runs).")
    args = parser.parse_args()

    per_run: list[tuple[str, dict]] = []
    for run_id in args.runs:
        summary = args.runs_root / run_id / "eval" / "eval_summary.json"
        if not summary.exists():
            print(f"  [skip] {run_id}: no eval_summary.json at {summary}")
            continue
        per_run.append((run_id, extract_metrics(summary)))

    if not per_run:
        raise SystemExit("No usable runs (no eval_summary.json found).")

    print(f"\n{'=' * 66}")
    print(f"  Aggregate over {len(per_run)} run(s): "
          f"{', '.join(rid for rid, _ in per_run)}")
    print(f"{'=' * 66}")

    print(f"\n  {'METRIC':<28} {'MEAN':>12} {'STD':>12}")
    print(f"  {'-' * 54}")
    for key, label, is_pct in METRICS:
        values = [m[key] for _, m in per_run]
        mean, std = mean_std(values)
        if is_pct:
            print(f"  {label:<28} {mean:>11.1%} {std:>11.1%}")
        else:
            print(f"  {label:<28} {mean:>12.2f} {std:>12.2f}")

    # Per-run headline for reference.
    print(f"\n  {'PER-RUN hard accuracy (full set)':<40}")
    for rid, m in per_run:
        print(f"    {rid:<36} {m['hard_full']:>7.1%}")
    print()


if __name__ == "__main__":
    main()
