from pvrclawk.membank.core.rules.parser import parse_rule


class RuleEngine:
    def __init__(self, rules: list[str]):
        self.rules = rules

    def validate(self) -> None:
        for rule in self.rules:
            parse_rule(rule)

    def evaluate_multiplier(self, query_tags: list[str], mood: dict[str, float]) -> float:
        multiplier = 1.0
        for raw in self.rules:
            parsed = parse_rule(raw)
            pred = parsed["predicate"]
            action = parsed["action"]
            if "tag(" in pred:
                found = any(f'tag("{tag}")' in pred for tag in query_tags)
                if not found:
                    continue
            if "weight" in action and "+=" in action:
                multiplier += float(action.split("+=", 1)[1].strip())
            elif "weight" in action and "-=" in action:
                multiplier -= float(action.split("-=", 1)[1].strip())
        return max(multiplier, 0.0)
