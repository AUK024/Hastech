"""add graph subscriptions table"""
from alembic import op
import sqlalchemy as sa

revision = '0005_graph_subscriptions'
down_revision = '0004_mailbox_graph_user_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'graph_subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mailbox_id', sa.Integer(), sa.ForeignKey('monitored_mailboxes.id'), nullable=False),
        sa.Column('graph_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('resource', sa.String(length=500), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=False, server_default='created'),
        sa.Column('notification_url', sa.String(length=500), nullable=False),
        sa.Column('lifecycle_notification_url', sa.String(length=500), nullable=True),
        sa.Column('client_state', sa.String(length=255), nullable=True),
        sa.Column('expiration_datetime', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_renewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_graph_subscriptions_mailbox_id', 'graph_subscriptions', ['mailbox_id'], unique=True)
    op.create_index('ix_graph_subscriptions_graph_subscription_id', 'graph_subscriptions', ['graph_subscription_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_graph_subscriptions_graph_subscription_id', table_name='graph_subscriptions')
    op.drop_index('ix_graph_subscriptions_mailbox_id', table_name='graph_subscriptions')
    op.drop_table('graph_subscriptions')
