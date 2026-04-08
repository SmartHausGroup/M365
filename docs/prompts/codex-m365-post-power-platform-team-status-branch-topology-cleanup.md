# MATHS Prompt: M365 Post Power Platform and Team Status Branch Topology Cleanup

## Governance Ack

- `PLAN_REF_ACK: plan:m365-post-power-platform-team-status-branch-topology-cleanup:R1`
- `PARENT_PLAN_ACK: plan:m365-power-platform-and-team-status-merge-to-development`
- `NORTH_STAR_ACK: Operations/NORTHSTAR.md`

## Goal

Delete the merged feature branch `codex/m365-power-platform-executor-auth-remediation` locally and on origin after proving it has zero unique commits beyond `development`.

## Rules

- validate the merged ancestry first
- delete only the approved local and remote branch
- keep `development`, `staging`, and `main`
- synchronize trackers truthfully
