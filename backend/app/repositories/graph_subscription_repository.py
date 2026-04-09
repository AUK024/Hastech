from __future__ import annotations

from datetime import datetime
from sqlalchemy import delete
from sqlalchemy import select
from app.models.graph_subscription import GraphSubscription
from app.repositories.base import RepositoryBase
from app.schemas.graph_subscription import GraphSubscriptionCreate, GraphSubscriptionUpdate


class GraphSubscriptionRepository(RepositoryBase):
    def list(self, tenant_code: str = 'default') -> list[GraphSubscription]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(GraphSubscription)
            .where(GraphSubscription.tenant_code == normalized_tenant)
            .order_by(GraphSubscription.id.desc())
        ).all()

    def list_active(self, tenant_code: str = 'default') -> list[GraphSubscription]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(GraphSubscription)
            .where(GraphSubscription.tenant_code == normalized_tenant)
            .where(GraphSubscription.is_active.is_(True))
            .order_by(GraphSubscription.id.desc())
        ).all()

    def list_due_for_renewal(self, renew_before: datetime, tenant_code: str = 'default') -> list[GraphSubscription]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(GraphSubscription)
            .where(GraphSubscription.tenant_code == normalized_tenant)
            .where(GraphSubscription.is_active.is_(True))
            .where(GraphSubscription.graph_subscription_id.is_not(None))
            .where(GraphSubscription.expiration_datetime.is_not(None))
            .where(GraphSubscription.expiration_datetime <= renew_before)
            .order_by(GraphSubscription.expiration_datetime.asc())
        ).all()

    def get(self, subscription_id: int, tenant_code: str = 'default') -> GraphSubscription | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(GraphSubscription).where(
                GraphSubscription.id == subscription_id,
                GraphSubscription.tenant_code == normalized_tenant,
            )
        )

    def get_by_mailbox_id(self, mailbox_id: int, tenant_code: str = 'default') -> GraphSubscription | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(GraphSubscription).where(
                GraphSubscription.mailbox_id == mailbox_id,
                GraphSubscription.tenant_code == normalized_tenant,
            )
        )

    def create(self, data: GraphSubscriptionCreate) -> GraphSubscription:
        payload = data.model_dump()
        payload['tenant_code'] = str(payload.get('tenant_code', 'default')).strip().lower() or 'default'
        obj = GraphSubscription(**payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: GraphSubscription, data: GraphSubscriptionUpdate) -> GraphSubscription:
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_by_mailbox_id(self, mailbox_id: int, tenant_code: str = 'default') -> None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        self.db.execute(
            delete(GraphSubscription).where(
                GraphSubscription.mailbox_id == mailbox_id,
                GraphSubscription.tenant_code == normalized_tenant,
            )
        )
        self.db.commit()
