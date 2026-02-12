import re


RULE_RE = re.compile(r"^if\s+(.+)\s+then\s+(.+)$")


def parse_rule(rule: str) -> dict[str, str]:
    match = RULE_RE.match(rule.strip())
    if not match:
        raise ValueError("Invalid DSL rule. Expected: if <predicate> then <action>")
    return {"predicate": match.group(1).strip(), "action": match.group(2).strip()}
