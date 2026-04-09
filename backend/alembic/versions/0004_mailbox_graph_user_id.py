"""add graph_user_id to monitored mailboxes"""
from alembic import op
import sqlalchemy as sa

revision = '0004_mailbox_graph_user_id'
down_revision = '0003_employee_user_password_hash'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('monitored_mailboxes', sa.Column('graph_user_id', sa.String(length=255), nullable=True))
    op.create_index('ix_monitored_mailboxes_graph_user_id', 'monitored_mailboxes', ['graph_user_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_monitored_mailboxes_graph_user_id', table_name='monitored_mailboxes')
    op.drop_column('monitored_mailboxes', 'graph_user_id')
