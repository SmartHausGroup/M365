"""
Agent Dashboard Router - Integrated dashboard with agent-specific pages
"""
import json
import os
from typing import Dict, List, Any
import time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api/agents", tags=["agent-dashboard"])
from provisioning_api.storage import JsonStore

# Load agent data
def load_agent_data() -> Dict[str, Any]:
    """Load agent configuration and team data"""
    try:
        # Load agent definitions
        with open("registry/agents.yaml", "r") as f:
            import yaml
            agents_config = yaml.safe_load(f)
        
        # Load team data with real names
        with open("registry/ai_team.json", "r") as f:
            team_data = json.load(f)
        
        return {
            "agents": agents_config.get("agents", {}),
            "team": team_data.get("departments", {}),
            "total_agents": team_data.get("total_agents", 0)
        }
    except Exception as e:
        print(f"Error loading agent data: {e}")
        return {"agents": {}, "team": {}, "total_agents": 0}

@router.get("/dashboard", response_class=HTMLResponse)
async def agent_dashboard(request: Request):
    """Main agent dashboard with navigation to individual agents"""
    agent_data = load_agent_data()
    
    # Create agent cards with real names
    agent_cards = []
    for dept_name, dept_agents in agent_data["team"].items():
        for agent_info in dept_agents:
            agent_id = agent_info["agent"]
            agent_config = agent_data["agents"].get(agent_id, {})
            
            card = {
                "id": agent_id,
                "name": agent_info["name"],
                "role": agent_info["role"],
                "department": dept_name.replace("_", " ").replace("-", " ").title(),
                "title": agent_config.get("name", agent_id.replace("-", " ").title()),
                "risk_tier": agent_config.get("risk_tier", "medium"),
                "allowed_actions": len(agent_config.get("allowed_actions", [])),
                "approval_rules": len(agent_config.get("approval_rules", []))
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
                        <div class="stat-number">{agent_data['total_agents']}</div>
                        <div class="stat-label">AI Agents</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{len(agent_data['team'])}</div>
                        <div class="stat-label">Departments</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Availability</div>
                    </div>
                </div>
            </div>
            
            <div class="nav-bar">
                <a href="/api/agents/dashboard" class="nav-link active">🏠 Team Overview</a>
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
    departments = {}
    for card in agent_cards:
        dept = card["department"]
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(card)
    
    # Generate department sections
    for dept_name, agents in departments.items():
        html_content += f"""
                    <div class="department">
                        <h3>{dept_name}</h3>
        """
        
        for agent in agents:
            risk_class = f"risk-{agent['risk_tier']}"
            html_content += f"""
                        <div class="agent-card" onclick="openAgentPage('{agent['id']}')">
                            <div class="agent-name">{agent['name']}</div>
                            <div class="agent-role">{agent['role']}</div>
                            <div class="agent-meta">
                                <span class="actions-count">⚡ {agent['allowed_actions']} actions</span>
                                <span class="approvals-count">🔒 {agent['approval_rules']} approvals</span>
                                <span class="risk-badge {risk_class}">{agent['risk_tier']}</span>
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
                window.location.href = `/api/agents/${agentId}`;
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

# Place the status route before dynamic /{agent_id} routes to avoid conflicts
@router.get("/status")
async def agents_status_root():
    """Get status of all agents (top-level to avoid /{agent_id} catch-all)."""
    agent_data = load_agent_data()
    agents_status: Dict[str, Any] = {}
    for dept, members in agent_data.get("team", {}).items():
        for a in members:
            aid = a.get("agent")
            cfg = agent_data.get("agents", {}).get(aid, {})
            agents_status[aid] = {
                "name": cfg.get("name", aid.replace("-", " ").title()),
                "department": dept,
                "risk_tier": cfg.get("risk_tier", "medium"),
                "actions_count": len(cfg.get("allowed_actions", [])),
                "approvals_count": len(cfg.get("approval_rules", [])),
            }
    return {
        "status": "operational",
        "total_agents": agent_data.get("total_agents", len(agents_status)),
        "departments": len(agent_data.get("team", {})),
        "agents": agents_status,
    }

@router.get("/{agent_id}", response_class=HTMLResponse)
async def agent_detail_page(request: Request, agent_id: str):
    """Individual agent detail page"""
    agent_data = load_agent_data()
    
    # Find agent info
    agent_info = None
    agent_config = None
    
    for dept_name, dept_agents in agent_data["team"].items():
        for agent in dept_agents:
            if agent["agent"] == agent_id:
                agent_info = agent
                agent_config = agent_data["agents"].get(agent_id, {})
                break
        if agent_info:
            break
    
    if not agent_info:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get agent capabilities
    allowed_actions = agent_config.get("allowed_actions", [])
    approval_rules = agent_config.get("approval_rules", [])
    risk_tier = agent_config.get("risk_tier", "medium")
    
    # Generate action categories
    action_categories = {}
    for action in allowed_actions:
        category = action.split(".")[0] if "." in action else "general"
        if category not in action_categories:
            action_categories[category] = []
        action_categories[category].append(action)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent_info['name']} - SmartHaus AI Team</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{ 
                max-width: 1200px; 
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
            .agent-avatar {{
                width: 120px;
                height: 120px;
                background: linear-gradient(135deg, #3498db, #9b59b6);
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 3em;
                color: white;
            }}
            .agent-name {{ font-size: 2.5em; margin-bottom: 10px; }}
            .agent-role {{ font-size: 1.3em; opacity: 0.9; margin-bottom: 20px; }}
            .agent-dept {{ 
                background: rgba(255,255,255,0.2);
                padding: 8px 20px;
                border-radius: 20px;
                display: inline-block;
                font-size: 0.9em;
            }}
            .content {{ padding: 40px; }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                text-align: center;
                border-left: 5px solid #3498db;
            }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
            .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
            .section {{
                margin-bottom: 40px;
            }}
            .section h3 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.5em;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 10px;
            }}
            .action-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}
            .action-category {{
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                border-left: 5px solid #e74c3c;
            }}
            .category-title {{
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .action-item {{
                background: white;
                padding: 12px 15px;
                margin-bottom: 8px;
                border-radius: 8px;
                border-left: 3px solid #3498db;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            .approval-rules {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 10px;
                padding: 20px;
            }}
            .approval-rule {{
                background: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 8px;
                border-left: 4px solid #f39c12;
            }}
            .risk-badge {{
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
                text-transform: uppercase;
                display: inline-block;
                margin-top: 10px;
            }}
            .risk-{risk_tier} {{
                background: {'#d5f4e6; color: #27ae60;' if risk_tier == 'low' else 
                           '#fef9e7; color: #f39c12;' if risk_tier == 'medium' else
                           '#fadbd8; color: #e74c3c;' if risk_tier == 'high' else
                           '#f8d7da; color: #c0392b;'}
            }}
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header" style="position: relative;">
                <a href="/api/agents/dashboard" class="back-btn">← Back to Team</a>
                <div class="agent-avatar">
                    {agent_info['name'][0].upper()}
                </div>
                <h1 class="agent-name">{agent_info['name']}</h1>
                <p class="agent-role">{agent_info['role']}</p>
                <div class="agent-dept">{agent_info['department'].replace('_', ' ').title()}</div>
                <div class="risk-badge risk-{risk_tier}">Risk: {risk_tier}</div>
            </div>
            
            <div class="nav-bar">
                <a href="/api/agents/dashboard" class="nav-link">🏠 Team Overview</a>
                <a href="/api/email/dashboard" class="nav-link">📧 Email Management</a>
                <a href="/api/m365/empire-overview" class="nav-link">🏢 M365 Empire</a>
                <a href="/health" class="nav-link">💚 System Health</a>
            </div>
            
            <div class="content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{len(allowed_actions)}</div>
                        <div class="stat-label">Allowed Actions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(approval_rules)}</div>
                        <div class="stat-label">Approval Rules</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(action_categories)}</div>
                        <div class="stat-label">Action Categories</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{risk_tier.upper()}</div>
                        <div class="stat-label">Risk Level</div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>🎯 Capabilities & Actions</h3>
                    <div class="action-grid">
    """
    
    # Generate action categories
    for category, actions in action_categories.items():
        html_content += f"""
                        <div class="action-category">
                            <div class="category-title">{category.replace('_', ' ').title()}</div>
        """
        for action in actions:
            html_content += f"""
                            <div class="action-item">{action}</div>
            """
        html_content += """
                        </div>
        """
    
    html_content += """
                    </div>
                </div>
    """
    
    # Add approval rules if any
    if approval_rules:
        html_content += """
                <div class="section">
                    <h3>🔒 Approval Rules</h3>
                    <div class="approval-rules">
        """
        for rule in approval_rules:
            action = rule.get("action", "Unknown")
            approvers = rule.get("approvers", [])
            condition = rule.get("condition", "")
            
            html_content += f"""
                        <div class="approval-rule">
                            <strong>Action:</strong> {action}<br>
                            <strong>Approvers:</strong> {', '.join(approvers)}<br>
                            {f'<strong>Condition:</strong> {condition}<br>' if condition else ''}
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
        """
    
    quick_actions_html = """
                <div class=\"section\">
                    <h3>⚡ Quick Actions</h3>
                    <div class=\"action-grid\">
                        <div class=\"action-category\">
                            <div class=\"category-title\">Assign Task</div>
                            <div class=\"action-item\">
                                <input id=\"task-title\" placeholder=\"Task title\" style=\"width: 100%; padding: 8px;\" />
                                <button style=\"margin-top:10px; padding:8px 12px;\" onclick=\"assignTask('__AGENT__')\">Create Task</button>
                            </div>
                        </div>
                        <div class=\"action-category\">
                            <div class=\"category-title\">Send Instruction</div>
                            <div class=\"action-item\">
                                <input id=\"instruction-text\" placeholder=\"Instruction\" style=\"width: 100%; padding: 8px;\" />
                                <button style=\"margin-top:10px; padding:8px 12px;\" onclick=\"sendInstruction('__AGENT__')\">Send</button>
                            </div>
                        </div>
                        <div class=\"action-category\">
                            <div class=\"category-title\">Logs</div>
                            <div class=\"action-item\">
                                <button style=\"padding:8px 12px;\" onclick=\"loadLogs('__AGENT__')\">View Logs</button>
                                <pre id=\"logs\" style=\"margin-top:10px; max-height:200px; overflow:auto; background:#f8f9fa; padding:10px;\"></pre>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
            // Live updates via SSE: stream logs and show heartbeats
            (function() {
                try {
                    var path = window.location.pathname;
                    var parts = path.split('/');
                    var agentId = parts[parts.length - 1] || parts[parts.length - 2];
                    if (agentId && agentId !== 'dashboard') {
                        var es = new EventSource('/api/agents/' + agentId + '/events');
                        es.addEventListener('log', function(e) {
                            try {
                                var data = JSON.parse(e.data);
                                var pre = document.getElementById('logs');
                                if (pre) {
                                    pre.textContent += '\n' + JSON.stringify(data);
                                }
                            } catch(_) {}
                        });
                        es.addEventListener('ping', function(_) {/* heartbeat */});
                    }
                } catch (_) {}
            })();
            async function assignTask(agentId) {
                var title = document.getElementById('task-title').value.trim();
                if (!title) { alert('Enter a task title'); return; }
                var url = '/api/agents/' + agentId + '/tasks';
                const r = await fetch(url, { method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{title: title}}) });
                const data = await r.json();
                alert('Task created: ' + (data.id || 'ok'));
            }
            async function sendInstruction(agentId) {
                var instruction = document.getElementById('instruction-text').value.trim();
                if (!instruction) { alert('Enter an instruction'); return; }
                var url = '/api/agents/' + agentId + '/instructions';
                const r = await fetch(url, { method: 'POST', headers: {{'Content-Type':'application/json'}}, body: JSON.stringify({{instruction: instruction}}) });
                const data = await r.json();
                alert('Instruction sent: ' + (data.id || 'ok'));
            }
            async function loadLogs(agentId) {
                var url = '/api/agents/' + agentId + '/logs';
                const r = await fetch(url);
                const data = await r.json();
                document.getElementById('logs').textContent = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """
    html_content += quick_actions_html.replace("__AGENT__", agent_id)
    
    return HTMLResponse(content=html_content)

@router.get("/status_legacy")
async def agents_status():
    """Get status of all agents"""
    agent_data = load_agent_data()
    
    # Build status map based on team listing to ensure department mapping for all agents
    agents_status: Dict[str, Any] = {}
    for dept, members in agent_data.get("team", {}).items():
        for a in members:
            aid = a.get("agent")
            cfg = agent_data.get("agents", {}).get(aid, {})
            agents_status[aid] = {
                "name": cfg.get("name", aid.replace("-", " ").title()),
                "department": dept,
                "risk_tier": cfg.get("risk_tier", "medium"),
                "actions_count": len(cfg.get("allowed_actions", [])),
                "approvals_count": len(cfg.get("approval_rules", [])),
            }

    return {
        "status": "operational",
        "total_agents": agent_data.get("total_agents", len(agents_status)),
        "departments": len(agent_data.get("team", {})),
        "agents": agents_status,
    }


def _tasks_collection(agent_id: str) -> str:
    return f"agent_tasks_{agent_id}"


def _logs_collection(agent_id: str) -> str:
    return f"agent_logs_{agent_id}"


def _instructions_collection(agent_id: str) -> str:
    return f"agent_instructions_{agent_id}"


def _find_agent(agent_id: str) -> dict:
    data = load_agent_data()
    for dept, agents in data.get("team", {}).items():
        for a in agents:
            if a.get("agent") == agent_id:
                a = {**a}
                a["department"] = dept
                a["config"] = data.get("agents", {}).get(agent_id, {})
                return a
    raise HTTPException(status_code=404, detail="Agent not found")


@router.get("/{agent_id}/status")
async def agent_status(agent_id: str) -> dict:
    agent = _find_agent(agent_id)
    tasks = JsonStore().list(_tasks_collection(agent_id))
    total = len(tasks)
    in_progress = len([t for t in tasks if t.get("status") == "in_progress"])
    failed = len([t for t in tasks if t.get("status") == "failed"])
    completed = len([t for t in tasks if t.get("status") == "completed"])
    last_ts = max([t.get("ts", 0) for t in tasks], default=0)
    state = "active" if in_progress else ("idle" if total else "idle")
    return {
        "agent": agent_id,
        "name": agent.get("name"),
        "department": agent.get("department"),
        "status": state,
        "tasks": {"total": total, "in_progress": in_progress, "completed": completed, "failed": failed},
        "last_activity": last_ts or None,
    }


@router.get("/{agent_id}/tasks")
async def list_tasks(agent_id: str) -> list[dict]:
    _find_agent(agent_id)
    return JsonStore().list(_tasks_collection(agent_id))


@router.post("/{agent_id}/tasks")
async def create_task(agent_id: str, body: dict) -> dict:
    agent = _find_agent(agent_id)
    task = {
        "agent": agent_id,
        "title": body.get("title") or body.get("description") or "Task",
        "description": body.get("description"),
        "priority": (body.get("priority") or "medium").lower(),
        "due": body.get("due"),
        "status": "queued",
        "created_by": body.get("created_by", "system"),
    }
    rec = JsonStore().append(_tasks_collection(agent_id), task)
    JsonStore().append(_logs_collection(agent_id), {"type": "task_created", "task_id": rec["id"], "title": task["title"]})
    return {"status": "accepted", "id": rec["id"], "task": rec}


@router.put("/{agent_id}/tasks/{task_id}")
async def update_task(agent_id: str, task_id: str, body: dict) -> dict:
    _find_agent(agent_id)
    # naive update: append a new record with same id as event
    update = {
        "task_id": task_id,
        "status": (body.get("status") or "in_progress").lower(),
        "percent": body.get("percent"),
        "message": body.get("message"),
    }
    JsonStore().append(_logs_collection(agent_id), {"type": "task_update", **update})
    return {"status": "ok", "id": task_id}


@router.post("/{agent_id}/instructions")
async def send_instructions(agent_id: str, body: dict) -> dict:
    _find_agent(agent_id)
    inst = {
        "instruction": body.get("instruction") or body.get("command"),
        "mode": body.get("mode") or "immediate",
        "priority": (body.get("priority") or "normal").lower(),
        "scheduled_at": body.get("scheduled_at"),
    }
    rec = JsonStore().append(_instructions_collection(agent_id), inst)
    JsonStore().append(_logs_collection(agent_id), {"type": "instruction", "instruction_id": rec["id"]})
    return {"status": "accepted", "id": rec["id"]}


@router.get("/{agent_id}/performance")
async def get_performance(agent_id: str) -> dict:
    _find_agent(agent_id)
    tasks = JsonStore().list(_tasks_collection(agent_id))
    total = len(tasks)
    completed = len([t for t in tasks if t.get("status") == "completed"])
    failed = len([t for t in tasks if t.get("status") == "failed"])
    completion_rate = (completed / total) if total else 0.0
    return {
        "agent": agent_id,
        "metrics": {
            "completion_rate": round(completion_rate, 3),
            "completed": completed,
            "failed": failed,
            "total": total,
        },
    }


@router.get("/{agent_id}/logs")
async def get_logs(agent_id: str) -> list[dict]:
    _find_agent(agent_id)
    return JsonStore().list(_logs_collection(agent_id))


@router.post("/{agent_id}/execute")
async def execute_action(agent_id: str, body: dict) -> dict:
    agent = _find_agent(agent_id)
    action = body.get("action") or ""
    params = body.get("params") or {}
    allowed = set(agent.get("config", {}).get("allowed_actions", []))
    if allowed and action not in allowed:
        raise HTTPException(status_code=403, detail=f"Action not allowed: {action}")

    # Safety gate: by default do not mutate; simulate execution unless explicitly enabled
    allow_mut = (os.getenv("ALLOW_M365_MUTATIONS", "false").lower() in ("1", "true", "yes"))
    adapter_url = os.getenv("OPS_ADAPTER_URL") or os.getenv("ADAPTER_URL")

    if allow_mut and adapter_url:
        try:
            from smarthaus_graph.client import GraphClient

            gc = GraphClient()
            result = gc.invoke_adapter_action(adapter_url, agent_id, action, params)
            JsonStore().append(_logs_collection(agent_id), {"type": "execute", "action": action, "mode": "adapter"})
            return {"status": "ok", "result": result}
        except Exception as e:
            # Fall back to queued if adapter fails
            JsonStore().append(_logs_collection(agent_id), {"type": "execute_error", "action": action, "error": str(e)})
            return {"status": "queued", "message": "Adapter error; queued for review"}
    else:
        JsonStore().append(_logs_collection(agent_id), {"type": "execute", "action": action, "mode": "dry_run"})
        return {"status": "queued", "message": "Dry-run mode; execution queued"}


@router.get("/{agent_id}/events")
async def agent_events(agent_id: str):
    """Server-Sent Events stream of agent log updates (simple polling)."""
    _find_agent(agent_id)

    async def eventgen():  # type: ignore[no-redef]
        last_len = 0
        while True:
            logs = JsonStore().list(_logs_collection(agent_id))
            if len(logs) > last_len:
                for row in logs[last_len:]:
                    data = json.dumps(row)
                    yield f"event: log\ndata: {data}\n\n"
                last_len = len(logs)
            # heartbeat every 2s
            yield "event: ping\ndata: {}\n\n"
            import asyncio
            await asyncio.sleep(2)

    return StreamingResponse(eventgen(), media_type="text/event-stream")
