package ops

import future.keywords.if

# Default decision (deny-by-default)
default decision := {
  "allow": false,
  "approval_required": false,
  "reason": "denied_by_default"
}

effective_input := object.get(input, "input", input)

effective_agent := effective_input.agent
effective_action := effective_input.action

default rate_limited := false
rate_limited if {
  not object.get(effective_input, "rate_allowed", false)
}

allowed if {
  allow_map := allowed_actions
  allow_map[effective_agent][effective_action]
}

approval_required if {
  approval_map := mandatory_approvals
  approval_map[effective_agent][effective_action]
}

approval_required if {
  effective_agent == "outreach-coordinator"
  effective_action == "email.send_bulk"
  recipients := object.get(object.get(effective_input, "data", {}), "recipients_count", 0)
  recipients > 100
}

decision := {
  "allow": false,
  "approval_required": false,
  "reason": "rate_limited"
}
if {
  rate_limited
}

decision := {
  "allow": true,
  "approval_required": true,
  "reason": ""
}
if {
  not rate_limited
  allowed
  approval_required
}

decision := {
  "allow": true,
  "approval_required": false,
  "reason": ""
}
if {
  not rate_limited
  allowed
  not approval_required
}

decision := {
  "allow": false,
  "approval_required": false,
  "reason": "action_not_allowed"
}
if {
  not rate_limited
  not allowed
}

allowed_actions := {
  "m365-administrator": {
    "users.read": true,
    "users.create": true,
    "users.update": true,
    "users.disable": true,
    "groups.create": true,
    "groups.add_member": true,
    "teams.create": true,
    "teams.add_channel": true,
    "sites.provision": true,
    "licenses.assign": true,
  },
  "website-manager": {
    "deployment.preview": true,
    "deployment.production": true,
    "content.update": true,
    "content.create": true,
    "analytics.read": true,
    "seo.update": true,
  },
  "hr-generalist": {
    "employee.onboard": true,
    "employee.update_info": true,
    "employee.offboard": true,
    "policy.create": true,
    "review.initiate": true,
  },
  "outreach-coordinator": {
    "email.send_individual": true,
    "email.send_bulk": true,
    "email.schedule": true,
    "meeting.schedule": true,
    "followup.create": true,
    "campaign.create": true,
  },
}

mandatory_approvals := {
  "m365-administrator": {
    "users.disable": true,
  },
  "website-manager": {
    "deployment.production": true,
  },
  "hr-generalist": {
    "employee.offboard": true,
  },
}
