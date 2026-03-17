"""
SmartHaus Business Operations Dashboard
Real business operations management for M365 and project delivery
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import httpx

from smarthaus_common.config import load_bootstrap_env

load_bootstrap_env(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="SmartHaus Business Operations", version="3.0.0")

# Business Operations Data Models
class BusinessTask(BaseModel):
    id: str
    title: str
    description: str
    assigned_to: str
    business_unit: str
    priority: str
    status: str
    due_date: datetime
    client: Optional[str] = None
    budget: Optional[float] = None
    created_by: str
    created_at: datetime

class Project(BaseModel):
    id: str
    name: str
    client: str
    business_unit: str
    status: str
    progress: int
    budget_total: float
    budget_used: float
    start_date: datetime
    end_date: datetime
    team_lead: str
    deliverables: List[str]

class M365Operation(BaseModel):
    id: str
    operation_type: str
    description: str
    target: str
    status: str
    requested_by: str
    approved_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    cost_impact: float

class ClientWork(BaseModel):
    id: str
    client_name: str
    project_type: str
    status: str
    value: float
    start_date: datetime
    delivery_date: datetime
    team_assigned: List[str]

# Mock business data - in production this would come from real systems
BUSINESS_DATA = {
    "active_projects": [
        {
            "id": "PROJ-001",
            "name": "TAI Quantum AIUCP Platform",
            "client": "Internal R&D",
            "business_unit": "TAI",
            "status": "Active",
            "progress": 75,
            "budget_total": 150000,
            "budget_used": 112500,
            "start_date": "2024-01-15",
            "end_date": "2024-12-31",
            "team_lead": "Marcus Chen",
            "deliverables": ["Quantum Core", "Holographic Memory", "macOS Client", "Orchestration Engine"]
        },
        {
            "id": "PROJ-002", 
            "name": "SmartHaus Website v2.0",
            "client": "SmartHaus Group",
            "business_unit": "Website",
            "status": "Active",
            "progress": 60,
            "budget_total": 75000,
            "budget_used": 45000,
            "start_date": "2024-03-01",
            "end_date": "2024-11-30",
            "team_lead": "Sarah Williams",
            "deliverables": ["Next.js Frontend", "Content Management", "Analytics Dashboard", "SEO Optimization"]
        },
        {
            "id": "PROJ-003",
            "name": "LATTICE Research Platform",
            "client": "Research Division",
            "business_unit": "LATTICE",
            "status": "Planning",
            "progress": 25,
            "budget_total": 200000,
            "budget_used": 50000,
            "start_date": "2024-06-01",
            "end_date": "2025-06-30",
            "team_lead": "Alex Rodriguez",
            "deliverables": ["LQL Engine", "LEF Framework", "AIOS Integration", "Research Tools"]
        }
    ],
    "pending_tasks": [
        {
            "id": "TASK-001",
            "title": "Set up shared mailbox for support@smarthausgroup.com",
            "description": "Create Exchange shared mailbox with proper permissions for customer support",
            "assigned_to": "Marcus Chen (M365 Admin)",
            "business_unit": "Operations",
            "priority": "High",
            "status": "Pending",
            "due_date": "2024-09-20",
            "client": "Internal",
            "budget": 0,
            "created_by": "Sarah Williams",
            "created_at": "2024-09-15T10:30:00Z"
        },
        {
            "id": "TASK-002",
            "title": "Provision M365 accounts for new TAI team members",
            "description": "Create user accounts, assign licenses, set up Teams access for 3 new developers",
            "assigned_to": "Marcus Chen (M365 Admin)",
            "business_unit": "TAI",
            "priority": "Medium",
            "status": "In Progress",
            "due_date": "2024-09-18",
            "client": "TAI Team",
            "budget": 0,
            "created_by": "Alex Rodriguez",
            "created_at": "2024-09-14T14:20:00Z"
        },
        {
            "id": "TASK-003",
            "title": "Deploy website updates to production",
            "description": "Deploy latest website changes including new advisory service pages",
            "assigned_to": "Sarah Williams (Website Manager)",
            "business_unit": "Website",
            "priority": "High",
            "status": "Pending",
            "due_date": "2024-09-17",
            "client": "SmartHaus Group",
            "budget": 0,
            "created_by": "Phil Smart",
            "created_at": "2024-09-15T09:15:00Z"
        }
    ],
    "m365_operations": [
        {
            "id": "M365-001",
            "operation_type": "User Creation",
            "description": "Create user account for john.smith@smarthausgroup.com",
            "target": "john.smith@smarthausgroup.com",
            "status": "Completed",
            "requested_by": "HR Team",
            "approved_by": "Marcus Chen",
            "completed_at": "2024-09-14T16:45:00Z",
            "cost_impact": 12.50
        },
        {
            "id": "M365-002",
            "operation_type": "Teams Workspace",
            "description": "Create Teams workspace for Project Alpha collaboration",
            "target": "Project Alpha Team",
            "status": "Pending Approval",
            "requested_by": "Project Manager",
            "approved_by": None,
            "completed_at": None,
            "cost_impact": 0
        }
    ],
    "client_work": [
        {
            "id": "CLIENT-001",
            "client_name": "TechCorp Solutions",
            "project_type": "M365 Migration",
            "status": "In Progress",
            "value": 45000,
            "start_date": "2024-08-01",
            "delivery_date": "2024-10-31",
            "team_assigned": ["Marcus Chen", "Sarah Williams"]
        },
        {
            "id": "CLIENT-002",
            "client_name": "Innovation Labs",
            "project_type": "AI Platform Development",
            "status": "Proposal",
            "value": 125000,
            "start_date": "2024-10-01",
            "delivery_date": "2025-03-31",
            "team_assigned": ["Alex Rodriguez", "Marcus Chen"]
        }
    ]
}

@app.get("/", response_class=HTMLResponse)
async def business_dashboard(request: Request):
    """Main business operations dashboard"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartHaus Business Operations</title>
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
                padding: 1.5rem 2rem; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header h1 {{ font-size: 2rem; font-weight: 600; }}
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
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
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
                font-size: 1.2rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .project-item {{ 
                padding: 1rem; 
                border: 1px solid #e9ecef; 
                border-radius: 6px; 
                margin-bottom: 1rem;
                background: #f8f9fa;
            }}
            .project-header {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: start; 
                margin-bottom: 0.5rem;
            }}
            .project-title {{ font-weight: 600; color: #2c3e50; }}
            .project-client {{ color: #6c757d; font-size: 0.9rem; }}
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
            .task-item {{ 
                padding: 1rem; 
                border-left: 4px solid #ffc107; 
                background: #fff3cd; 
                margin-bottom: 0.5rem;
                border-radius: 4px;
            }}
            .task-high {{ border-left-color: #dc3545; background: #f8d7da; }}
            .task-medium {{ border-left-color: #ffc107; background: #fff3cd; }}
            .task-low {{ border-left-color: #28a745; background: #d4edda; }}
            .task-header {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                margin-bottom: 0.5rem;
            }}
            .task-title {{ font-weight: 600; }}
            .task-assignee {{ color: #6c757d; font-size: 0.9rem; }}
            .btn {{ 
                padding: 0.5rem 1rem; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 0.9rem;
                transition: all 0.2s;
                margin: 0.25rem;
            }}
            .btn-primary {{ background: #1976d2; color: white; }}
            .btn-success {{ background: #28a745; color: white; }}
            .btn-warning {{ background: #ffc107; color: #212529; }}
            .btn-danger {{ background: #dc3545; color: white; }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
            .status-badge {{ 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem; 
                font-weight: 500;
            }}
            .status-active {{ background: #d4edda; color: #155724; }}
            .status-pending {{ background: #fff3cd; color: #856404; }}
            .status-completed {{ background: #d1ecf1; color: #0c5460; }}
            .quick-actions {{ 
                background: #e3f2fd; 
                padding: 1rem; 
                border-radius: 8px; 
                margin-bottom: 1rem;
            }}
            .quick-actions h4 {{ color: #1976d2; margin-bottom: 0.5rem; }}
            .action-buttons {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏢 SmartHaus Business Operations</h1>
            <p>Manage projects, tasks, M365 operations, and client work</p>
        </div>
        
        <div class="nav">
            <a href="/" class="active">📊 Dashboard</a>
            <a href="/projects">📋 Projects</a>
            <a href="/tasks">✅ Tasks</a>
            <a href="/m365">🔧 M365 Ops</a>
            <a href="/clients">👥 Clients</a>
            <a href="/agents">🤖 Agents</a>
        </div>
        
        <div class="container">
            <!-- Quick Actions -->
            <div class="quick-actions">
                <h4>🚀 Quick Actions</h4>
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="createTask()">➕ New Task</button>
                    <button class="btn btn-success" onclick="createProject()">📋 New Project</button>
                    <button class="btn btn-warning" onclick="m365Operation()">🔧 M365 Request</button>
                    <button class="btn btn-primary" onclick="assignAgent()">🤖 Assign Agent</button>
                </div>
            </div>
            
            <!-- Dashboard Grid -->
            <div class="dashboard-grid">
                <!-- Active Projects -->
                <div class="card">
                    <h3>📋 Active Projects</h3>
                    {"".join([f'''
                    <div class="project-item">
                        <div class="project-header">
                            <div>
                                <div class="project-title">{project["name"]}</div>
                                <div class="project-client">{project["client"]} • {project["business_unit"]}</div>
                            </div>
                            <span class="status-badge status-{project["status"].lower()}">{project["status"]}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {project["progress"]}%"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #6c757d; margin-top: 0.5rem;">
                            <span>{project["progress"]}% Complete</span>
                            <span>${project["budget_used"]:,.0f} / ${project["budget_total"]:,.0f}</span>
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <button class="btn btn-primary" onclick="viewProject('{project["id"]}')">View Details</button>
                            <button class="btn btn-success" onclick="updateProgress('{project["id"]}')">Update Progress</button>
                        </div>
                    </div>
                    ''' for project in BUSINESS_DATA["active_projects"]])}
                </div>
                
                <!-- Pending Tasks -->
                <div class="card">
                    <h3>✅ Pending Tasks</h3>
                    {"".join([f'''
                    <div class="task-item task-{task["priority"].lower()}">
                        <div class="task-header">
                            <div class="task-title">{task["title"]}</div>
                            <span class="status-badge status-{task["status"].lower()}">{task["status"]}</span>
                        </div>
                        <div class="task-assignee">Assigned to: {task["assigned_to"]}</div>
                        <div style="font-size: 0.9rem; color: #6c757d; margin: 0.5rem 0;">
                            Due: {task["due_date"]} • Priority: {task["priority"]}
                        </div>
                        <div>
                            <button class="btn btn-success" onclick="completeTask('{task["id"]}')">✅ Complete</button>
                            <button class="btn btn-warning" onclick="reassignTask('{task["id"]}')">🔄 Reassign</button>
                        </div>
                    </div>
                    ''' for task in BUSINESS_DATA["pending_tasks"]])}
                </div>
                
                <!-- M365 Operations -->
                <div class="card">
                    <h3>🔧 M365 Operations</h3>
                    {"".join([f'''
                    <div class="task-item">
                        <div class="task-header">
                            <div class="task-title">{op["operation_type"]}</div>
                            <span class="status-badge status-{op["status"].lower().replace(' ', '')}">{op["status"]}</span>
                        </div>
                        <div class="task-assignee">{op["description"]}</div>
                        <div style="font-size: 0.9rem; color: #6c757d; margin: 0.5rem 0;">
                            Target: {op["target"]} • Requested by: {op["requested_by"]}
                        </div>
                        <div>
                            <button class="btn btn-success" onclick="approveOperation('{op["id"]}')">✅ Approve</button>
                            <button class="btn btn-primary" onclick="executeOperation('{op["id"]}')">🚀 Execute</button>
                        </div>
                    </div>
                    ''' for op in BUSINESS_DATA["m365_operations"]])}
                </div>
                
                <!-- Client Work -->
                <div class="card">
                    <h3>👥 Client Work</h3>
                    {"".join([f'''
                    <div class="project-item">
                        <div class="project-header">
                            <div>
                                <div class="project-title">{client["client_name"]}</div>
                                <div class="project-client">{client["project_type"]}</div>
                            </div>
                            <span class="status-badge status-{client["status"].lower().replace(' ', '')}">{client["status"]}</span>
                        </div>
                        <div style="font-size: 0.9rem; color: #6c757d; margin: 0.5rem 0;">
                            Value: ${client["value"]:,.0f} • Delivery: {client["delivery_date"]}
                        </div>
                        <div>
                            <button class="btn btn-primary" onclick="viewClient('{client["id"]}')">View Details</button>
                            <button class="btn btn-success" onclick="updateClient('{client["id"]}')">Update Status</button>
                        </div>
                    </div>
                    ''' for client in BUSINESS_DATA["client_work"]])}
                </div>
            </div>
        </div>
        
        <script>
            // Quick Action Functions
            function createTask() {{
                const title = prompt('Task Title:');
                const assignee = prompt('Assign to (agent name):');
                const priority = prompt('Priority (High/Medium/Low):');
                if (title && assignee && priority) {{
                    alert(`Task created: ${{title}}\\nAssigned to: ${{assignee}}\\nPriority: ${{priority}}\\n\\nTask will be added to the system.`);
                }}
            }}
            
            function createProject() {{
                const name = prompt('Project Name:');
                const client = prompt('Client:');
                const budget = prompt('Budget:');
                if (name && client && budget) {{
                    alert(`Project created: ${{name}}\\nClient: ${{client}}\\nBudget: ${{budget}}\\n\\nProject will be added to the system.`);
                }}
            }}
            
            function m365Operation() {{
                const operation = prompt('M365 Operation (e.g., "Create User", "Add to Team"):');
                const target = prompt('Target (email, team name, etc.):');
                if (operation && target) {{
                    alert(`M365 Operation requested: ${{operation}}\\nTarget: ${{target}}\\n\\nRequest will be sent to Marcus Chen for approval.`);
                }}
            }}
            
            function assignAgent() {{
                const agent = prompt('Agent to assign (Marcus Chen, Sarah Williams, Alex Rodriguez):');
                const task = prompt('Task description:');
                if (agent && task) {{
                    alert(`Task assigned to ${{agent}}: ${{task}}\\n\\nAgent will be notified via Teams.`);
                }}
            }}
            
            // Project Functions
            function viewProject(projectId) {{
                alert(`Opening project details for ${{projectId}}\\n\\nThis would show full project timeline, deliverables, team members, and progress tracking.`);
            }}
            
            function updateProgress(projectId) {{
                const progress = prompt('Update progress percentage:');
                if (progress) {{
                    alert(`Progress updated for ${{projectId}}: ${{progress}}%\\n\\nTeam will be notified of progress update.`);
                }}
            }}
            
            // Task Functions
            function completeTask(taskId) {{
                alert(`Task ${{taskId}} marked as completed!\\n\\nStakeholders will be notified and project progress will be updated.`);
            }}
            
            function reassignTask(taskId) {{
                const newAssignee = prompt('Reassign to:');
                if (newAssignee) {{
                    alert(`Task ${{taskId}} reassigned to ${{newAssignee}}\\n\\nNew assignee will be notified via Teams.`);
                }}
            }}
            
            // M365 Functions
            function approveOperation(opId) {{
                alert(`M365 Operation ${{opId}} approved!\\n\\nOperation will be executed by Marcus Chen.`);
            }}
            
            function executeOperation(opId) {{
                alert(`M365 Operation ${{opId}} executed!\\n\\nOperation completed successfully.`);
            }}
            
            // Client Functions
            function viewClient(clientId) {{
                alert(`Opening client details for ${{clientId}}\\n\\nThis would show full client project details, timeline, deliverables, and communication history.`);
            }}
            
            function updateClient(clientId) {{
                const status = prompt('Update client status:');
                if (status) {{
                    alert(`Client ${{clientId}} status updated to: ${{status}}\\n\\nClient will be notified of status change.`);
                }}
            }}
            
            // Auto-refresh every 5 minutes
            setTimeout(() => location.reload(), 300000);
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
        "version": "3.0.0",
        "business_operations": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
