from collections import defaultdict

import networkx as nx

from pvrclawk.membank.core.graph.scorer import VectorScorer
from pvrclawk.membank.models.base import BaseNode
from pvrclawk.membank.models.link import Link


class GraphEngine:
    def __init__(self, scorer: VectorScorer):
        self.scorer = scorer

    def retrieve(
        self,
        nodes: list[BaseNode],
        links: list[Link],
        query_tags: list[str],
        limit: int = 5,
    ) -> list[tuple[str, float]]:
        node_by_uid = {n.uid: n for n in nodes}
        g = nx.Graph()
        for uid in node_by_uid:
            g.add_node(uid)
        for link in links:
            g.add_edge(link.source, link.target, weight=link.weight)

        # Phase 1: Direct tag match on nodes themselves
        scores: dict[str, float] = defaultdict(float)
        for node in nodes:
            node_tags = set(node.tags.keys()) if isinstance(node.tags, dict) else set()
            overlap = node_tags & set(query_tags)
            if overlap:
                # Sum the tag weights for matching tags
                direct_score = sum(node.tags.get(t, 0.0) for t in overlap)
                scores[node.uid] += direct_score

        # Phase 2: Link-based scoring (existing logic)
        total_frequency = sum(max(l.usage_count, 0) for l in links)
        for link in links:
            scores[link.target] += self.scorer.score_link(link, query_tags, total_frequency=total_frequency)

        # Phase 3: Rank and expand 1-hop neighbors
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        expanded = dict(ranked)
        for uid, score in ranked:
            if uid in g:
                for neighbor in g.neighbors(uid):
                    expanded[neighbor] = max(expanded.get(neighbor, 0.0), score * 0.5)

        return sorted(expanded.items(), key=lambda x: x[1], reverse=True)[:limit]
