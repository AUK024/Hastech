from pydantic import BaseModel, ConfigDict


class BlockedSenderRuleBase(BaseModel):
    rule_type: str
    rule_value: str
    description: str | None = None
    is_active: bool = True


class BlockedSenderRuleCreate(BlockedSenderRuleBase):
    pass


class BlockedSenderRuleUpdate(BaseModel):
    rule_type: str | None = None
    rule_value: str | None = None
    description: str | None = None
    is_active: bool | None = None


class BlockedSenderRuleRead(BlockedSenderRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
