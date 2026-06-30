import argparse
import json
from pathlib import Path


def extract_metrics(summary_path: Path) -> dict:
    with open(summary_path) as f:
        data = json.load(f)

    agg = data["aggregate"]
    cost = data.get("cost", {}).get("total", {})
    results = data["results"]
    total = data["total"]

    passed = [r for r in results if r.get("hard_score") == 1.0]
    failed = [r for r in results if r.get("status") == "graded"
              and r.get("hard_score", 1.0) < 1.0]
    retry  = [r for r in results if r.get("status") == "retry_needed"]
    graded = passed + failed

    return {
        "total":         total,
        "n_graded":      len(graded),
        "n_passed":      len(passed),
        "n_failed":      len(failed),
        "n_retry":       len(retry),
        "hard_graded":   len(passed) / len(graded) if graded else 0.0,
        "cell_graded":   agg.get("mean_cell_graded", 0.0),
        "hard_full":     len(passed) / total if total else 0.0,
        "cell_full":     agg.get("mean_cell_accuracy", 0.0),
        "cost_usd":      cost.get("cost", 0.0),
        "elapsed_s":     data.get("elapsed", 0.0),
    }


def _bar(value: float, width: int = 20) -> str:
    filled = round(value * width)
    return "█" * filled + "░" * (width - filled)


def print_report(m: dict, summary_path: Path) -> None:
    total = m["total"]
    print(f"\n{'═' * 58}")
    print(f"  {summary_path}")
    print(f"{'═' * 58}")

    print(f"\n  {'COVERAGE':─<50}")
    print(f"  {'Graded':<28} {m['n_graded']:>4} / {total}")
    print(f"  {'  Passed':<28} {m['n_passed']:>4} / {total}")
    print(f"  {'  Failed (graded, wrong)':<28} {m['n_failed']:>4} / {total}")
    print(f"  {'  Retry needed':<28} {m['n_retry']:>4} / {total}")

    print(f"\n  {'QUALITY — graded tasks only':─<50}")
    print(f"  {'Hard accuracy':<28} {m['hard_graded']:>7.1%}  {_bar(m['hard_graded'])}")
    print(f"  {'Cell accuracy':<28} {m['cell_graded']:>7.1%}  {_bar(m['cell_graded'])}")

    print(f"\n  {'QUALITY — full ' + str(total) + '-task set':─<50}")
    print(f"  {'Hard accuracy':<28} {m['hard_full']:>7.1%}  {_bar(m['hard_full'])}")
    print(f"  {'Cell accuracy':<28} {m['cell_full']:>7.1%}  {_bar(m['cell_full'])}")

    print(f"\n  {'COST / EFFICIENCY':─<50}")
    print(f"  {'API cost':<28} ${m['cost_usd']:.4f}")
    print(f"  {'Wall time':<28} {m['elapsed_s']:.0f}s  ({m['elapsed_s'] / 60:.1f} min)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Compute evaluation metrics from eval_summary.json.",
    )
    parser.add_argument(
        "--summary",
        default="results/runs/skillgrad_gpt-5.4/eval/eval_summary.json",
        help="Path to eval_summary.json.",
    )
    args = parser.parse_args()

    path = Path(args.summary)
    print_report(extract_metrics(path), path)


if __name__ == "__main__":
    main()
