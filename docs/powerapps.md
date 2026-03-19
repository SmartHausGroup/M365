# Power Apps – Client Portal and Status Tracker

Data Backbone
- SharePoint list per service site named `RepositoryStatus`
  - Columns: Repo (Text), Status (Choice), OpenIssues (Number), Velocity (Number), LastUpdated (Date)
- Optional lists: `Milestones`, `Risks`, `Deliverables`

Apps
- Repository Status Tracker
  - Create from data → SharePoint → `RepositoryStatus`
  - Add gallery by service, detail view for recent tasks and links to Teams/Planner
- Client Portal
  - Read-only views across multiple service lists (use a central list or API endpoint)
  - Embed Power BI tiles for executive summaries

Security
- Use Azure AD security groups mapped to service Teams for access control
- For external clients, use guest access with constrained permissions

Automation Hooks
- Trigger Flows from app actions (e.g., Request Review → create Planner task + Teams notification)
