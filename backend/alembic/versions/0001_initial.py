"""initial schema"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'monitored_mailboxes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('mailbox_type', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('auto_reply_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'auto_reply_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('source_language', sa.String(10), nullable=False),
        sa.Column('subject_template', sa.Text(), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('signature_template', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'blocked_sender_rules',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('rule_value', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('setting_key', sa.String(120), nullable=False, unique=True),
        sa.Column('setting_value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'incoming_emails',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mailbox_id', sa.Integer(), sa.ForeignKey('monitored_mailboxes.id'), nullable=False),
        sa.Column('message_id', sa.String(255), nullable=False, unique=True),
        sa.Column('internet_message_id', sa.String(255), nullable=True),
        sa.Column('conversation_id', sa.String(255), nullable=False),
        sa.Column('sender_name', sa.String(255), nullable=True),
        sa.Column('sender_email', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body_preview', sa.Text(), nullable=True),
        sa.Column('detected_language', sa.String(20), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_internal', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_blocked_by_rule', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('processing_status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'auto_reply_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('incoming_email_id', sa.Integer(), sa.ForeignKey('incoming_emails.id'), nullable=False),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('auto_reply_templates.id'), nullable=False),
        sa.Column('translated_subject', sa.Text(), nullable=True),
        sa.Column('translated_body', sa.Text(), nullable=True),
        sa.Column('target_language', sa.String(20), nullable=True),
        sa.Column('reply_sent', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('provider_message_id', sa.String(255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'webhook_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_type', sa.String(120), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('module_name', sa.String(120), nullable=False),
        sa.Column('action_name', sa.String(120), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('result', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    for table in ['audit_logs', 'webhook_logs', 'auto_reply_logs', 'incoming_emails', 'app_settings', 'blocked_sender_rules', 'auto_reply_templates', 'monitored_mailboxes']:
        op.drop_table(table)
