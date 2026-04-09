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
import { EmployeeUsersPage } from './EmployeeUsersPage'
import { GraphSubscriptionsPage } from './GraphSubscriptionsPage'
import { TenantsPage } from './TenantsPage'

export const routes = [
  { path: '/login', label: 'Login', component: LoginPage, public: true, sidebar: false, category: 'Auth' },
  { path: '/', label: 'Dashboard', component: DashboardPage, category: 'Overview' },
  { path: '/employee-users', label: 'Employee Users', component: EmployeeUsersPage, category: 'Overview', adminOnly: true },
  { path: '/mailboxes', label: 'Mailbox List', component: MailboxListPage, category: 'Operations' },
  { path: '/mailboxes/:id', label: 'Mailbox Detail', component: MailboxDetailPage, category: 'Operations', sidebar: false },
  { path: '/templates', label: 'Template List', component: TemplateListPage, category: 'Operations' },
  { path: '/templates/:id', label: 'Template Edit', component: TemplateEditPage, category: 'Operations', sidebar: false },
  { path: '/blocked-rules', label: 'Blocked Rules', component: BlockedRulesListPage, category: 'Operations' },
  { path: '/blocked-rules/:id', label: 'Blocked Rule Edit', component: BlockedRuleEditPage, category: 'Operations', sidebar: false },
  { path: '/incoming-mails', label: 'Incoming Logs', component: IncomingMailLogsPage, category: 'Logs' },
  { path: '/auto-reply-logs', label: 'Auto Reply Logs', component: AutoReplyLogsPage, category: 'Logs' },
  { path: '/webhook-logs', label: 'Webhook Logs', component: WebhookLogsPage, category: 'Logs' },
  { path: '/audit-logs', label: 'Audit Logs', component: AuditLogsPage, category: 'Logs' },
  { path: '/reports', label: 'Reports', component: ReportsPage, category: 'Reports' },
  { path: '/reports/:id', label: 'Report Detail', component: ReportDetailPage, category: 'Reports', sidebar: false },
  { path: '/graph-subscriptions', label: 'Graph Subscriptions', component: GraphSubscriptionsPage, category: 'System', adminOnly: true },
  { path: '/tenants', label: 'Tenants', component: TenantsPage, category: 'System', adminOnly: true },
  { path: '/settings', label: 'Settings', component: SettingsPage, category: 'System' },
]
