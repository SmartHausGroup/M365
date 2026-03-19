## Agent API Reference

Base path: `/api/agents`

Endpoints
- `GET /api/agents/status` — Summary of all agents
- `GET /api/agents/{agentId}/status` — Per-agent status and task counters
- `GET /api/agents/{agentId}/tasks` — List tasks for the agent
- `POST /api/agents/{agentId}/tasks` — Create task
  - Body: `{ "title": "...", "description?": "...", "priority?": "low|medium|high|critical", "due?": "ISO" }`
- `PUT /api/agents/{agentId}/tasks/{taskId}` — Update task status
  - Body: `{ "status": "queued|in_progress|completed|failed", "percent?": 0-100, "message?": "..." }`
- `POST /api/agents/{agentId}/instructions` — Send instruction
  - Body: `{ "instruction": "...", "mode?": "immediate|scheduled|conditional|recurring", "priority?": "normal|high", "scheduled_at?": "ISO" }`
- `GET /api/agents/{agentId}/logs` — Event log for the agent
- `GET /api/agents/{agentId}/performance` — Computed performance metrics
- `POST /api/agents/{agentId}/execute` — Execute allowed agent action (dry-run by default)
  - Body: `{ "action": "<agent action>", "params": {..} }`
  - Honors `ALLOW_M365_MUTATIONS=true` and `OPS_ADAPTER_URL` to route via Ops Adapter

Notes
- Persistence uses local JSON store under `APP_DATA` (default `./data`).
- HTML dashboard pages include a simple Quick Actions panel for assigning tasks, sending instructions, and viewing logs.
- For production, enable auth and RBAC via Microsoft OAuth (see `MICROSOFT_OAUTH_SETUP.md`).
