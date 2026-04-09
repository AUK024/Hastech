from sqlalchemy import select
from app.models.auto_reply_template import AutoReplyTemplate
from app.repositories.base import RepositoryBase
from app.schemas.auto_reply_template import AutoReplyTemplateCreate, AutoReplyTemplateUpdate


class TemplateRepository(RepositoryBase):
    def list(self, tenant_code: str = 'default') -> list[AutoReplyTemplate]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(AutoReplyTemplate)
            .where(AutoReplyTemplate.tenant_code == normalized_tenant)
            .order_by(AutoReplyTemplate.id.desc())
        ).all()

    def get(self, template_id: int, tenant_code: str = 'default') -> AutoReplyTemplate | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(AutoReplyTemplate).where(
                AutoReplyTemplate.id == template_id,
                AutoReplyTemplate.tenant_code == normalized_tenant,
            )
        )

    def create(self, data: AutoReplyTemplateCreate, tenant_code: str = 'default') -> AutoReplyTemplate:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        obj = AutoReplyTemplate(tenant_code=normalized_tenant, **data.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: AutoReplyTemplate, data: AutoReplyTemplateUpdate) -> AutoReplyTemplate:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: AutoReplyTemplate) -> None:
        self.db.delete(obj)
        self.db.commit()
