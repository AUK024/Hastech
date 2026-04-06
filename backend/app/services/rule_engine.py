import re
from app.models.blocked_sender_rule import BlockedSenderRule


class RuleEngineService:
    """Config-driven sender filtering and business rule checks."""

    def is_sender_blocked(self, sender_email: str, rules: list[BlockedSenderRule]) -> bool:
        email = sender_email.lower()
        for rule in rules:
            if not rule.is_active:
                continue
            rule_type = rule.rule_type.lower()
            value = rule.rule_value.lower()
            if rule_type == 'exact_email' and email == value:
                return True
            if rule_type == 'domain' and email.endswith(f'@{value.lstrip("@")}'):
                return True
            if rule_type in {'contains', 'pattern'} and value in email:
                return True
            if rule_type in {'regex', 'no_reply', 'auto_generated', 'daemon'} and re.search(value, email):
                return True
        return False
