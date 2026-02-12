from pvrclawk.membank.core.rules.engine import RuleEngine


def test_rule_validate():
    engine = RuleEngine(['if tag("tcp") then weight("tcp") += 0.1'])
    engine.validate()


def test_rule_multiplier_changes():
    engine = RuleEngine(['if tag("tcp") then weight("tcp") += 0.1'])
    mul = engine.evaluate_multiplier(["tcp"], {})
    assert mul > 1.0
