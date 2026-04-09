from sqlalchemy import select
from app.models.tenant import Tenant
from app.repositories.base import RepositoryBase
from app.schemas.tenant import TenantCreate, TenantUpdate


class TenantRepository(RepositoryBase):
    def list(self) -> list[Tenant]:
        return self.db.scalars(select(Tenant).order_by(Tenant.id.desc())).all()

    def get(self, tenant_id: int) -> Tenant | None:
        return self.db.scalar(select(Tenant).where(Tenant.id == tenant_id))

    def get_by_code(self, tenant_code: str) -> Tenant | None:
        normalized = tenant_code.strip().lower()
        return self.db.scalar(select(Tenant).where(Tenant.tenant_code == normalized))

    def create(self, data: TenantCreate) -> Tenant:
        obj = Tenant(
            tenant_code=data.tenant_code.strip().lower(),
            display_name=data.display_name,
            is_active=data.is_active,
            description=data.description,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: Tenant, data: TenantUpdate) -> Tenant:
        payload = data.model_dump(exclude_none=True)
        for key, value in payload.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: Tenant) -> None:
        self.db.delete(obj)
        self.db.commit()
