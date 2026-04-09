"""add tenants table"""
from alembic import op
import sqlalchemy as sa

revision = '0006_tenants'
down_revision = '0005_graph_subscriptions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_code', sa.String(length=120), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_tenants_tenant_code', 'tenants', ['tenant_code'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_tenants_tenant_code', table_name='tenants')
    op.drop_table('tenants')
