from __future__ import annotations

from datetime import datetime
from sqlalchemy import delete
from sqlalchemy import select
from app.models.graph_subscription import GraphSubscription
from app.repositories.base import RepositoryBase
from app.schemas.graph_subscription import GraphSubscriptionCreate, GraphSubscriptionUpdate


class GraphSubscriptionRepository(RepositoryBase):
    def list(self) -> list[GraphSubscription]:
        return self.db.scalars(select(GraphSubscription).order_by(GraphSubscription.id.desc())).all()

    def list_active(self) -> list[GraphSubscription]:
        return self.db.scalars(
            select(GraphSubscription)
            .where(GraphSubscription.is_active.is_(True))
            .order_by(GraphSubscription.id.desc())
        ).all()

    def list_due_for_renewal(self, renew_before: datetime) -> list[GraphSubscription]:
        return self.db.scalars(
            select(GraphSubscription)
            .where(GraphSubscription.is_active.is_(True))
            .where(GraphSubscription.graph_subscription_id.is_not(None))
            .where(GraphSubscription.expiration_datetime.is_not(None))
            .where(GraphSubscription.expiration_datetime <= renew_before)
            .order_by(GraphSubscription.expiration_datetime.asc())
        ).all()

    def get(self, subscription_id: int) -> GraphSubscription | None:
        return self.db.scalar(select(GraphSubscription).where(GraphSubscription.id == subscription_id))

    def get_by_mailbox_id(self, mailbox_id: int) -> GraphSubscription | None:
        return self.db.scalar(select(GraphSubscription).where(GraphSubscription.mailbox_id == mailbox_id))

    def create(self, data: GraphSubscriptionCreate) -> GraphSubscription:
        obj = GraphSubscription(**data.model_dump())
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

    def delete_by_mailbox_id(self, mailbox_id: int) -> None:
        self.db.execute(delete(GraphSubscription).where(GraphSubscription.mailbox_id == mailbox_id))
        self.db.commit()
