# utils/

All scripts are run from the **SkillGrad repo root**.

---

## Evaluation Results Explorer

Reads `eval_summary.json` produced by `bash scripts/eval.sh` and prints
the task IDs belonging to a chosen outcome group: tasks that passed,
tasks that were graded but incorrect, or tasks that never produced output.

**Script:** `eval_status.py`

### Task status groups

| Status | Meaning |
|--------|---------|
| `passed` | Agent produced `output.xlsx`; every graded cell matched the golden file exactly (`hard_score = 1.0`) |
| `failed` | Agent produced `output.xlsx`; grader ran but at least one cell was wrong (`hard_score = 0.0`) |
| `retry` | Agent never produced a gradable `output.xlsx` (API error, wrong path, max turns exceeded, etc.) |

### Usage

```bash
# passed tasks (default)
python utils/eval_status.py

# graded but wrong
python utils/eval_status.py --status failed

# no output produced
python utils/eval_status.py --status retry

# point to a different run
python utils/eval_status.py --summary results/runs/skillgrad_gpt-4.1/eval/eval_summary.json
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--summary` | `results/runs/skillgrad_gpt-5.4/eval/eval_summary.json` | Path to `eval_summary.json` |
| `--status` | `passed` | Which group to print: `passed`, `failed`, or `retry` |

---

## Evaluation Metrics Reporter

Reads `eval_summary.json` and prints a structured breakdown of all key metrics.

**Script:** `eval_metrics.py`

### Usage

```bash
# default run
python utils/eval_metrics.py

# point to a different run
python utils/eval_metrics.py --summary results/runs/skillgrad_gpt-4.1/eval/eval_summary.json
```