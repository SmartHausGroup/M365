# Power Automate – Workflow Blueprints

These blueprints mirror the GitHub → Teams/Planner automations implemented in the API so you can run everything 100% inside Power Platform if preferred.

1) GitHub → Teams (Push Notification)
- Trigger: When an HTTP request is received
- Parse JSON: GitHub push schema
- Action: Post message in a chat or channel (Teams) → Channel: General → Message: Commit summary with link

2) GitHub → Planner (Issue → Backlog)
- Trigger: When an HTTP request is received
- Condition: `@equals(triggerBody()?.action, 'opened')` and `@contains(string(triggerBody()), 'issue')`
- Action: Create a task (Planner) → Plan: per-service plan → Bucket: Backlog → Title: `Issue opened: #{number} {title}` → References: issue URL

3) GitHub → Planner (PR → Code Review)
- Trigger: When an HTTP request is received
- Condition: action in `opened, reopened, ready_for_review`
- Action: Create a task (Planner) in `Code Review` bucket → Title: `PR: #{number} {title}` → References: PR URL
- Action: Post message (Teams) into `Code Review` channel

4) Release → Teams + Done
- Trigger: When an HTTP request is received
- Condition: `@equals(triggerBody()?.action, 'published')`
- Action: Create/Update task (Planner) with `percentComplete=100` in `Done`
- Action: Post message (Teams) with release notes link

5) UCP → Teams (Setup Token Delivery, SmartHaus Internal Only)
- Trigger: When an HTTP request is received
- Scope: SmartHaus internal UCP administration only
- Validate: `X-UCP-Flow-Event`, `X-UCP-Flow-Schema-Version`, `X-UCP-Flow-Secret`, `X-UCP-Request-Id`
- Parse JSON: the `ucp_setup_token_delivery` contract from UCP
- Action: Post setup token to the intended teammate in Teams
- Action: Return the exact success or failure JSON contract expected by UCP
- Artifacts:
  - `flows/internal-ops/ucp-setup-token-delivery-flow.json`
  - `flows/internal-ops/UCP_SETUP_TOKEN_DELIVERY_FLOW_RUNBOOK.md`

Deployment Tips
- Package into a Power Platform Solution for ALM
- Parameterize: API key or secret, Plan IDs, Team/Channel IDs via Environment Variables
- For GitHub origin, either: set organization webhooks to the Flow HTTP endpoint or use GitHub connector triggers
