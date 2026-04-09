from sqlalchemy import select
from app.models.blocked_sender_rule import BlockedSenderRule
from app.repositories.base import RepositoryBase
from app.schemas.blocked_sender_rule import BlockedSenderRuleCreate, BlockedSenderRuleUpdate


class BlockedRuleRepository(RepositoryBase):
    def list(self, tenant_code: str = 'default') -> list[BlockedSenderRule]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(BlockedSenderRule)
            .where(BlockedSenderRule.tenant_code == normalized_tenant)
            .order_by(BlockedSenderRule.id.desc())
        ).all()

    def get(self, rule_id: int, tenant_code: str = 'default') -> BlockedSenderRule | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(BlockedSenderRule).where(
                BlockedSenderRule.id == rule_id,
                BlockedSenderRule.tenant_code == normalized_tenant,
            )
        )

    def create(self, data: BlockedSenderRuleCreate, tenant_code: str = 'default') -> BlockedSenderRule:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        obj = BlockedSenderRule(tenant_code=normalized_tenant, **data.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: BlockedSenderRule, data: BlockedSenderRuleUpdate) -> BlockedSenderRule:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: BlockedSenderRule) -> None:
        self.db.delete(obj)
        self.db.commit()
