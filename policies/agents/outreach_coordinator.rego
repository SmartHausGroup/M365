package agents.outreach_coordinator

import future.keywords.contains
import future.keywords.if

default allow_actions = {}

allow_actions = {
  "email.send_individual",
  "email.send_bulk",
  "email.schedule",
  "meeting.schedule",
  "followup.create",
  "campaign.create",
}

# Require approval for large bulk sends; otherwise not required
approval_required contains action if {
  action := "email.send_bulk"
  input.action == action
  input.data.recipients_count > 100
}
