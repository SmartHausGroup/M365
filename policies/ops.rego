package ops

import future.keywords.if
import future.keywords.in

# Default decision (deny-by-default)
default decision := {
  "allow": false,
  "approval_required": false,
  "reason": "denied_by_default"
}

# Generated from the active persona graph and the explicit
# unsupported_m365_only_action perimeter in src/ops_adapter/actions.py.
effective_input := object.get(input, "input", input)
effective_agent := effective_input.agent
effective_action := effective_input.action
effective_data := object.get(effective_input, "data", {})

default rate_limited := false
rate_limited if {
  not object.get(effective_input, "rate_allowed", false)
}

allowed if {
  allow_map := allowed_actions
  effective_action in allow_map[effective_agent]
}

approval_required if {
  approval_map := mandatory_approvals
  effective_action in approval_map[effective_agent]
}

approval_required if {
  effective_agent == "calendar-management-agent"
  effective_action == "meeting.organize"
  object.get(effective_data, "attendees_count", 0) > 10
}

approval_required if {
  effective_agent == "calendar-management-agent"
  effective_action == "meeting.organize"
  object.get(effective_data, "external_attendees", 0) > 0
}

approval_required if {
  effective_agent == "email-processing-agent"
  effective_action == "email.respond"
  object.get(effective_data, "priority", "") == "high"
}

approval_required if {
  effective_agent == "email-processing-agent"
  effective_action == "email.respond"
  object.get(effective_data, "contains_sensitive_info", false) == true
}

approval_required if {
  effective_agent == "outreach-coordinator"
  effective_action == "email.send_bulk"
  recipients := object.get(
    effective_data,
    "recipients_count",
    object.get(effective_data, "recipients", 0),
  )
  recipients > 100
}

approval_required if {
  effective_agent == "project-coordination-agent"
  effective_action == "task.assign"
  object.get(effective_data, "estimated_hours", 0) > 40
}

approval_required if {
  effective_agent == "project-coordination-agent"
  effective_action == "task.assign"
  object.get(effective_data, "priority", "") == "critical"
}

approval_required if {
  effective_agent == "project-shipper"
  effective_action == "task.assign"
  object.get(effective_data, "estimated_hours", 0) > 40
}

approval_required if {
  effective_agent == "project-shipper"
  effective_action == "task.assign"
  object.get(effective_data, "priority", "") == "critical"
}

approval_required if {
  effective_agent == "support-responder"
  effective_action == "mail.send"
  object.get(effective_data, "priority", "") == "high"
}

approval_required if {
  effective_agent == "support-responder"
  effective_action == "mail.send"
  object.get(effective_data, "contains_sensitive_info", false) == true
}

decision := {
  "allow": false,
  "approval_required": false,
  "reason": "rate_limited"
} if {
  rate_limited
}

decision := {
  "allow": true,
  "approval_required": true,
  "reason": ""
} if {
  not rate_limited
  allowed
  approval_required
}

decision := {
  "allow": true,
  "approval_required": false,
  "reason": ""
} if {
  not rate_limited
  allowed
  not approval_required
}

decision := {
  "allow": false,
  "approval_required": false,
  "reason": "action_not_allowed"
} if {
  not rate_limited
  not allowed
}

