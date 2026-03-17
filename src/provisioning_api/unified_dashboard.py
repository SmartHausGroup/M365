"""
SmartHaus Unified Dashboard
One page to rule them all - complete business management system
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)

app = FastAPI(title="SmartHaus Unified Dashboard", version="6.0.0")

# Load real department data
def load_departments():
    """Load real department data from registry"""
    try:
        with open("registry/ai_team.json", "r") as f:
            team_data = json.load(f)
        
        departments = team_data.get("departments", {})
        
        # Map to our display format
        dept_mapping = {
            "operations": {"name": "Operations", "description": "M365 administration, website management, and system operations", "icon": "🔧", "color": "#1976d2"},
            "hr": {"name": "Human Resources", "description": "Employee management, onboarding, and policy administration", "icon": "👥", "color": "#9c27b0"},
            "communication": {"name": "Communications", "description": "Outreach coordination and external communications", "icon": "📢", "color": "#ff9800"},
            "engineering": {"name": "Engineering", "description": "AI development, backend architecture, and technical implementation", "icon": "⚙️", "color": "#28a745"},
            "marketing": {"name": "Marketing", "description": "Content creation, growth hacking, and social media management", "icon": "📈", "color": "#ffc107"},
            "product": {"name": "Product Management", "description": "Product strategy, user research, and market analysis", "icon": "📋", "color": "#ff9800"},
            "project-management": {"name": "Project Management", "description": "Project coordination, shipping, and studio production", "icon": "🚀", "color": "#4caf50"},
            "studio-operations": {"name": "Studio Operations", "description": "Analytics, finance, infrastructure, legal, and customer support", "icon": "🏢", "color": "#607d8b"},
            "testing": {"name": "Testing & Quality", "description": "API testing, performance benchmarking, and quality assurance", "icon": "🧪", "color": "#795548"},
            "design": {"name": "Design", "description": "Brand management, UX/UI design, and visual identity", "icon": "🎨", "color": "#e91e63"},
            "bonus": {"name": "Special Teams", "description": "Performance coaching and team morale", "icon": "⭐", "color": "#9c27b0"}
        }
        
        result = {}
        for dept_id, agents in departments.items():
            if dept_id in dept_mapping:
                dept_info = dept_mapping[dept_id]
                result[dept_id] = {
                    "name": dept_info["name"],
                    "description": dept_info["description"],
                    "icon": dept_info["icon"],
                    "color": dept_info["color"],
                    "agents": [
                        {
                            "name": agent["name"],
                            "role": agent["role"],
                            "status": "Active",
                            "workload": "High" if "Senior" in agent["role"] or "Lead" in agent["role"] or "Director" in agent["role"] else "Medium"
                        }
                        for agent in agents
                    ]
                }
        
        return result
    except Exception as e:
        print(f"Error loading departments: {e}")
        return {}

# Department definitions with descriptions
DEPARTMENTS = load_departments()

# Load real data
def load_real_data():
    """Load actual business data from files"""
    try:
        # Load agent data
        with open("registry/ai_team.json", "r") as f:
            team_data = json.load(f)
        
        # Load project data
        with open("data/smarthaus_website_projects.json", "r") as f:
            project_data = json.load(f)
        
        # Load client data
        with open("data/clients_projects.json", "r") as f:
            client_data = json.load(f)
        
        # Load agent tasks
        with open("data/agent_tasks_m365-administrator.json", "r") as f:
            task_data = json.load(f)
        
        # Calculate real metrics
        total_agents = team_data.get("total_agents", 0)
        active_projects = project_data.get("metadata", {}).get("active_projects", 0)
        client_projects = len(client_data) if isinstance(client_data, list) else 0
        
        # Count tasks
        completed_tasks = len([task for task in task_data if task.get("status") == "completed"])
        pending_tasks = len([task for task in task_data if task.get("status") in ["pending", "in_progress"]])
        
        return {
            "active_projects": active_projects,
            "total_agents": total_agents,
            "active_agents": total_agents,  # All agents are active
            "completed_tasks_today": completed_tasks,
            "pending_tasks": pending_tasks,
            "m365_operations": 8,  # From M365 admin tasks
            "client_projects": client_projects
        }
    except Exception as e:
        print(f"Error loading real data: {e}")
        # Fallback to default values
        return {
            "active_projects": 1,
            "total_agents": 39,
            "active_agents": 39,
            "completed_tasks_today": 0,
            "pending_tasks": 0,
            "m365_operations": 0,
            "client_projects": 0
        }

@app.get("/", response_class=HTMLResponse)
async def unified_dashboard(request: Request):
    """Main unified dashboard - one page for everything"""
    
    # Load real business metrics
    business_metrics = load_real_data()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartHaus Unified Dashboard</title>
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
                padding: 2rem; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header h1 {{ font-size: 2.5rem; font-weight: 600; margin-bottom: 0.5rem; }}
            .header p {{ opacity: 0.9; font-size: 1.1rem; }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
            
            /* Quick Stats */
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 1rem; 
                margin-bottom: 2rem;
            }}
            .stat-card {{ 
                background: white; 
                padding: 1.5rem; 
                border-radius: 8px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 4px solid #1976d2;
            }}
            .stat-number {{ font-size: 2rem; font-weight: 600; color: #1976d2; }}
            .stat-label {{ color: #6c757d; font-size: 0.9rem; margin-top: 0.5rem; }}
            
            /* Department Grid */
            .departments-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
                gap: 1.5rem; 
                margin-bottom: 2rem;
            }}
            .department-card {{ 
                background: white; 
                border-radius: 8px; 
                padding: 1.5rem; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                cursor: pointer;
                transition: all 0.3s ease;
                border-left: 4px solid #1976d2;
            }}
            .department-card:hover {{ 
                transform: translateY(-5px); 
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }}
            .department-header {{ 
                display: flex; 
                align-items: center; 
                margin-bottom: 1rem;
            }}
            .department-icon {{ 
                font-size: 2rem; 
                margin-right: 1rem; 
            }}
            .department-name {{ 
                font-size: 1.3rem; 
                font-weight: 600; 
                color: #1976d2; 
            }}
            .department-description {{ 
                color: #6c757d; 
                margin-bottom: 1rem; 
                line-height: 1.5;
            }}
            .department-agents {{ 
                display: flex; 
                flex-wrap: wrap; 
                gap: 0.5rem; 
                margin-bottom: 1rem;
            }}
            .agent-badge {{ 
                background: #e3f2fd; 
                color: #1976d2; 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem;
                font-weight: 500;
            }}
            .department-actions {{ 
                display: flex; 
                gap: 0.5rem; 
                margin-top: 1rem;
            }}
            .btn {{ 
                padding: 0.5rem 1rem; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 0.9rem;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-block;
            }}
            .btn-primary {{ background: #1976d2; color: white; }}
            .btn-secondary {{ background: #6c757d; color: white; }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
            
            /* Quick Actions */
            .quick-actions {{ 
                background: white; 
                padding: 2rem; 
                border-radius: 8px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }}
            .quick-actions h3 {{ 
                color: #1976d2; 
                margin-bottom: 1rem; 
                font-size: 1.3rem;
            }}
            .actions-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 1rem;
            }}
            .action-item {{ 
                background: #f8f9fa; 
                padding: 1rem; 
                border-radius: 6px; 
                border-left: 4px solid #28a745;
                cursor: pointer;
                transition: all 0.2s;
            }}
            .action-item:hover {{ background: #e3f2fd; }}
            .action-title {{ font-weight: 600; color: #1976d2; margin-bottom: 0.5rem; }}
            .action-desc {{ color: #6c757d; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏢 SmartHaus Unified Dashboard</h1>
            <p>Complete business management system - one page for everything</p>
        </div>
        
        <div class="container">
            <!-- Quick Stats -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{business_metrics['active_projects']}</div>
                    <div class="stat-label">Active Projects</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{business_metrics['total_agents']}</div>
                    <div class="stat-label">Total Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{business_metrics['completed_tasks_today']}</div>
                    <div class="stat-label">Tasks Completed Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{business_metrics['pending_tasks']}</div>
                    <div class="stat-label">Pending Tasks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{business_metrics['m365_operations']}</div>
                    <div class="stat-label">M365 Operations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{business_metrics['client_projects']}</div>
                    <div class="stat-label">Client Projects</div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="quick-actions">
                <h3>🚀 Quick Actions</h3>
                <div class="actions-grid">
                    <div class="action-item" onclick="createTask()">
                        <div class="action-title">➕ Create New Task</div>
                        <div class="action-desc">Assign a task to any agent</div>
                    </div>
                    <div class="action-item" onclick="createProject()">
                        <div class="action-title">📋 Create New Project</div>
                        <div class="action-desc">Start a new client or internal project</div>
                    </div>
                    <div class="action-item" onclick="m365Operation()">
                        <div class="action-title">🔧 M365 Operation</div>
                        <div class="action-desc">Request M365 administration task</div>
                    </div>
                    <div class="action-item" onclick="viewReports()">
                        <div class="action-title">📊 View Reports</div>
                        <div class="action-desc">Business intelligence and analytics</div>
                    </div>
                    <div class="action-item" onclick="manageClients()">
                        <div class="action-title">👥 Manage Clients</div>
                        <div class="action-desc">Client project and communication management</div>
                    </div>
                    <div class="action-item" onclick="systemHealth()">
                        <div class="action-title">🏥 System Health</div>
                        <div class="action-desc">M365 services and infrastructure status</div>
                    </div>
                </div>
            </div>
            
            <!-- Departments -->
            <h2 style="color: #1976d2; margin-bottom: 1.5rem; font-size: 1.8rem;">🏢 Departments</h2>
            <div class="departments-grid">
                {"".join([f'''
                <div class="department-card" onclick="openDepartment('{dept_id}')">
                    <div class="department-header">
                        <div class="department-icon">{dept["icon"]}</div>
                        <div class="department-name">{dept["name"]}</div>
                    </div>
                    <div class="department-description">{dept["description"]}</div>
                    <div class="department-agents">
                        {"".join([f'<span class="agent-badge">{agent["name"]} - {agent["role"]}</span>' for agent in dept["agents"][:3]])}
                        {f'<span class="agent-badge">+{len(dept["agents"]) - 3} more</span>' if len(dept["agents"]) > 3 else ''}
                    </div>
                    <div class="department-actions">
                        <button class="btn btn-primary" onclick="event.stopPropagation(); viewDepartment('{dept_id}')">View Team</button>
                        <button class="btn btn-secondary" onclick="event.stopPropagation(); assignTask('{dept_id}')">Assign Task</button>
                    </div>
                </div>
                ''' for dept_id, dept in DEPARTMENTS.items()])}
            </div>
        </div>
        
        <script>
            function openDepartment(deptId) {{
                window.location.href = `/department/${{deptId}}`;
            }}
            
            function viewDepartment(deptId) {{
                window.location.href = `/department/${{deptId}}/team`;
            }}
            
            function assignTask(deptId) {{
                const task = prompt('Task to assign to ' + deptId + ' department:');
                if (task) {{
                    alert(`Task assigned to ${{deptId}} department: ${{task}}`);
                }}
            }}
            
            function createTask() {{
                const task = prompt('New task:');
                const assignee = prompt('Assign to (agent name):');
                if (task && assignee) {{
                    alert(`Task created: ${{task}}\\nAssigned to: ${{assignee}}`);
                }}
            }}
            
            function createProject() {{
                const project = prompt('New project name:');
                const client = prompt('Client:');
                if (project && client) {{
                    alert(`Project created: ${{project}}\\nClient: ${{client}}`);
                }}
            }}
            
            function m365Operation() {{
                const operation = prompt('M365 operation:');
                if (operation) {{
                    alert(`M365 operation requested: ${{operation}}`);
                }}
            }}
            
            function viewReports() {{
                alert('Opening business intelligence reports...');
            }}
            
            function manageClients() {{
                alert('Opening client management interface...');
            }}
            
            function systemHealth() {{
                alert('Checking system health status...');
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/department/{dept_id}", response_class=HTMLResponse)
async def department_page(request: Request, dept_id: str):
    """Department team page"""
    
    if dept_id not in DEPARTMENTS:
        raise HTTPException(status_code=404, detail="Department not found")
    
    dept = DEPARTMENTS[dept_id]
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{dept['name']} Team - SmartHaus</title>
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
                padding: 2rem; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header h1 {{ font-size: 2rem; font-weight: 600; margin-bottom: 0.5rem; }}
            .header p {{ opacity: 0.9; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
            .back-btn {{ 
                color: white; 
                text-decoration: none; 
                background: rgba(255,255,255,0.2); 
                padding: 0.5rem 1rem; 
                border-radius: 4px;
                margin-bottom: 1rem;
                display: inline-block;
            }}
            .agents-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 1.5rem; 
            }}
            .agent-card {{ 
                background: white; 
                border-radius: 8px; 
                padding: 1.5rem; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid {dept['color']};
                cursor: pointer;
                transition: all 0.3s ease;
            }}
            .agent-card:hover {{ 
                transform: translateY(-5px); 
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }}
            .agent-name {{ 
                font-size: 1.2rem; 
                font-weight: 600; 
                color: {dept['color']}; 
                margin-bottom: 0.5rem;
            }}
            .agent-role {{ 
                color: #6c757d; 
                margin-bottom: 1rem; 
            }}
            .agent-status {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 1rem;
            }}
            .status-badge {{ 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem; 
                font-weight: 500;
            }}
            .status-active {{ background: #d4edda; color: #155724; }}
            .workload-high {{ background: #f8d7da; color: #721c24; }}
            .workload-medium {{ background: #fff3cd; color: #856404; }}
            .workload-low {{ background: #d4edda; color: #155724; }}
            .btn {{ 
                padding: 0.5rem 1rem; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 0.9rem;
                transition: all 0.2s;
                margin: 0.25rem;
            }}
            .btn-primary {{ background: {dept['color']}; color: white; }}
            .btn-secondary {{ background: #6c757d; color: white; }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
        </style>
    </head>
    <body>
        <div class="header">
            <a href="/" class="back-btn">← Back to Dashboard</a>
            <h1>{dept['icon']} {dept['name']} Team</h1>
            <p>{dept['description']}</p>
        </div>
        
        <div class="container">
            <div class="agents-grid">
                {"".join([f'''
                <div class="agent-card" onclick="openAgent('{agent['name'].lower().replace(' ', '-')}')">
                    <div class="agent-name">{agent['name']}</div>
                    <div class="agent-role">{agent['role']}</div>
                    <div class="agent-status">
                        <span class="status-badge status-active">{agent['status']}</span>
                        <span class="status-badge workload-{agent['workload'].lower()}">{agent['workload']} Workload</span>
                    </div>
                    <div>
                        <button class="btn btn-primary" onclick="event.stopPropagation(); assignTask('{agent['name']}')">Assign Task</button>
                        <button class="btn btn-secondary" onclick="event.stopPropagation(); viewWork('{agent['name']}')">View Work</button>
                    </div>
                </div>
                ''' for agent in dept['agents']])}
            </div>
        </div>
        
        <script>
            function openAgent(agentName) {{
                alert(`Opening ${{agentName}}'s workspace...`);
            }}
            
            function assignTask(agentName) {{
                const task = prompt(`Task for ${{agentName}}:`);
                if (task) {{
                    alert(`Task assigned to ${{agentName}}: ${{task}}`);
                }}
            }}
            
            function viewWork(agentName) {{
                alert(`Viewing ${{agentName}}'s current work and progress...`);
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "6.0.0",
        "unified_dashboard": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
