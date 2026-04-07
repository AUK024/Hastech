from sqlalchemy import select
from app.core.security import hash_password
from app.models.employee_user import EmployeeUser
from app.repositories.base import RepositoryBase
from app.schemas.employee_user import EmployeeUserCreate, EmployeeUserUpdate


class EmployeeUserRepository(RepositoryBase):
    def list(self) -> list[EmployeeUser]:
        return self.db.scalars(select(EmployeeUser).order_by(EmployeeUser.id.desc())).all()

    def get(self, user_id: int) -> EmployeeUser | None:
        return self.db.scalar(select(EmployeeUser).where(EmployeeUser.id == user_id))

    def get_by_email(self, email: str) -> EmployeeUser | None:
        return self.db.scalar(select(EmployeeUser).where(EmployeeUser.email == email.lower()))

    def create(self, data: EmployeeUserCreate, created_by: str) -> EmployeeUser:
        user = EmployeeUser(
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
