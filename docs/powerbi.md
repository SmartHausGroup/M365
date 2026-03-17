# Power BI – Data Sources and Dashboards

Data Sources
- API: `/api/m365/empire-overview` – enterprise-wide, multi-service JSON snapshot
- API: `/api/research/insights` – cross-repository research KPIs
- API: `/api/bi/analytics` – website, client, marketing aggregates
- Optionally: SharePoint lists within each service site for persistent metrics (e.g., `RepositoryStatus`)

Recommended Datasets
- Enterprise Overview: Services, Repos, Active Work, Risks, Compliance
- Engineering Velocity: Issues/PRs created/closed (by week), Cycle time, Throughput
- Resource Allocation: Tasks by assignee, WIP by service, Load
- Compliance: Policy checks, Review completion, Evidence links

Modeling Tips
- Normalize service key (`tai`, `lattice`, etc.) across all tables
- Use Date tables for time-series visuals
- Ingest GitHub + Planner metrics via scheduled refresh against API endpoints

Publishing
- Publish datasets to your Fabric/Power BI workspace
- Create Executive dashboards with cards for total velocity, on-time delivery, top risks

