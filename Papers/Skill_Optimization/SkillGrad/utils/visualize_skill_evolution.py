from __future__ import annotations

import argparse
import re
from pathlib import Path


def collect_versions(train_dir: Path) -> list[tuple[str, Path]]:
    """Ordered (label, path): seed, iter 1, ..., final."""
    versions: list[tuple[int, str, Path]] = []
    for p in train_dir.glob("SKILL.md.iter_*"):
        m = re.fullmatch(r"SKILL\.md\.iter_(\d+)", p.name)
        if not m:
            continue  # skip stray files like SKILL.md.iter_0_
        n = int(m.group(1))
        versions.append((n, "seed" if n == 0 else f"iter {n}", p))
    versions.sort(key=lambda x: x[0])
    out = [(lbl, p) for _, lbl, p in versions]
    final = train_dir / "final_skill" / "xlsx" / "SKILL.md"
    if final.exists():
        out.append(("final", final))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", default="skillgrad_gpt-5.4")
    ap.add_argument("--embedder", default="all-MiniLM-L6-v2",
                    help="SentenceTransformer model name.")
    args = ap.parse_args()

    train_dir = Path("results") / "runs" / args.run_id / "train"
    out = Path("results/skill_evolution.png")

    versions = collect_versions(train_dir)
    if len(versions) < 2:
        raise SystemExit(f"Need >=2 skill versions, found {len(versions)} in "
                         f"{train_dir}. Run training with >=1 patch first.")
    labels = [lbl for lbl, _ in versions]
    print(f"  {len(versions)} versions: {', '.join(labels)}")

    from sentence_transformers import SentenceTransformer

    texts = [p.read_text(encoding="utf-8") for _, p in versions]
    model = SentenceTransformer(args.embedder)
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    from sklearn.decomposition import PCA
    xy = PCA(n_components=2, random_state=0).fit_transform(vecs)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot(xy[:, 0], xy[:, 1], "-", color="#1f77b4", lw=1.8, alpha=0.8, zorder=2)
    for i in range(1, len(versions)):
        ax.annotate("", xy=xy[i], xytext=xy[i - 1],
                    arrowprops=dict(arrowstyle="-|>", color="#1f77b4", lw=1.8,
                                    shrinkA=8, shrinkB=8), zorder=2)
    for i, lbl in enumerate(labels):
        color = "#9467bd" if i == 0 else "#ff7f0e" if i == len(labels) - 1 else "#1f77b4"
        marker = "*" if i in (0, len(labels) - 1) else "o"
        size = 300 if marker == "*" else 150
        ax.scatter(*xy[i], c=color, s=size, marker=marker,
                   edgecolors="black", linewidths=0.7, zorder=3)
        ax.annotate(lbl, xy[i], fontsize=9, fontweight="bold", color="#10456e",
                    xytext=(7, 6), textcoords="offset points", zorder=4)

    ax.set_title(f"Skill embedding trajectory — {args.run_id}\n"
                 f"arrow = one patch; {len(versions)} versions | PCA", fontsize=11)
    ax.set_xlabel("PCA-1")
    ax.set_ylabel("PCA-2")
    ax.grid(True, ls=":", alpha=0.3)
    fig.tight_layout()

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    print(f"\n  Saved → {out}")


if __name__ == "__main__":
    main()
