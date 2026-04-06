import { LoginPage } from './LoginPage'
import { DashboardPage } from './DashboardPage'
import { MailboxListPage } from './MailboxListPage'
import { MailboxDetailPage } from './MailboxDetailPage'
import { TemplateListPage } from './TemplateListPage'
import { TemplateEditPage } from './TemplateEditPage'
import { BlockedRulesListPage } from './BlockedRulesListPage'
import { BlockedRuleEditPage } from './BlockedRuleEditPage'
import { SettingsPage } from './SettingsPage'
import { IncomingMailLogsPage } from './IncomingMailLogsPage'
import { AutoReplyLogsPage } from './AutoReplyLogsPage'
import { WebhookLogsPage } from './WebhookLogsPage'
import { AuditLogsPage } from './AuditLogsPage'
import { ReportsPage } from './ReportsPage'
import { ReportDetailPage } from './ReportDetailPage'

export const routes = [
  { path: '/', label: 'Dashboard', component: DashboardPage },
  { path: '/login', label: 'Login', component: LoginPage },
  { path: '/mailboxes', label: 'Mailbox List', component: MailboxListPage },
  { path: '/mailboxes/:id', label: 'Mailbox Detail', component: MailboxDetailPage },
  { path: '/templates', label: 'Template List', component: TemplateListPage },
  { path: '/templates/:id', label: 'Template Edit', component: TemplateEditPage },
  { path: '/blocked-rules', label: 'Blocked Rules', component: BlockedRulesListPage },
  { path: '/blocked-rules/:id', label: 'Blocked Rule Edit', component: BlockedRuleEditPage },
  { path: '/settings', label: 'Settings', component: SettingsPage },
  { path: '/incoming-mails', label: 'Incoming Logs', component: IncomingMailLogsPage },
  { path: '/auto-reply-logs', label: 'Auto Reply Logs', component: AutoReplyLogsPage },
  { path: '/webhook-logs', label: 'Webhook Logs', component: WebhookLogsPage },
  { path: '/audit-logs', label: 'Audit Logs', component: AuditLogsPage },
  { path: '/reports', label: 'Reports', component: ReportsPage },
  { path: '/reports/:id', label: 'Report Detail', component: ReportDetailPage },
]
