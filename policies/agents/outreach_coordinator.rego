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
  "mail.send",
}

approval_required contains action if {
  action := "email.send_bulk"
  input.action == action
  recipients := object.get(input.data, "recipients_count", object.get(input.data, "recipients", 0))
  recipients > 100
}
