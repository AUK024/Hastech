from types import SimpleNamespace
from app.services.rule_engine import RuleEngineService


def test_rule_engine_blocks_domain() -> None:
    rules = [SimpleNamespace(rule_type='domain', rule_value='example.com', is_active=True)]
    assert RuleEngineService().is_sender_blocked('a@example.com', rules) is True


def test_rule_engine_blocks_contains() -> None:
    rules = [SimpleNamespace(rule_type='contains', rule_value='no-reply', is_active=True)]
    assert RuleEngineService().is_sender_blocked('no-reply@vendor.com', rules) is True
