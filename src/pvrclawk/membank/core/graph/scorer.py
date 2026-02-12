from pvrclawk.membank.models.config import AppConfig
from pvrclawk.membank.models.link import Link


class VectorScorer:
    def __init__(self, config: AppConfig):
        self.config = config

    def compute_decay(self, link_frequency: int, total_frequency: int) -> float:
        if total_frequency <= 0:
            return 0.0
        ratio = float(link_frequency) / float(total_frequency)
        if ratio < 0.0:
            return 0.0
        if ratio > 1.0:
            return 1.0
        return ratio

    def score_link(
        self,
        link: Link,
        query_tags: list[str],
        total_frequency: int,
        mood_factor: float = 1.0,
        rule_adjustment: float = 1.0,
    ) -> float:
        tag_match = 1.0 if any(tag in query_tags for tag in link.tags) else 0.0
        if tag_match == 0.0:
            return 0.0
        freq_decay = self.compute_decay(link.usage_count, total_frequency)
        return tag_match * link.weight * link.decay * freq_decay * mood_factor * rule_adjustment
