"""Print task IDs that passed (hard_score == 1.0) from an eval summary."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Print passed/failed task IDs from eval_summary.json")
    parser.add_argument(
        "--summary",
        default="results/runs/skillgrad_gpt-5.4/eval/eval_summary.json",
        help="Path to eval_summary.json",
    )
    parser.add_argument(
        "--status",
        choices=["passed", "failed", "retry"],
        default="passed",
        help="Which tasks to print: passed (hard=1), failed (hard=0, graded), retry (no output)",
    )
    args = parser.parse_args()

    path = Path(args.summary)
    if not path.exists():
        raise FileNotFoundError(f"Summary not found: {path}")

    with open(path) as f:
        data = json.load(f)

    results = data["results"]
    total = data["total"]

    if args.status == "passed":
        subset = [r for r in results if r.get("hard_score") == 1.0]
    elif args.status == "failed":
        subset = [r for r in results if r.get("status") == "graded" and r.get("hard_score", 1.0) < 1.0]
    else:  # retry
        subset = [r for r in results if r.get("status") == "retry_needed"]

    print(f"Status: {args.status} — {len(subset)} / {total}\n")
    for r in subset:
        print(r["id"])


if __name__ == "__main__":
    main()
