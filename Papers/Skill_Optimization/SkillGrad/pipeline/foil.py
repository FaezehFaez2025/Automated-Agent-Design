"""Foil: similarity-based foil retrieval for SkillGrad diagnosis."""

from pathlib import Path
from typing import Optional


EMBEDDING_MODEL = "text-embedding-3-small"


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class FoilIndex:
    """Embedding index over S0-passing tasks for foil retrieval."""

    def __init__(
        self,
        candidate_ids: list[str],
        id_to_instruction: dict[str, str],
        async_openai_client,
    ) -> None:
        self.candidate_ids = [
            tid for tid in candidate_ids if tid in id_to_instruction
        ]
        self.id_to_instruction = id_to_instruction
        self._client = async_openai_client
        self._embeddings: dict[str, list[float]] = {}

    async def build(self) -> None:
        """Embed all candidates once at the start of a run."""
        print(f"  [foil] Embedding {len(self.candidate_ids)} candidate task(s) ...")
        texts = [self.id_to_instruction[tid] for tid in self.candidate_ids]
        response = await self._client.embeddings.create(
            input=texts, model=EMBEDDING_MODEL,
        )
        for item in response.data:
            self._embeddings[self.candidate_ids[item.index]] = item.embedding

    async def embed_text(self, text: str) -> list[float]:
        """Embed a single text string."""
        response = await self._client.embeddings.create(
            input=[text], model=EMBEDDING_MODEL,
        )
        return response.data[0].embedding

    def rank_candidates(
        self,
        query_embedding: list[float],
        exclude_id: str,
    ) -> list[str]:
        """Candidate IDs sorted by cosine similarity to query (descending)."""
        scored = [
            (_cosine(query_embedding, self._embeddings[tid]), tid)
            for tid in self.candidate_ids
            if tid != exclude_id
        ]
        scored.sort(reverse=True)
        return [tid for _, tid in scored]


async def find_foil(
    failed_assessment: dict,
    foil_index: FoilIndex,
    dataset: list[dict],
    id_to_idx: dict[str, int],
    base_trajectories_dir: Path,
) -> Optional[dict]:
    """Return the most similar S0-passing task and its base trajectory."""
    failed_id = failed_assessment["id"]
    query_emb = await foil_index.embed_text(
        failed_assessment["example"]["instruction"],
    )
    ranked = foil_index.rank_candidates(query_emb, failed_id)

    base_dir = Path(base_trajectories_dir)
    for candidate_id in ranked:
        if candidate_id not in id_to_idx:
            continue
        base_trace = base_dir / candidate_id / "trace.jsonl"
        if not base_trace.exists():
            continue
        return {
            "id": candidate_id,
            "example": dataset[id_to_idx[candidate_id]],
            "merged_trace_path": str(base_trace),
        }

    print(f"  [foil] No foil found for {failed_id}")
    return None
