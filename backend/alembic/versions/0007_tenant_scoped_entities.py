"""add tenant_code columns to operational tables"""
from alembic import op
import sqlalchemy as sa

revision = '0007_tenant_scoped_entities'
down_revision = '0006_tenants'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'monitored_mailboxes',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_monitored_mailboxes_tenant_code', 'monitored_mailboxes', ['tenant_code'], unique=False)

    op.add_column(
        'auto_reply_templates',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_auto_reply_templates_tenant_code', 'auto_reply_templates', ['tenant_code'], unique=False)

    op.add_column(
        'blocked_sender_rules',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_blocked_sender_rules_tenant_code', 'blocked_sender_rules', ['tenant_code'], unique=False)

    op.add_column(
        'employee_users',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_employee_users_tenant_code', 'employee_users', ['tenant_code'], unique=False)

    op.add_column(
        'incoming_emails',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_incoming_emails_tenant_code', 'incoming_emails', ['tenant_code'], unique=False)

    op.add_column(
        'auto_reply_logs',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_auto_reply_logs_tenant_code', 'auto_reply_logs', ['tenant_code'], unique=False)

    op.add_column(
        'webhook_logs',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_webhook_logs_tenant_code', 'webhook_logs', ['tenant_code'], unique=False)

    op.add_column(
        'audit_logs',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_audit_logs_tenant_code', 'audit_logs', ['tenant_code'], unique=False)

    op.add_column(
        'graph_subscriptions',
        sa.Column('tenant_code', sa.String(length=120), nullable=False, server_default='default'),
    )
    op.create_index('ix_graph_subscriptions_tenant_code', 'graph_subscriptions', ['tenant_code'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_graph_subscriptions_tenant_code', table_name='graph_subscriptions')
    op.drop_column('graph_subscriptions', 'tenant_code')

    op.drop_index('ix_audit_logs_tenant_code', table_name='audit_logs')
    op.drop_column('audit_logs', 'tenant_code')

    op.drop_index('ix_webhook_logs_tenant_code', table_name='webhook_logs')
    op.drop_column('webhook_logs', 'tenant_code')

    op.drop_index('ix_auto_reply_logs_tenant_code', table_name='auto_reply_logs')
    op.drop_column('auto_reply_logs', 'tenant_code')

    op.drop_index('ix_incoming_emails_tenant_code', table_name='incoming_emails')
    op.drop_column('incoming_emails', 'tenant_code')

    op.drop_index('ix_employee_users_tenant_code', table_name='employee_users')
    op.drop_column('employee_users', 'tenant_code')

    op.drop_index('ix_blocked_sender_rules_tenant_code', table_name='blocked_sender_rules')
    op.drop_column('blocked_sender_rules', 'tenant_code')

    op.drop_index('ix_auto_reply_templates_tenant_code', table_name='auto_reply_templates')
    op.drop_column('auto_reply_templates', 'tenant_code')

    op.drop_index('ix_monitored_mailboxes_tenant_code', table_name='monitored_mailboxes')
    op.drop_column('monitored_mailboxes', 'tenant_code')
