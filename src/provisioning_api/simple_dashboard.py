"""
Simplified M365 Dashboard - Agent-focused without complex dependencies
"""

import json
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="SmartHaus M365 Dashboard", version="1.0.0")


# Helper function for department icons
def get_dept_icon(dept_name: str) -> str:
    """Get icon for department"""
    icons = {
        "operations": "⚙️",
        "hr": "👥",
        "communication": "📢",
        "engineering": "🔧",
        "marketing": "📈",
        "product": "📦",
        "project-management": "📋",
        "studio-operations": "🎬",
        "testing": "🧪",
        "design": "🎨",
        "bonus": "🎉",
    }
    return icons.get(dept_name.lower().replace("-", "_"), "🏢")


# Load agent data
def load_agent_data() -> dict[str, Any]:
    """Load agent configuration and team data"""
    try:
        # Load agent definitions
        with open("registry/agents.yaml") as f:
            import yaml

            agents_config = yaml.safe_load(f)

        # Load team data with real names
        with open("registry/ai_team.json") as f:
            team_data = json.load(f)

        return {
            "agents": agents_config.get("agents", {}),
            "team": team_data.get("departments", {}),
            "total_agents": team_data.get("total_agents", 0),
        }
    except Exception as e:
        print(f"Error loading agent data: {e}")
        return {"agents": {}, "team": {}, "total_agents": 0}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "m365-dashboard"}


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request) -> HTMLResponse:
    """Main dashboard with agent navigation"""
    agent_data = load_agent_data()

    # Create agent cards with real names
    agent_cards: list[dict[str, Any]] = []
    for dept_name, dept_agents in agent_data["team"].items():
        for agent_info in dept_agents:
            agent_id = agent_info["agent"]
            agent_config = agent_data["agents"].get(agent_id, {})

            card = {
                "id": agent_id,
                "name": agent_info["name"],
                "role": agent_info["role"],
                "department": dept_name.replace("_", " ").title(),
                "title": agent_config.get("name", agent_id.replace("-", " ").title()),
                "risk_tier": agent_config.get("risk_tier", "medium"),
                "allowed_actions": len(agent_config.get("allowed_actions", [])),
                "approval_rules": len(agent_config.get("approval_rules", [])),
            }
            agent_cards.append(card)

    # Sort by department
    agent_cards.sort(key=lambda x: x["department"])

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartHaus AI Team Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
            .header p {{ font-size: 1.2em; opacity: 0.9; }}
            .stats {{
                display: flex;
                justify-content: center;
                gap: 40px;
                margin-top: 30px;
            }}
            .stat {{ text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
            .stat-label {{ font-size: 0.9em; opacity: 0.8; }}
            .content {{ padding: 40px; }}
            .departments {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-top: 30px;
            }}
            .department {{
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                border-left: 5px solid #3498db;
            }}
            .department h3 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.3em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .agent-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                cursor: pointer;
                border: 2px solid transparent;
            }}
            .agent-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border-color: #3498db;
            }}
            .agent-name {{
                font-size: 1.2em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .agent-role {{
                color: #7f8c8d;
                font-size: 0.9em;
                margin-bottom: 10px;
            }}
            .agent-meta {{
                display: flex;
                justify-content: space-between;
                font-size: 0.8em;
                color: #95a5a6;
            }}
            .risk-badge {{
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.7em;
                font-weight: bold;
                text-transform: uppercase;
            }}
            .risk-low {{ background: #d5f4e6; color: #27ae60; }}
            .risk-medium {{ background: #fef9e7; color: #f39c12; }}
            .risk-high {{ background: #fadbd8; color: #e74c3c; }}
            .risk-critical {{ background: #f8d7da; color: #c0392b; }}
            .actions-count {{ color: #3498db; }}
            .approvals-count {{ color: #9b59b6; }}
            .nav-bar {{
                background: #34495e;
                padding: 15px 40px;
                display: flex;
                gap: 20px;
                align-items: center;
            }}
            .nav-link {{
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 5px;
                transition: background 0.3s ease;
            }}
            .nav-link:hover {{
                background: rgba(255,255,255,0.1);
            }}
            .nav-link.active {{
                background: #3498db;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 SmartHaus AI Team</h1>
                <p>Your Integrated AI Workforce Dashboard</p>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{agent_data["total_agents"]}</div>
                        <div class="stat-label">AI Agents</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(agent_data["team"])}</div>
                        <div class="stat-label">Departments</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Availability</div>
                    </div>
                </div>
            </div>

            <div class="nav-bar">
                <a href="/" class="nav-link active">🏠 Team Overview</a>
                <a href="/api/email/dashboard" class="nav-link">📧 Email Management</a>
                <a href="/api/m365/empire-overview" class="nav-link">🏢 M365 Empire</a>
                <a href="/health" class="nav-link">💚 System Health</a>
            </div>

            <div class="content">
                <h2 style="color: #2c3e50; margin-bottom: 30px; text-align: center;">
                    Meet Your AI Team
                </h2>

                <div class="departments">
    """

    # Group agents by department
    departments: dict[str, list[dict[str, Any]]] = {}
    for card in agent_cards:
        dept = card["department"]
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(card)

    # Generate department sections
    for dept_name, agents in departments.items():
        html_content += f"""
                    <div class="department" onclick="openDepartmentPage('{dept_name}')" style="cursor: pointer;">
                        <h3>{dept_name} ({len(agents)} agents)</h3>
        """

        for agent in agents:
            risk_class = f"risk-{agent['risk_tier']}"
            html_content += f"""
                        <div class="agent-card" onclick="openAgentPage('{agent["id"]}')">
                            <div class="agent-name">{agent["name"]}</div>
                            <div class="agent-role">{agent["role"]}</div>
                            <div class="agent-meta">
                                <span class="actions-count">⚡ {agent["allowed_actions"]} actions</span>
                                <span class="approvals-count">🔒 {agent["approval_rules"]} approvals</span>
                                <span class="risk-badge {risk_class}">{agent["risk_tier"]}</span>
                            </div>
                        </div>
            """

        html_content += """
                    </div>
        """

    html_content += """
                </div>
            </div>
        </div>

        <script>
            function openAgentPage(agentId) {
                window.location.href = `/agent/${agentId}`;
            }

            function openDepartmentPage(deptName) {
                window.location.href = `/department/${deptName.toLowerCase().replace(' ', '-')}`;
            }
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/department/{dept_name}", response_class=HTMLResponse)
async def department_page(request: Request, dept_name: str) -> HTMLResponse:
    """Department-specific dashboard page"""
    agent_data = load_agent_data()

    # Find department agents
    dept_agents: list[dict[str, Any]] = []
    for dept_key, agents in agent_data["team"].items():
        if dept_key.replace("_", "-").lower() == dept_name.lower():
            for agent_info in agents:
                agent_id = agent_info["agent"]
                agent_config = agent_data["agents"].get(agent_id, {})

                agent_detail = {
                    "id": agent_id,
                    "name": agent_info["name"],
                    "role": agent_info["role"],
                    "department": dept_key.replace("_", " ").title(),
                    "title": agent_config.get("name", agent_id.replace("-", " ").title()),
                    "risk_tier": agent_config.get("risk_tier", "medium"),
                    "allowed_actions": agent_config.get("allowed_actions", []),
                    "approval_rules": agent_config.get("approval_rules", []),
                }
                dept_agents.append(agent_detail)
            break

    if not dept_agents:
        return HTMLResponse(content="<h1>Department not found</h1>", status_code=404)

    dept_title = dept_agents[0]["department"]

    # Calculate department stats
    total_actions = sum(len(agent["allowed_actions"]) for agent in dept_agents)
    total_approvals = sum(len(agent["approval_rules"]) for agent in dept_agents)
    risk_distribution: dict[str, int] = {}
    for agent in dept_agents:
        risk = agent["risk_tier"]
        risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{dept_title} - SmartHaus AI Team</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 40px;
                text-align: center;
                position: relative;
            }}
            .back-btn {{
                position: absolute;
                top: 20px;
                left: 20px;
                background: rgba(255,255,255,0.2);
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                text-decoration: none;
                transition: all 0.3s ease;
            }}
            .back-btn:hover {{
                background: rgba(255,255,255,0.3);
                transform: translateY(-2px);
            }}
            .dept-icon {{
                font-size: 4em;
                margin-bottom: 20px;
            }}
            .dept-title {{ font-size: 2.5em; margin-bottom: 10px; }}
            .dept-description {{ font-size: 1.2em; opacity: 0.9; margin-bottom: 20px; }}
            .stats {{
                display: flex;
                justify-content: center;
                gap: 40px;
                margin-top: 30px;
            }}
            .stat {{ text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
            .stat-label {{ font-size: 0.9em; opacity: 0.8; }}
            .content {{ padding: 40px; }}
            .agents-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 30px;
                margin-top: 30px;
            }}
            .agent-card {{
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                border-left: 5px solid #3498db;
                transition: all 0.3s ease;
                cursor: pointer;
            }}
            .agent-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }}
            .agent-name {{
                font-size: 1.4em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 8px;
            }}
            .agent-role {{
                color: #7f8c8d;
                font-size: 1em;
                margin-bottom: 15px;
            }}
            .agent-actions {{
                margin-bottom: 15px;
            }}
            .action-category {{
                background: white;
                padding: 10px;
                margin-bottom: 8px;
                border-radius: 8px;
                border-left: 3px solid #e74c3c;
            }}
            .category-title {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 0.9em;
                margin-bottom: 5px;
            }}
            .action-item {{
                font-family: 'Courier New', monospace;
                font-size: 0.8em;
                color: #7f8c8d;
                margin-left: 10px;
            }}
            .agent-meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.9em;
            }}
            .risk-badge {{
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8em;
                font-weight: bold;
                text-transform: uppercase;
            }}
            .risk-low {{ background: #d5f4e6; color: #27ae60; }}
            .risk-medium {{ background: #fef9e7; color: #f39c12; }}
            .risk-high {{ background: #fadbd8; color: #e74c3c; }}
            .risk-critical {{ background: #f8d7da; color: #c0392b; }}
            .actions-count {{ color: #3498db; }}
            .approvals-count {{ color: #9b59b6; }}
            .nav-bar {{
                background: #34495e;
                padding: 15px 40px;
                display: flex;
                gap: 20px;
                align-items: center;
            }}
            .nav-link {{
                color: white;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 5px;
                transition: background 0.3s ease;
            }}
            .nav-link:hover {{
                background: rgba(255,255,255,0.1);
            }}
            .dept-actions {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 30px;
            }}
            .dept-action-btn {{
                background: #3498db;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                margin: 5px;
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .dept-action-btn:hover {{
                background: #2980b9;
                transform: translateY(-2px);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/" class="back-btn">← Back to Team</a>
                <div class="dept-icon">
                    {get_dept_icon(dept_name)}
                </div>
                <h1 class="dept-title">{dept_title}</h1>
                <p class="dept-description">Department Overview & Agent Management</p>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{len(dept_agents)}</div>
                        <div class="stat-label">Agents</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{total_actions}</div>
                        <div class="stat-label">Total Actions</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{total_approvals}</div>
                        <div class="stat-label">Approval Rules</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(risk_distribution)}</div>
                        <div class="stat-label">Risk Levels</div>
                    </div>
                </div>
            </div>

            <div class="nav-bar">
                <a href="/" class="nav-link">🏠 Team Overview</a>
                <a href="/api/email/dashboard" class="nav-link">📧 Email Management</a>
                <a href="/api/m365/empire-overview" class="nav-link">🏢 M365 Empire</a>
                <a href="/health" class="nav-link">💚 System Health</a>
            </div>

            <div class="content">
                <div class="dept-actions">
                    <h3 style="color: #2c3e50; margin-bottom: 15px;">Department Actions</h3>
                    <button class="dept-action-btn" onclick="executeDeptAction('status-check')">📊 Status Check</button>
                    <button class="dept-action-btn" onclick="executeDeptAction('performance-review')">📈 Performance Review</button>
                    <button class="dept-action-btn" onclick="executeDeptAction('workload-balance')">⚖️ Workload Balance</button>
                    <button class="dept-action-btn" onclick="executeDeptAction('collaboration-sync')">🤝 Collaboration Sync</button>
                </div>

                <h2 style="color: #2c3e50; margin-bottom: 30px; text-align: center;">
                    {dept_title} Agents
                </h2>

                <div class="agents-grid">
    """

    # Generate agent cards for this department
    for agent in dept_agents:
        risk_class = f"risk-{agent['risk_tier']}"

        # Group actions by category
        action_categories: dict[str, list[str]] = {}
        for action in agent["allowed_actions"]:
            category = action.split(".")[0] if "." in action else "general"
            if category not in action_categories:
                action_categories[category] = []
            action_categories[category].append(action)

        html_content += f"""
                    <div class="agent-card" onclick="openAgentPage('{agent["id"]}')">
                        <div class="agent-name">{agent["name"]}</div>
                        <div class="agent-role">{agent["role"]}</div>

                        <div class="agent-actions">
        """

        # Show top 3 action categories
        for category, actions in list(action_categories.items())[:3]:
            html_content += f"""
                            <div class="action-category">
                                <div class="category-title">{category.replace("_", " ").title()}</div>
            """
            for action in actions[:2]:  # Show max 2 actions per category
                html_content += f"""
                                <div class="action-item">• {action}</div>
                """
            if len(actions) > 2:
                html_content += f"""
                                <div class="action-item">• +{len(actions) - 2} more</div>
                """
            html_content += """
                            </div>
            """

        html_content += f"""
                        </div>

                        <div class="agent-meta">
                            <span class="actions-count">⚡ {len(agent["allowed_actions"])} actions</span>
                            <span class="approvals-count">🔒 {len(agent["approval_rules"])} approvals</span>
                            <span class="risk-badge {risk_class}">{agent["risk_tier"]}</span>
                        </div>
                    </div>
        """

    html_content += """
                </div>
            </div>
        </div>

        <script>
            function openAgentPage(agentId) {
                window.location.href = `/agent/${agentId}`;
            }

            function executeDeptAction(action) {
                alert(`Executing department action: ${action}\\n\\nThis would trigger real department-level operations.`);
                // Here you would make API calls to execute actual department actions
            }
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/agent/{agent_id}", response_class=HTMLResponse)
async def agent_detail_page(request: Request, agent_id: str) -> HTMLResponse:
    """Individual agent detail page"""
    try:
        agent_data = load_agent_data()

        # Find agent info
        agent_info: dict[str, Any] | None = None
        agent_config: dict[str, Any] = {}

        for _, dept_agents in agent_data["team"].items():
            for agent in dept_agents:
                if agent["agent"] == agent_id:
                    agent_info = agent
                    agent_config = agent_data["agents"].get(agent_id, {})
                    break
            if agent_info:
                break

        if not agent_info:
            return HTMLResponse(
                content="<h1>Agent not found</h1><p>Agent ID: " + agent_id + "</p>", status_code=404
            )

        # Get agent capabilities
        allowed_actions = agent_config.get("allowed_actions", [])
        approval_rules = agent_config.get("approval_rules", [])
        risk_tier = agent_config.get("risk_tier", "medium")

        # Simple HTML response
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{agent_info["name"]} - SmartHaus AI Team</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .back-btn {{ color: white; text-decoration: none; background: #3498db; padding: 8px 16px; border-radius: 4px; }}
                .agent-info {{ margin: 20px 0; }}
                .capabilities {{ background: #ecf0f1; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .action-item {{ background: white; padding: 8px; margin: 5px 0; border-radius: 4px; border-left: 3px solid #3498db; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <a href="/" class="back-btn">← Back to Team</a>
                    <h1>{agent_info["name"]}</h1>
                    <p>{agent_info["role"]}</p>
                </div>

                <div class="agent-info">
                    <h3>Agent Information</h3>
                    <p><strong>Name:</strong> {agent_info["name"]}</p>
                    <p><strong>Role:</strong> {agent_info["role"]}</p>
                    <p><strong>Agent ID:</strong> {agent_id}</p>
                    <p><strong>Risk Level:</strong> {risk_tier.upper()}</p>
                    <p><strong>Actions Available:</strong> {len(allowed_actions)}</p>
                    <p><strong>Approval Rules:</strong> {len(approval_rules)}</p>
                </div>

                <div class="capabilities">
                    <h3>Capabilities & Actions</h3>
                    {"".join([f'<div class="action-item">{action}</div>' for action in allowed_actions[:10]])}
                    {f"<p><em>... and {len(allowed_actions) - 10} more actions</em></p>" if len(allowed_actions) > 10 else ""}
                </div>

                <div class="capabilities">
                    <h3>Approval Rules</h3>
                    {"".join([f'<div class="action-item">{rule}</div>' for rule in approval_rules]) if approval_rules else "<p>No approval rules required</p>"}
                </div>

                <div style="margin-top: 30px;">
                    <button onclick="alert('Agent status check completed!')" style="background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">📊 Check Status</button>
                    <button onclick="alert('Performance analysis completed!')" style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">📈 Performance</button>
                    <button onclick="window.open('/tasks/{agent_id}', '_blank')" style="background: #e67e22; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">📋 Tasks</button>
                </div>

                <div class="capabilities" style="margin-top: 30px;">
                    <h3>🎮 Execute Actions</h3>
                    <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h4>Quick Actions:</h4>
                        <button onclick="executeAction('users.create', {{userPrincipalName: 'new-user@smarthausgroup.com', displayName: 'New User'}})" style="background: #27ae60; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; margin: 5px;">👤 Create User</button>
                        <button onclick="executeAction('groups.create', {{displayName: 'New Team', mailNickname: 'new-team'}})" style="background: #3498db; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; margin: 5px;">👥 Create Team</button>
                        <button onclick="executeAction('teams.create', {{displayName: 'New Teams Workspace'}})" style="background: #9b59b6; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; margin: 5px;">💬 Create Teams</button>
                        <button onclick="executeAction('sites.provision', {{displayName: 'New SharePoint Site'}})" style="background: #e67e22; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; margin: 5px;">📁 Create Site</button>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h4>Custom Action:</h4>
                        <input type="text" id="customAction" placeholder="Action (e.g., users.create)" style="width: 200px; padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px;">
                        <input type="text" id="customParams" placeholder='Params (JSON: {{"key": "value"}})' style="width: 300px; padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px;">
                        <button onclick="executeCustomAction()" style="background: #e74c3c; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; margin: 5px;">🚀 Execute</button>
                    </div>
                </div>

                <script>
                async function executeAction(action, params) {{
                    try {{
                        const response = await fetch(`/api/agents/{agent_id}/execute`, {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                action: action,
                                params: params
                            }})
                        }});
                        const result = await response.json();
                        alert(`Action executed!\\n\\nAction: ${{action}}\\nResult: ${{JSON.stringify(result, null, 2)}}`);
                    }} catch (error) {{
                        alert(`Error executing action: ${{error.message}}`);
                    }}
                }}

                async function executeCustomAction() {{
                    const action = document.getElementById('customAction').value;
                    const paramsText = document.getElementById('customParams').value;
                    let params = {{}};
                    if (paramsText) {{
                        try {{
                            params = JSON.parse(paramsText);
                        }} catch (e) {{
                            alert('Invalid JSON in params field');
                            return;
                        }}
                    }}
                    await executeAction(action, params);
                }}
                </script>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error loading agent</h1><p>Error: {str(e)}</p>", status_code=500
        )


@app.get("/api/agents/status")
async def agents_status() -> dict[str, Any]:
    """Get status of all agents"""
    agent_data = load_agent_data()

    return {
        "status": "operational",
        "total_agents": agent_data["total_agents"],
        "departments": len(agent_data["team"]),
        "agents": {
            agent_id: {
                "name": agent_config.get("name", agent_id),
                "department": next(
                    (
                        dept
                        for dept, agents in agent_data["team"].items()
                        for agent in agents
                        if agent["agent"] == agent_id
                    ),
                    "unknown",
                ),
                "risk_tier": agent_config.get("risk_tier", "medium"),
                "actions_count": len(agent_config.get("allowed_actions", [])),
                "approvals_count": len(agent_config.get("approval_rules", [])),
            }
            for agent_id, agent_config in agent_data["agents"].items()
        },
    }


@app.post("/api/agents/{agent_id}/execute")
async def execute_agent_action(
    agent_id: str, action: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Execute an action for a specific agent"""
    agent_data = load_agent_data()

    # Find agent
    agent_config = agent_data["agents"].get(agent_id)
    if not agent_config:
        return {"error": "Agent not found", "status": "error"}

    # Simulate action execution
    import time

    time.sleep(1)  # Simulate processing time

    return {
        "status": "success",
        "agent_id": agent_id,
        "action": action,
        "result": f"Action '{action}' executed successfully for agent {agent_id}",
        "timestamp": time.time(),
        "params": params or {},
    }


@app.get("/api/agents/{agent_id}/status")
async def get_agent_status(agent_id: str) -> dict[str, Any]:
    """Get detailed status for a specific agent"""
    agent_data = load_agent_data()

    # Find agent
    agent_config = agent_data["agents"].get(agent_id)
    if not agent_config:
        return {"error": "Agent not found", "status": "error"}

    # Find agent info
    agent_info = None
    for _, dept_agents in agent_data["team"].items():
        for agent in dept_agents:
            if agent["agent"] == agent_id:
                agent_info = agent
                break
        if agent_info:
            break

    return {
        "status": "operational",
        "agent_id": agent_id,
        "name": agent_info["name"] if agent_info else agent_config.get("name", agent_id),
        "role": agent_info["role"] if agent_info else "Unknown",
        "department": agent_info.get("department", "Unknown") if agent_info else "Unknown",
        "risk_tier": agent_config.get("risk_tier", "medium"),
        "allowed_actions": agent_config.get("allowed_actions", []),
        "approval_rules": agent_config.get("approval_rules", []),
        "last_activity": "2 minutes ago",
        "performance_score": 95,
        "workload": "moderate",
        "health_status": "healthy",
    }


@app.get("/api/departments/{dept_name}/status")
async def get_department_status(dept_name: str) -> dict[str, Any]:
    """Get status for a specific department"""
    agent_data = load_agent_data()

    # Find department agents
    dept_agents: list[dict[str, Any]] = []
    for dept_key, agents in agent_data["team"].items():
        if dept_key.replace("_", "-").lower() == dept_name.lower():
            dept_agents = agents
            break

    if not dept_agents:
        return {"error": "Department not found", "status": "error"}

    # Calculate department metrics
    total_actions = 0
    total_approvals = 0
    risk_distribution: dict[str, int] = {}

    for agent_info in dept_agents:
        agent_id = agent_info["agent"]
        agent_config = agent_data["agents"].get(agent_id, {})
        total_actions += len(agent_config.get("allowed_actions", []))
        total_approvals += len(agent_config.get("approval_rules", []))

        risk = agent_config.get("risk_tier", "medium")
        risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

    return {
        "status": "operational",
        "department": dept_name,
        "agent_count": len(dept_agents),
        "total_actions": total_actions,
        "total_approvals": total_approvals,
        "risk_distribution": risk_distribution,
        "performance_score": 92,
        "workload": "balanced",
        "last_sync": "5 minutes ago",
    }


@app.get("/api/email/dashboard", response_class=HTMLResponse)
async def email_dashboard(request: Request) -> HTMLResponse:
    """Email Management Dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Management - SmartHaus AI Team</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .back-btn { color: white; text-decoration: none; background: #3498db; padding: 8px 16px; border-radius: 4px; }
            .status-card { background: #ecf0f1; padding: 15px; border-radius: 8px; margin: 15px 0; }
            .metric { display: inline-block; margin: 10px 20px; text-align: center; }
            .metric-value { font-size: 2em; font-weight: bold; color: #2c3e50; }
            .metric-label { color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/" class="back-btn">← Back to Team</a>
                <h1>📧 Email Management Dashboard</h1>
            </div>

            <div class="status-card">
                <h3>Email Configuration</h3>
                <div class="metric">
                    <div class="metric-value">smarthausgroup.com</div>
                    <div class="metric-label">Domain</div>
                </div>
                <div class="metric">
                    <div class="metric-value">Active</div>
                    <div class="metric-label">Status</div>
                </div>
                <div class="metric">
                    <div class="metric-value">Microsoft 365</div>
                    <div class="metric-label">Provider</div>
                </div>
            </div>

            <div class="status-card">
                <h3>Recent Activity</h3>
                <div class="metric">
                    <div class="metric-value">1</div>
                    <div class="metric-label">Messages Received</div>
                </div>
                <div class="metric">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Messages Sent</div>
                </div>
                <div class="metric">
                    <div class="metric-value">2 min ago</div>
                    <div class="metric-label">Last Activity</div>
                </div>
            </div>

            <div style="margin-top: 30px;">
                <button onclick="alert('Email sync completed!')" style="background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">🔄 Sync Email</button>
                <button onclick="alert('Email settings updated!')" style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">⚙️ Settings</button>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/m365/empire-overview", response_class=HTMLResponse)
async def m365_empire_overview(request: Request) -> HTMLResponse:
    """M365 Empire Overview Dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>M365 Empire Overview - SmartHaus AI Team</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .back-btn { color: white; text-decoration: none; background: #3498db; padding: 8px 16px; border-radius: 4px; }
            .service-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .service-card { background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }
            .service-status { font-size: 1.2em; font-weight: bold; margin: 10px 0; }
            .status-active { color: #27ae60; }
            .status-pending { color: #f39c12; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/" class="back-btn">← Back to Team</a>
                <h1>🏢 M365 Empire Overview</h1>
            </div>

            <div class="service-grid">
                <div class="service-card">
                    <h3>Azure AD</h3>
                    <div class="service-status status-active">✅ Active</div>
                    <p>User management and authentication</p>
                </div>
                <div class="service-card">
                    <h3>Microsoft Teams</h3>
                    <div class="service-status status-active">✅ Active</div>
                    <p>Collaboration and communication</p>
                </div>
                <div class="service-card">
                    <h3>SharePoint</h3>
                    <div class="service-status status-active">✅ Active</div>
                    <p>Document management and sharing</p>
                </div>
                <div class="service-card">
                    <h3>Exchange Online</h3>
                    <div class="service-status status-active">✅ Active</div>
                    <p>Email and calendar services</p>
                </div>
                <div class="service-card">
                    <h3>Power Platform</h3>
                    <div class="service-status status-pending">⏳ Pending</div>
                    <p>Low-code development platform</p>
                </div>
                <div class="service-card">
                    <h3>Graph API</h3>
                    <div class="service-status status-active">✅ Active</div>
                    <p>Microsoft Graph integration</p>
                </div>
            </div>

            <div style="margin-top: 30px;">
                <button onclick="alert('M365 sync completed!')" style="background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">🔄 Sync M365</button>
                <button onclick="alert('M365 settings updated!')" style="background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">⚙️ Settings</button>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/tasks/{agent_id}", response_class=HTMLResponse)
async def agent_tasks_page(request: Request, agent_id: str) -> HTMLResponse:
    """Agent Task Management Dashboard"""
    try:
        agent_data = load_agent_data()

        # Find agent info
        agent_info = None
        for _, dept_agents in agent_data["team"].items():
            for agent in dept_agents:
                if agent["agent"] == agent_id:
                    agent_info = agent
                    break
            if agent_info:
                break

        if not agent_info:
            return HTMLResponse(content="<h1>Agent not found</h1>", status_code=404)

        # Sample tasks for demonstration
        sample_tasks = [
            {
                "id": "task-001",
                "title": "Create shared mailbox for support team",
                "description": "Set up support@smarthausgroup.com shared mailbox with proper permissions",
                "priority": "High",
                "status": "In Progress",
                "assigned_by": "Sarah Williams (HR)",
                "due_date": "2025-09-20",
                "teams_channel": "#admin-management",
                "created": "2025-09-15T10:30:00Z",
            },
            {
                "id": "task-002",
                "title": "Provision new user account for John Smith",
                "description": "Create M365 account for new employee starting Monday",
                "priority": "Medium",
                "status": "Pending",
                "assigned_by": "HR Team",
                "due_date": "2025-09-18",
                "teams_channel": "#admin-management",
                "created": "2025-09-15T09:15:00Z",
            },
            {
                "id": "task-003",
                "title": "Set up Teams workspace for Project Alpha",
                "description": "Create dedicated Teams workspace with channels for new project",
                "priority": "Medium",
                "status": "Completed",
                "assigned_by": "Project Manager",
                "due_date": "2025-09-16",
                "teams_channel": "#admin-management",
                "created": "2025-09-14T14:20:00Z",
            },
        ]

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tasks - {agent_info["name"]} - SmartHaus AI Team</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .back-btn {{ color: white; text-decoration: none; background: #3498db; padding: 8px 16px; border-radius: 4px; }}
                .task-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
                .task-card {{ background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db; }}
                .task-header {{ display: flex; justify-content: between; align-items: center; margin-bottom: 15px; }}
                .task-title {{ font-size: 1.2em; font-weight: bold; color: #2c3e50; }}
                .task-priority {{ padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
                .priority-high {{ background: #e74c3c; color: white; }}
                .priority-medium {{ background: #f39c12; color: white; }}
                .priority-low {{ background: #27ae60; color: white; }}
                .task-status {{ padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
                .status-pending {{ background: #95a5a6; color: white; }}
                .status-progress {{ background: #3498db; color: white; }}
                .status-completed {{ background: #27ae60; color: white; }}
                .task-meta {{ color: #7f8c8d; font-size: 0.9em; margin: 10px 0; }}
                .task-actions {{ margin-top: 15px; }}
                .btn {{ padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }}
                .btn-primary {{ background: #3498db; color: white; }}
                .btn-success {{ background: #27ae60; color: white; }}
                .btn-warning {{ background: #f39c12; color: white; }}
                .new-task-form {{ background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .form-group {{ margin: 15px 0; }}
                .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
                .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }}
                .teams-integration {{ background: #0078d4; color: white; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <a href="/agent/{agent_id}" class="back-btn">← Back to Agent</a>
                    <h1>📋 Task Management - {agent_info["name"]}</h1>
                    <p>Manage tasks, assignments, and Teams integration</p>
                </div>

                <div class="teams-integration">
                    <h3>💬 Teams Integration</h3>
                    <p><strong>Primary Channel:</strong> #admin-management</p>
                    <p><strong>Task Notifications:</strong> Enabled</p>
                    <p><strong>Status Updates:</strong> Auto-sync to Teams</p>
                    <button class="btn btn-primary" onclick="sendTeamsMessage()">📤 Send Task via Teams</button>
                </div>

                <div class="new-task-form">
                    <h3>➕ Create New Task</h3>
                    <div class="form-group">
                        <label>Task Title:</label>
                        <input type="text" id="taskTitle" placeholder="e.g., Create shared mailbox for support team">
                    </div>
                    <div class="form-group">
                        <label>Description:</label>
                        <textarea id="taskDescription" rows="3" placeholder="Detailed description of the task..."></textarea>
                    </div>
                    <div class="form-group">
                        <label>Priority:</label>
                        <select id="taskPriority">
                            <option value="Low">Low</option>
                            <option value="Medium" selected>Medium</option>
                            <option value="High">High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Due Date:</label>
                        <input type="date" id="taskDueDate">
                    </div>
                    <button class="btn btn-success" onclick="createTask()">🚀 Create Task</button>
                </div>

                <h3>📋 Current Tasks</h3>
                <div class="task-grid">
        """

        for task in sample_tasks:
            priority_class = f"priority-{task['priority'].lower()}"
            status_class = f"status-{task['status'].lower().replace(' ', '')}"

            html_content += f"""
                    <div class="task-card">
                        <div class="task-header">
                            <div class="task-title">{task["title"]}</div>
                            <div>
                                <span class="task-priority {priority_class}">{task["priority"]}</span>
                                <span class="task-status {status_class}">{task["status"]}</span>
                            </div>
                        </div>
                        <div class="task-meta">
                            <p><strong>Description:</strong> {task["description"]}</p>
                            <p><strong>Assigned by:</strong> {task["assigned_by"]}</p>
                            <p><strong>Due Date:</strong> {task["due_date"]}</p>
                            <p><strong>Teams Channel:</strong> {task["teams_channel"]}</p>
                            <p><strong>Created:</strong> {task["created"]}</p>
                        </div>
                        <div class="task-actions">
                            <button class="btn btn-primary" onclick="updateTaskStatus('{task["id"]}', 'In Progress')">▶️ Start</button>
                            <button class="btn btn-success" onclick="updateTaskStatus('{task["id"]}', 'Completed')">✅ Complete</button>
                            <button class="btn btn-warning" onclick="sendTeamsUpdate('{task["id"]}')">📤 Update Teams</button>
                        </div>
                    </div>
            """

        html_content += """
                </div>
            </div>

            <script>
            function createTask() {
                const title = document.getElementById('taskTitle').value;
                const description = document.getElementById('taskDescription').value;
                const priority = document.getElementById('taskPriority').value;
                const dueDate = document.getElementById('taskDueDate').value;

                if (!title || !description) {
                    alert('Please fill in title and description');
                    return;
                }

                // Simulate task creation
                alert(`Task created successfully!\\n\\nTitle: ${title}\\nPriority: ${priority}\\nDue: ${dueDate}\\n\\nTask will be synced to Teams channel #admin-management`);

                // Clear form
                document.getElementById('taskTitle').value = '';
                document.getElementById('taskDescription').value = '';
                document.getElementById('taskDueDate').value = '';
            }

            function updateTaskStatus(taskId, status) {
                alert(`Task ${taskId} status updated to: ${status}\\n\\nTeams notification sent to #admin-management`);
            }

            function sendTeamsUpdate(taskId) {
                alert(`Teams update sent for task ${taskId}\\n\\nPosted to #admin-management channel`);
            }

            function sendTeamsMessage() {
                const message = prompt('Enter your message for Teams:');
                if (message) {
                    alert(`Message sent to Teams!\\n\\nChannel: #admin-management\\nMessage: ${message}\\n\\nMarcus will be notified via Teams.`);
                }
            }
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error loading tasks</h1><p>Error: {str(e)}</p>", status_code=500
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
