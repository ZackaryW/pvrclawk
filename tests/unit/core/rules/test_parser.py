import pytest

from pvrclawk.membank.core.rules.parser import parse_rule


def test_parse_rule_valid():
    parsed = parse_rule('if mood("tcp") < 0.3 then weight("tcp") -= 0.05')
    assert "predicate" in parsed
    assert "action" in parsed


def test_parse_rule_invalid():
    with pytest.raises(ValueError):
        parse_rule("invalid")
