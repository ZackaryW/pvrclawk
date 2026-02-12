import re

from pvrclawk.membank.models.index import IndexData


def _slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def derive_cluster_name(tags: dict[str, float]) -> str:
    ordered = sorted(tags.items(), key=lambda x: x[1], reverse=True)
    top = [_slug(name) for name, _ in ordered[:2] if _slug(name)]
    return "_".join(top) if top else "_inbox"


def select_best_cluster(index: IndexData, tags: dict[str, float]) -> str:
    best_name = "_inbox"
    best_score = 0.0
    for name, meta in index.clusters.items():
        score = 0.0
        for tag in meta.top_tags:
            score += tags.get(tag, 0.0)
        if score > best_score:
            best_name = name
            best_score = score
    return best_name
