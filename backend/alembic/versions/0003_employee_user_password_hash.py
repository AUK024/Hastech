"""add password hash to employee users"""
from alembic import op
import sqlalchemy as sa

revision = '0003_employee_user_password_hash'
down_revision = '0002_employee_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('employee_users', sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''))
    op.alter_column('employee_users', 'password_hash', server_default=None)


def downgrade() -> None:
    op.drop_column('employee_users', 'password_hash')