allowed_actions := {
  "ai-engineer": {"files.get", "files.list", "files.search", "lists.create_item", "lists.items", "lists.list", "reports.teams_activity", "reports.users_active", "sites.get", "sites.list"},
  "analytics-reporter": {"lists.get", "lists.items", "lists.list", "reports.email_activity", "reports.onedrive_usage", "reports.sharepoint_usage", "reports.teams_activity", "reports.users_active", "sites.list"},
  "api-tester": {"health.issue_get", "health.issues", "health.overview", "reports.email_activity", "reports.onedrive_usage", "reports.sharepoint_usage", "reports.teams_activity", "reports.users_active"},
  "audit-operations": {"audit.directory", "audit.provisioning", "audit.signins"},
  "backend-architect": {"apps.get", "apps.list", "drives.list", "files.get", "files.list", "files.search", "lists.create_item", "lists.get", "lists.items", "lists.list", "service_principals.list", "sites.get", "sites.list"},
  "brand-guardian": {"drives.list", "files.get", "files.list", "files.search", "lists.items", "lists.list", "sites.get", "sites.list"},
  "calendar-management-agent": {"availability.check", "calendar.availability", "calendar.create", "calendar.delete", "calendar.get", "calendar.list", "calendar.schedule", "calendar.update", "meeting.organize", "reminder.send"},
  "client-relationship-agent": {"client.follow-up", "satisfaction.survey"},
  "content-creator": {"drives.list", "files.get", "files.list", "lists.create_item", "lists.items", "lists.list", "sites.get", "sites.list"},
  "device-management": {"devices.actions", "devices.compliance", "devices.get", "devices.list"},
  "devops-automator": {"devices.compliance", "devices.get", "devices.list", "health.issue_get", "health.issues", "health.messages", "health.overview", "reports.email_activity", "reports.teams_activity", "reports.users_active"},
  "email-processing-agent": {"email.archive", "email.forward", "email.respond", "follow-up.schedule", "mail.delete", "mail.folders", "mail.forward", "mail.list", "mail.move", "mail.read", "mail.reply", "mail.send", "mailbox.settings"},
  "experiment-tracker": {"channels.list", "lists.create_item", "lists.items", "lists.list", "reports.teams_activity", "reports.users_active", "sites.list", "teams.list"},
  "feedback-synthesizer": {"files.list", "lists.create_item", "lists.items", "lists.list", "mail.list", "mail.read", "sites.list"},
  "finance-tracker": {"files.get", "files.list", "files.search", "lists.create_item", "lists.items", "lists.list", "sites.get", "sites.list"},
  "frontend-developer": {"drives.list", "files.create_folder", "files.get", "files.list", "files.search", "sites.get", "sites.list"},
  "growth-hacker": {"calendar.list", "lists.create_item", "lists.items", "lists.list", "mail.list", "mail.read", "mail.send", "reports.email_activity", "reports.teams_activity", "sites.list"},
  "hr-generalist": {"employee.offboard", "employee.onboard", "employee.update_info"},
  "identity-security": {"ca.named_locations", "ca.policies", "ca.policy_create", "ca.policy_delete", "ca.policy_get", "ca.policy_update"},
  "infrastructure-maintainer": {"devices.compliance", "devices.get", "devices.list", "files.get", "files.list", "security.alert_get", "security.alerts", "sites.list"},
  "it-operations-manager": {"alerts.respond", "backup.verify", "infrastructure.monitor", "security.scan", "system.health-check"},
  "legal-compliance-checker": {"files.get", "files.list", "files.search", "lists.items", "lists.list", "sites.get", "sites.list"},
  "m365-administrator": {"apps.get", "apps.list", "apps.update", "directory.domains", "directory.org", "directory.role_members", "directory.roles", "drives.list", "files.create_folder", "files.get", "files.list", "files.search", "files.share", "files.upload", "groups.add_member", "groups.create", "groups.get", "groups.list", "groups.list_members", "groups.remove_member", "licenses.assign", "lists.create_item", "lists.get", "lists.items", "lists.list", "service_principals.list", "sites.get", "sites.list", "sites.provision", "sites.root", "teams.add_channel", "teams.create", "users.create", "users.disable", "users.list", "users.read", "users.update"},
  "mobile-app-builder": {"channels.list", "drives.list", "files.create_folder", "files.get", "files.list", "sites.list", "teams.list"},
  "outreach-coordinator": {"email.schedule", "email.send_bulk", "email.send_individual", "followup.create", "mail.send", "meeting.schedule"},
  "performance-benchmarker": {"lists.items", "lists.list", "reports.email_activity", "reports.onedrive_usage", "reports.sharepoint_usage", "reports.teams_activity", "reports.users_active", "sites.list"},
  "platform-manager": {"apps.get", "apps.list", "directory.org", "service_principals.list", "sites.list", "sites.provision"},
  "project-coordination-agent": {"create_bucket", "create_plan", "create_task", "deadline.track", "list_buckets", "list_plans", "report.generate", "status.update", "task.assign", "task.create"},
  "project-manager": {"archive-project", "calendar.create", "calendar.get", "calendar.list", "channels.list", "lists.items", "lists.list", "sites.list", "teams.get", "teams.list"},
  "project-shipper": {"create_bucket", "create_task", "deadline.track", "list_buckets", "list_plans", "report.generate", "status.update", "task.assign", "task.create"},
  "rapid-prototyper": {"channels.list", "files.get", "files.list", "lists.create_item", "lists.items", "lists.list", "sites.list", "teams.list"},
  "recruitment-assistance-agent": {"interview.schedule"},
  "reports": {"reports.email_activity", "reports.onedrive_usage", "reports.sharepoint_usage", "reports.teams_activity", "reports.users_active"},
  "security-operations": {"security.alert_get", "security.alert_update", "security.alerts", "security.incident_get", "security.incidents", "security.secure_score"},
  "service-health": {"health.issue_get", "health.issues", "health.messages", "health.overview"},
  "sprint-prioritizer": {"calendar.availability", "calendar.create", "calendar.get", "calendar.list", "channels.create", "channels.list", "teams.get", "teams.list"},
  "studio-producer": {"calendar.create", "calendar.get", "calendar.list", "channels.list", "lists.items", "lists.list", "sites.list", "teams.get", "teams.list"},
  "support-responder": {"client.follow-up", "mail.folders", "mail.list", "mail.read", "mail.reply", "mail.send", "satisfaction.survey"},
  "teams-manager": {"add-workspace-members", "channels.create", "channels.list", "channels.send_message", "chat.create", "chat.list", "chat.send", "chat.send_message", "create-channels", "create-workspace", "get-team-status", "teams.add_member", "teams.archive", "teams.create", "teams.get", "teams.list", "teams.remove_member"},
  "test-results-analyzer": {"files.get", "files.list", "files.search", "lists.items", "lists.list", "reports.users_active", "sites.list"},
  "test-writer-fixer": {"files.get", "files.list", "files.search", "lists.create_item", "lists.items", "lists.list", "sites.list"},
  "tool-evaluator": {"files.get", "files.list", "lists.items", "lists.list", "reports.teams_activity", "reports.users_active", "sites.list"},
  "trend-researcher": {"files.get", "files.list", "lists.items", "lists.list", "reports.teams_activity", "reports.users_active", "sites.list"},
  "ucp-administrator": {"admin.audit_log", "admin.get_tenant_config", "admin.get_tier", "admin.get_user_tier", "admin.list_tiers", "admin.list_users", "admin.reload_config", "admin.remove_user_tier", "admin.set_user_tier"},
  "ui-designer": {"drives.list", "files.create_folder", "files.get", "files.list", "files.search", "sites.get", "sites.list"},
  "ux-researcher": {"calendar.create", "calendar.list", "files.get", "files.list", "mail.list", "mail.read", "sites.list"},
  "visual-storyteller": {"drives.list", "files.create_folder", "files.get", "files.list", "files.search", "sites.get", "sites.list"},
  "website-manager": {"files.create_folder", "files.get", "files.list", "files.search", "files.share", "files.upload", "lists.create_item", "lists.get", "lists.items", "lists.list", "sites.get", "sites.list"},
  "whimsy-injector": {"drives.list", "files.get", "files.list", "files.search", "lists.items", "lists.list", "sites.list"},
  "workflow-optimizer": {"files.get", "files.list", "lists.items", "lists.list", "reports.email_activity", "reports.sharepoint_usage", "reports.teams_activity", "sites.list"},
}

mandatory_approvals := {
  "ai-engineer": {"lists.create_item"},
  "backend-architect": {"lists.create_item"},
  "device-management": {"devices.actions"},
  "devops-automator": {"devices.compliance"},
  "finance-tracker": {"lists.create_item"},
  "growth-hacker": {"lists.create_item", "mail.send"},
  "hr-generalist": {"employee.offboard"},
  "identity-security": {"ca.policy_create", "ca.policy_delete", "ca.policy_update"},
  "infrastructure-maintainer": {"devices.compliance"},
  "it-operations-manager": {"security.scan"},
  "m365-administrator": {"groups.add_member", "groups.create", "licenses.assign", "sites.provision", "teams.add_channel", "teams.create", "users.create", "users.disable", "users.update"},
  "security-operations": {"security.alert_update"},
  "teams-manager": {"teams.archive", "teams.remove_member"},
  "ucp-administrator": {"admin.remove_user_tier", "admin.set_user_tier"},
}
