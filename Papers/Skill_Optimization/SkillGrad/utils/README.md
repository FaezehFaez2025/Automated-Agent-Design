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

---

## Skill Evolution Visualizer

Embeds every saved version of the skill (`SKILL.md.iter_0` … `SKILL.md.iter_N`,
plus `final_skill/xlsx/SKILL.md`) with a sentence-transformer, projects the
embeddings to 2D with PCA, and plots the trajectory as a sequence of connected
points — one point per skill version, one arrow per patch between consecutive
versions — so you can see how much (and in what direction) each training
iteration moved the skill.

**Script:** `visualize_skill_evolution.py`

### Requirements

```bash
pip install sentence-transformers scikit-learn matplotlib
```

### Usage

```bash
# default run
python utils/visualize_skill_evolution.py

# specify a run id
python utils/visualize_skill_evolution.py --run-id skillgrad_gpt-4.1

# use a different embedding model
python utils/visualize_skill_evolution.py --embedder all-mpnet-base-v2
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--run-id` | `skillgrad_gpt-5.4` | Run folder under `results/runs/<run-id>/train/` |
| `--embedder` | `all-MiniLM-L6-v2` | SentenceTransformer model name used to embed each `SKILL.md` version |

### Input

Reads from `results/runs/<run-id>/train/`:
- `SKILL.md.iter_0` (seed skill), `SKILL.md.iter_1`, `SKILL.md.iter_2`, … (one per training iteration)
- `final_skill/xlsx/SKILL.md` (final patched skill, if present)

Requires at least 2 versions to plot; raises an error otherwise.

### Output

Saves a PNG to `results/skill_evolution.png`.

---

## Momentum Dynamics Visualizer

Plots cumulative / new pattern counts from `train/iter_*/momentum_memory.md`
(SkillGrad paper Fig. 5 style). Pass one or more folder names under
`results/runs/`; multiple folders are averaged (shaded ±std band).

**Script:** `visualize_momentum_dynamics.py`

### Usage

```bash
python3 utils/visualize_momentum_dynamics.py \
  --runs skillgrad_gpt-5.4 \
  --out results/momentum_dynamics_skillgrad.png

python3 utils/visualize_momentum_dynamics.py \
  --runs foil_gpt-5.4 \
  --out results/momentum_dynamics_foil.png

# average several seeds
python3 utils/visualize_momentum_dynamics.py \
  --runs seed_a seed_b seed_c \
  --out results/momentum_dynamics.png
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--runs` | (required) | Folder name(s) under `results/runs/` |
| `--runs-root` | `results/runs` | Parent directory of run folders |
| `--out` | `results/momentum_dynamics.png` | Output PNG path |