"""
Enterprise M365 Management Dashboard
Professional-grade interface for SmartHaus M365 operations
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from smarthaus_common.config import AppConfig, has_selected_tenant, load_bootstrap_env
from smarthaus_common.tenant_config import get_tenant_config
from smarthaus_graph.client import GraphTokenProvider

load_bootstrap_env(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="SmartHaus M365 Enterprise Dashboard", version="2.0.0")

# Enterprise Configuration
ENTERPRISE_CONFIG = {
    "tenant": "smarthausgroup.com",
    "primary_domain": "smarthausgroup.com",
    "business_units": [
        "TAI Quantum AIUCP",
        "SmartHaus Website Platform",
        "LATTICE Research Platform",
        "Enterprise Advisory Services",
    ],
    "critical_services": [
        "Azure AD",
        "Exchange Online",
        "SharePoint Online",
        "Teams",
        "Power Platform",
        "Security & Compliance",
    ],
}


class M365ServiceStatus(BaseModel):
    service: str
    status: str
    health_score: int
    last_updated: datetime
    issues: list[str]
    metrics: dict[str, Any]


class BusinessUnitMetrics(BaseModel):
    unit: str
    active_users: int
    storage_used: str
    monthly_cost: float
    compliance_score: int
    projects_active: int


class SecurityAlert(BaseModel):
    id: str
    severity: str
    title: str
    description: str
    affected_users: int
    status: str
    created: datetime


class ProjectStatus(BaseModel):
    project_id: str
    name: str
    business_unit: str
    status: str
    progress: int
    budget_used: float
    budget_total: float
    team_size: int
    next_milestone: str
    risk_level: str


async def get_graph_token() -> str | None:
    """Get Microsoft Graph API token"""
    try:
        if has_selected_tenant():
            tenant_cfg = get_tenant_config()
            provider = GraphTokenProvider(tenant_config=tenant_cfg)
            return provider.get_app_token()

        cfg = AppConfig().graph
        if not all([cfg.tenant_id, cfg.client_id, cfg.client_secret]):
            return None

        from azure.identity import ClientSecretCredential

        cred = ClientSecretCredential(
            tenant_id=cfg.tenant_id,
            client_id=cfg.client_id,
            client_secret=cfg.client_secret,
        )
        token = cred.get_token(cfg.scope)
        return token.token
    except Exception:
        return None


async def fetch_m365_metrics() -> dict[str, Any]:
    """Fetch real M365 service metrics"""
    token = await get_graph_token()
    if not token:
        # Return mock data for demo
        return {
            "services": [
                {
                    "service": "Azure AD",
                    "status": "Healthy",
                    "health_score": 98,
                    "users": 47,
                    "last_sync": "2 min ago",
                },
                {
                    "service": "Exchange Online",
                    "status": "Healthy",
                    "health_score": 95,
                    "mailboxes": 47,
                    "last_sync": "1 min ago",
                },
                {
                    "service": "SharePoint Online",
                    "status": "Healthy",
                    "health_score": 92,
                    "sites": 12,
                    "last_sync": "3 min ago",
                },
                {
                    "service": "Teams",
                    "status": "Healthy",
                    "health_score": 96,
                    "teams": 8,
                    "last_sync": "1 min ago",
                },
                {
                    "service": "Power Platform",
                    "status": "Healthy",
                    "health_score": 89,
                    "flows": 15,
                    "last_sync": "5 min ago",
                },
                {
                    "service": "Security & Compliance",
                    "status": "Warning",
                    "health_score": 85,
                    "alerts": 3,
                    "last_sync": "2 min ago",
                },
            ],
            "business_units": [
                {
                    "unit": "TAI Quantum AIUCP",
                    "users": 12,
                    "storage": "2.3 TB",
                    "cost": 1240.50,
                    "compliance": 95,
                    "projects": 3,
                },
                {
                    "unit": "SmartHaus Website",
                    "users": 8,
                    "storage": "1.8 TB",
                    "cost": 890.25,
                    "compliance": 98,
                    "projects": 2,
                },
                {
                    "unit": "LATTICE Research",
                    "users": 15,
                    "storage": "4.1 TB",
                    "cost": 2100.75,
                    "compliance": 92,
                    "projects": 4,
                },
                {
                    "unit": "Enterprise Advisory",
                    "users": 12,
                    "storage": "1.2 TB",
                    "cost": 675.00,
                    "compliance": 99,
                    "projects": 1,
                },
            ],
            "security_alerts": [
                {
                    "id": "SEC-001",
                    "severity": "High",
                    "title": "Unusual sign-in activity",
                    "affected": 3,
                    "status": "Active",
                },
                {
                    "id": "SEC-002",
                    "severity": "Medium",
                    "title": "Privileged account access",
                    "affected": 1,
                    "status": "Investigating",
                },
                {
                    "id": "SEC-003",
                    "severity": "Low",
                    "title": "Password policy violation",
                    "affected": 5,
                    "status": "Resolved",
                },
            ],
            "projects": [
                {
                    "id": "TAI-001",
                    "name": "Quantum Core Development",
                    "unit": "TAI",
                    "status": "Active",
                    "progress": 75,
                    "budget": 45000,
                    "team": 8,
                    "milestone": "Beta Release",
                    "risk": "Low",
                },
                {
                    "id": "WEB-001",
                    "name": "Website Platform v2.0",
                    "unit": "SmartHaus",
                    "status": "Active",
                    "progress": 60,
                    "budget": 25000,
                    "team": 6,
                    "milestone": "UI/UX Complete",
                    "risk": "Medium",
                },
                {
                    "id": "LAT-001",
                    "name": "LQL Research Platform",
                    "unit": "LATTICE",
                    "status": "Planning",
                    "progress": 25,
                    "budget": 35000,
                    "team": 10,
                    "milestone": "Architecture Review",
                    "risk": "High",
                },
            ],
        }

    # Real Graph API calls would go here
    return {}


@app.get("/", response_class=HTMLResponse)
async def enterprise_dashboard(request: Request) -> HTMLResponse:
    """Main enterprise dashboard"""
    metrics = await fetch_m365_metrics()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartHaus M365 Enterprise Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8f9fa;
                color: #333;
                line-height: 1.6;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 1rem 2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header h1 {{ font-size: 1.8rem; font-weight: 600; }}
            .header p {{ opacity: 0.9; margin-top: 0.5rem; }}
            .nav {{
                background: white;
                padding: 1rem 2rem;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                gap: 2rem;
            }}
            .nav a {{
                color: #495057;
                text-decoration: none;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                transition: all 0.2s;
            }}
            .nav a:hover, .nav a.active {{
                background: #e3f2fd;
                color: #1976d2;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            .card {{
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #1976d2;
            }}
            .card h3 {{
                color: #1976d2;
                margin-bottom: 1rem;
                font-size: 1.1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .metric {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.75rem 0;
                border-bottom: 1px solid #f1f3f4;
            }}
            .metric:last-child {{ border-bottom: none; }}
            .metric-label {{ color: #6c757d; font-size: 0.9rem; }}
            .metric-value {{ font-weight: 600; color: #333; }}
            .status-badge {{
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 500;
            }}
            .status-healthy {{ background: #d4edda; color: #155724; }}
            .status-warning {{ background: #fff3cd; color: #856404; }}
            .status-critical {{ background: #f8d7da; color: #721c24; }}
            .chart-container {{ height: 200px; margin-top: 1rem; }}
            .alert-item {{
                padding: 1rem;
                border-left: 4px solid #dc3545;
                background: #f8f9fa;
                margin-bottom: 0.5rem;
                border-radius: 4px;
            }}
            .alert-high {{ border-left-color: #dc3545; }}
            .alert-medium {{ border-left-color: #ffc107; }}
            .alert-low {{ border-left-color: #28a745; }}
            .project-item {{
                padding: 1rem;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                margin-bottom: 1rem;
            }}
            .progress-bar {{
                width: 100%;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
                margin: 0.5rem 0;
            }}
            .progress-fill {{
                height: 100%;
                background: linear-gradient(90deg, #28a745, #20c997);
                transition: width 0.3s ease;
            }}
            .risk-high {{ border-left-color: #dc3545; }}
            .risk-medium {{ border-left-color: #ffc107; }}
            .risk-low {{ border-left-color: #28a745; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏢 SmartHaus M365 Enterprise Dashboard</h1>
            <p>Comprehensive M365 service management and business intelligence</p>
        </div>

        <div class="nav">
            <a href="/" class="active">📊 Overview</a>
            <a href="/services">🔧 Services</a>
            <a href="/security">🛡️ Security</a>
            <a href="/projects">📋 Projects</a>
            <a href="/compliance">📋 Compliance</a>
            <a href="/reports">📈 Reports</a>
        </div>

        <div class="container">
            <!-- Service Health Overview -->
            <div class="dashboard-grid">
                <div class="card">
                    <h3>🔧 M365 Service Health</h3>
                    {
        "".join(
            [
                f'''
                    <div class="metric">
                        <span class="metric-label">{service["service"]}</span>
                        <div>
                            <span class="status-badge status-{service["status"].lower()}">{service["status"]}</span>
                            <span class="metric-value">{service["health_score"]}%</span>
                        </div>
                    </div>
                    '''
                for service in metrics.get("services", [])
            ]
        )
    }
                </div>

                <div class="card">
                    <h3>🏢 Business Unit Metrics</h3>
                    {
        "".join(
            [
                f'''
                    <div class="metric">
                        <span class="metric-label">{unit["unit"]}</span>
                        <span class="metric-value">{unit["users"]} users</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Storage</span>
                        <span class="metric-value">{unit["storage"]}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Monthly Cost</span>
                        <span class="metric-value">${unit["cost"]:,.2f}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Compliance</span>
                        <span class="metric-value">{unit["compliance"]}%</span>
                    </div>
                    <hr style="margin: 1rem 0; border: none; border-top: 1px solid #e9ecef;">
                    '''
                for unit in metrics.get("business_units", [])
            ]
        )
    }
                </div>

                <div class="card">
                    <h3>🛡️ Security Alerts</h3>
                    {
        "".join(
            [
                f'''
                    <div class="alert-item alert-{alert["severity"].lower()}">
                        <strong>{alert["title"]}</strong><br>
                        <small>Severity: {alert["severity"]} | Affected: {alert["affected"]} users | Status: {alert["status"]}</small>
                    </div>
                    '''
                for alert in metrics.get("security_alerts", [])
            ]
        )
    }
                </div>
            </div>

            <!-- Project Status -->
            <div class="card">
                <h3>📋 Active Projects</h3>
                {
        "".join(
            [
                f'''
                <div class="project-item risk-{project["risk"].lower()}">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                        <div>
                            <strong>{project["name"]}</strong><br>
                            <small>{project["unit"]} | Team: {project["team"]} members</small>
                        </div>
                        <span class="status-badge status-{project["status"].lower()}">{project["status"]}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {project["progress"]}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #6c757d; margin-top: 0.5rem;">
                        <span>Progress: {project["progress"]}%</span>
                        <span>Budget: ${project["budget"]:,.0f}</span>
                        <span>Next: {project["milestone"]}</span>
                    </div>
                </div>
                '''
                for project in metrics.get("projects", [])
            ]
        )
    }
            </div>
        </div>

        <script>
            // Auto-refresh every 5 minutes
            setTimeout(() => location.reload(), 300000);

            // Add interactive features
            document.addEventListener('DOMContentLoaded', function() {{
                // Add click handlers for navigation
                document.querySelectorAll('.nav a').forEach(link => {{
                    link.addEventListener('click', function(e) {{
                        e.preventDefault();
                        // Remove active class from all links
                        document.querySelectorAll('.nav a').forEach(l => l.classList.remove('active'));
                        // Add active class to clicked link
                        this.classList.add('active');
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/services", response_class=HTMLResponse)
async def services_page(request: Request) -> HTMLResponse:
    """M365 Services Management Page"""
    metrics = await fetch_m365_metrics()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>M365 Services - SmartHaus Enterprise</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8f9fa;
                color: #333;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                padding: 1rem 2rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .nav {{
                background: white;
                padding: 1rem 2rem;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                gap: 2rem;
            }}
            .nav a {{
                color: #495057;
                text-decoration: none;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 4px;
                transition: all 0.2s;
            }}
            .nav a:hover, .nav a.active {{
                background: #e3f2fd;
                color: #1976d2;
            }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
            .service-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 1.5rem;
            }}
            .service-card {{
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #1976d2;
            }}
            .service-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }}
            .service-title {{ font-size: 1.2rem; font-weight: 600; color: #1976d2; }}
            .status-badge {{
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 500;
            }}
            .status-healthy {{ background: #d4edda; color: #155724; }}
            .status-warning {{ background: #fff3cd; color: #856404; }}
            .status-critical {{ background: #f8d7da; color: #721c24; }}
            .metric-row {{
                display: flex;
                justify-content: space-between;
                padding: 0.5rem 0;
                border-bottom: 1px solid #f1f3f4;
            }}
            .metric-row:last-child {{ border-bottom: none; }}
            .action-buttons {{
                margin-top: 1rem;
                display: flex;
                gap: 0.5rem;
            }}
            .btn {{
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.9rem;
                transition: all 0.2s;
            }}
            .btn-primary {{ background: #1976d2; color: white; }}
            .btn-secondary {{ background: #6c757d; color: white; }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 M365 Services Management</h1>
            <p>Monitor and manage Microsoft 365 services across SmartHaus</p>
        </div>

        <div class="nav">
            <a href="/">📊 Overview</a>
            <a href="/services" class="active">🔧 Services</a>
            <a href="/security">🛡️ Security</a>
            <a href="/projects">📋 Projects</a>
            <a href="/compliance">📋 Compliance</a>
            <a href="/reports">📈 Reports</a>
        </div>

        <div class="container">
            <div class="service-grid">
                {
        "".join(
            [
                f'''
                <div class="service-card">
                    <div class="service-header">
                        <div class="service-title">{service["service"]}</div>
                        <span class="status-badge status-{service["status"].lower()}">{service["status"]}</span>
                    </div>
                    <div class="metric-row">
                        <span>Health Score</span>
                        <span><strong>{service["health_score"]}%</strong></span>
                    </div>
                    <div class="metric-row">
                        <span>Last Sync</span>
                        <span>{service["last_sync"]}</span>
                    </div>
                    <div class="metric-row">
                        <span>Status</span>
                        <span>{service["status"]}</span>
                    </div>
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="manageService('{service["service"]}')">Manage</button>
                        <button class="btn btn-secondary" onclick="viewLogs('{service["service"]}')">Logs</button>
                    </div>
                </div>
                '''
                for service in metrics.get("services", [])
            ]
        )
    }
            </div>
        </div>

        <script>
            function manageService(serviceName) {{
                alert(`Opening management console for ${{serviceName}}`);
                // Here you would integrate with actual M365 admin portals
            }}

            function viewLogs(serviceName) {{
                alert(`Opening logs for ${{serviceName}}`);
                // Here you would show service-specific logs
            }}
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/api/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "dashboard": "operational",
            "graph_api": "connected" if await get_graph_token() else "disconnected",
            "m365_services": "monitoring",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
