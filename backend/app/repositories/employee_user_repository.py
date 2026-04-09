from sqlalchemy import select
from app.core.security import hash_password
from app.models.employee_user import EmployeeUser
from app.repositories.base import RepositoryBase
from app.schemas.employee_user import EmployeeUserCreate, EmployeeUserUpdate


class EmployeeUserRepository(RepositoryBase):
    def list(self, tenant_code: str = 'default') -> list[EmployeeUser]:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalars(
            select(EmployeeUser)
            .where(EmployeeUser.tenant_code == normalized_tenant)
            .order_by(EmployeeUser.id.desc())
        ).all()

    def get(self, user_id: int, tenant_code: str = 'default') -> EmployeeUser | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(EmployeeUser).where(
                EmployeeUser.id == user_id,
                EmployeeUser.tenant_code == normalized_tenant,
            )
        )

    def get_by_email(self, email: str, tenant_code: str = 'default') -> EmployeeUser | None:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        return self.db.scalar(
            select(EmployeeUser).where(
                EmployeeUser.email == email.lower(),
                EmployeeUser.tenant_code == normalized_tenant,
            )
        )

    def create(self, data: EmployeeUserCreate, created_by: str, tenant_code: str = 'default') -> EmployeeUser:
        normalized_tenant = tenant_code.strip().lower() or 'default'
        user = EmployeeUser(
            tenant_code=normalized_tenant,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            is_active=data.is_active,
            created_by=created_by.lower(),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, obj: EmployeeUser, data: EmployeeUserUpdate) -> EmployeeUser:
        payload = data.model_dump(exclude_none=True)
        new_password = payload.pop('password', None)
        if new_password:
            obj.password_hash = hash_password(new_password)
        for key, value in payload.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: EmployeeUser) -> None:
        self.db.delete(obj)
        self.db.commit()
