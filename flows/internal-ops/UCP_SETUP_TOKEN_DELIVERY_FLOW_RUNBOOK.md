# UCP Setup Token Delivery Flow Runbook

## Purpose

This runbook defines how SmartHaus builds the internal-only Power Automate flow
used by local UCP admins to deliver setup tokens to teammates through Teams.

This is not part of the public/customer-facing M365 integration-pack surface.
It exists only to support SmartHaus management of UCP onboarding.

## Inputs

- Flow blueprint:
  - `flows/internal-ops/ucp-setup-token-delivery-flow.json`
- UCP contract docs:
  - `docs/platform/SMARTHAUS_INTERNAL_POWER_AUTOMATE_TOKEN_DELIVERY_FLOW_CONTRACT.md`
  - `docs/platform/SMARTHAUS_INTERNAL_POWER_AUTOMATE_TOKEN_DELIVERY_FAILURE_BOUNDARIES.md`
  - `docs/platform/SMARTHAUS_INTERNAL_POWER_AUTOMATE_TOKEN_DELIVERY_BUILD_ASSEMBLY.md`

## Required Operator Decisions

Before building the flow, lock:

1. Which SmartHaus admin owns the flow
2. Which SmartHaus environment stores the shared secret
3. Whether delivery goes to:
   - one-to-one Teams chat, or
   - a tightly controlled internal channel only if chat delivery is not viable
4. How SmartHaus rotates the shared secret when a token-delivery leak is suspected

## Prerequisites

- Access to Power Automate in the SmartHaus tenant
- Access to Microsoft Teams in the SmartHaus tenant
- A generated shared secret value for `UCP_INTERNAL_TEAMS_TOKEN_FLOW_SHARED_SECRET`
- A local UCP admin machine that will later set:
  - `UCP_INTERNAL_TEAMS_TOKEN_FLOW_URL`
  - `UCP_INTERNAL_TEAMS_TOKEN_FLOW_SHARED_SECRET`

## Build Steps

### 1. Create the flow

Create a new Power Automate cloud flow with trigger:

- **When an HTTP request is received**

This becomes the endpoint referenced by `UCP_INTERNAL_TEAMS_TOKEN_FLOW_URL`.

### 2. Add request validation

Validate these headers before any Teams action:

- `X-UCP-Flow-Event`
- `X-UCP-Flow-Schema-Version`
- `X-UCP-Flow-Secret`
- `X-UCP-Request-Id`

Reject the request unless:

- `X-UCP-Flow-Event == ucp_setup_token_delivery`
- `X-UCP-Flow-Schema-Version == 2026-03-20`
- `X-UCP-Flow-Secret` matches the configured secret
- `X-UCP-Request-Id` is non-empty

### 3. Parse and validate the JSON body

Require the exact Phase 2 fields:

- `event`
- `schema_version`
- `request_id`
- `recipient_upn`
- `recipient_name`
- `tenant_id`
- `issued_by`
- `ttl_seconds`
- `expires_at`
- `token`
- `setup_url`
- `instructions`

Reject the request if:

- the body is not valid JSON
- any required field is missing
- `event != ucp_setup_token_delivery`
- `schema_version != 2026-03-20`
- `recipient_upn` is empty
- `token` does not start with `shst_`

### 4. Deliver through Teams

Compose the Teams message using:

- recipient: `recipient_upn`
- token: `token`
- setup instructions: `instructions`
- optional metadata: `tenant_id`, `issued_by`, `expires_at`

Preferred path:

- **Post message in a chat or channel**
- Mode: direct teammate chat if available in the tenant permissions model

Do not echo the token anywhere except the intended Teams delivery body.

### 5. Return the success contract

On successful delivery, return `HTTP 200` with JSON:

```json
{
  "status": "delivered",
  "delivery_backend": "power_automate",
  "delivery_channel": "teams",
  "delivery_target": "babu@smarthausgroup.com",
  "recipient_upn": "babu@smarthausgroup.com",
  "provider_run_id": "08585287489123456789012345678CU01",
  "provider_message_id": "1700000000000",
  "delivered_at": "2026-03-20T21:22:06Z",
  "token_echoed": false
}
```

### 6. Return the failure contract

On failure, return non-2xx JSON:

```json
{
  "status": "error",
  "error_code": "delivery_failed",
  "message": "Teams delivery failed.",
  "retryable": false,
  "delivery_backend": "power_automate",
  "delivery_target": "babu@smarthausgroup.com",
  "provider_run_id": "08585287489123456789012345678CU01",
  "token_echoed": false
}
```

## UCP Admin-Machine Configuration

After the flow exists:

1. Copy the generated HTTP trigger URL
2. Set `UCP_INTERNAL_TEAMS_TOKEN_FLOW_URL`
3. Set `UCP_INTERNAL_TEAMS_TOKEN_FLOW_SHARED_SECRET`
4. Restart the local UCP admin runtime

## Operator Smoke Path

On the SmartHaus admin machine:

1. Start local UCP
2. Call `POST /api/v1/setup/generate-and-deliver-token`
3. Confirm UCP returns:
   - `status: ok`
   - `delivery_backend: power_automate`
   - `delivery_channel: teams`
   - `provider_run_id`
4. Confirm the teammate receives the token in Teams

## No-Go Conditions

Do not call this process complete if:

- the flow URL exists but the shared secret is not enforced
- the flow echoes the token in the HTTP response
- the flow posts into an uncontrolled public channel
- the operator runbook requires hidden manual steps not written here
