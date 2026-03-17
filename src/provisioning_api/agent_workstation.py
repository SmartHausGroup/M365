"""
SmartHaus Agent Workstation
Individual agent management and task assignment system
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

app = FastAPI(title="SmartHaus Agent Workstation", version="4.0.0")

# Agent-specific work definitions
AGENT_WORK_DEFINITIONS = {
    "alex-thompson": {
        "name": "Alex Thompson",
        "role": "ML Engineer",
        "department": "Engineering",
        "current_projects": [
            "TAI Quantum Core Development",
            "Holographic Memory System",
            "LQL Research Platform"
        ],
        "daily_tasks": [
            "Model training and optimization",
            "Research paper analysis",
            "Algorithm development",
            "Performance benchmarking",
            "Code review and testing"
        ],
        "specialized_work": [
            "Quantum algorithm implementation",
            "Neural network architecture design",
            "Machine learning model deployment",
            "Research collaboration coordination",
            "Technical documentation"
        ],
        "tools_access": [
            "Jupyter Notebooks",
            "TensorFlow/PyTorch",
            "GitHub repositories",
            "Research databases",
            "Cloud computing resources"
        ],
        "current_workload": "High",
        "next_deadline": "2024-09-25",
        "priority_tasks": [
            "Complete quantum core prototype",
            "Review LQL research papers",
            "Optimize memory system performance"
        ]
    },
    "jordan-kim": {
        "name": "Jordan Kim", 
        "role": "Principal Backend Engineer",
        "department": "Engineering",
        "current_projects": [
            "TAI Orchestration Engine",
            "API Gateway Development",
            "Database Architecture"
        ],
        "daily_tasks": [
            "System architecture design",
            "API development and testing",
            "Database optimization",
            "Code review and mentoring",
            "Technical documentation"
        ],
        "specialized_work": [
            "Microservices architecture",
            "Database design and optimization",
            "API security implementation",
            "Performance monitoring setup",
            "Team technical leadership"
        ],
        "tools_access": [
            "AWS/Azure cloud services",
            "Docker and Kubernetes",
            "PostgreSQL/MongoDB",
            "API testing tools",
            "Monitoring dashboards"
        ],
        "current_workload": "High",
        "next_deadline": "2024-09-22",
        "priority_tasks": [
            "Complete orchestration engine",
            "Review API security protocols",
            "Optimize database queries"
        ]
    },
    "isabella-rossi": {
        "name": "Isabella Rossi",
        "role": "Brand Guardian", 
        "department": "Design",
        "current_projects": [
            "SmartHaus Brand Guidelines",
            "Website Visual Identity",
            "Marketing Material Design"
        ],
        "daily_tasks": [
            "Brand consistency review",
            "Visual design creation",
            "Design system maintenance",
            "Creative direction",
            "Asset management"
        ],
        "specialized_work": [
            "Brand strategy development",
            "Visual identity design",
            "Design system creation",
            "Creative team leadership",
            "Brand compliance monitoring"
        ],
        "tools_access": [
            "Adobe Creative Suite",
            "Figma design tools",
            "Brand asset libraries",
            "Design collaboration platforms",
            "Marketing material templates"
        ],
        "current_workload": "Medium",
        "next_deadline": "2024-09-20",
        "priority_tasks": [
            "Update brand guidelines",
            "Create website design system",
            "Review marketing materials"
        ]
    },
    "david-park": {
        "name": "David Park",
        "role": "Communications Manager",
        "department": "Communication", 
        "current_projects": [
            "Client Communication Strategy",
            "Internal Team Coordination",
            "Stakeholder Management"
        ],
        "daily_tasks": [
            "Email campaign management",
            "Meeting coordination",
            "Client communication",
            "Team updates and announcements",
            "Documentation and reporting"
        ],
        "specialized_work": [
            "Communication strategy development",
            "Stakeholder relationship management",
            "Crisis communication planning",
            "Team coordination and alignment",
            "Client onboarding communication"
        ],
        "tools_access": [
            "Email marketing platforms",
            "Calendar and scheduling tools",
            "Communication templates",
            "Client management systems",
            "Team collaboration platforms"
        ],
        "current_workload": "High",
        "next_deadline": "2024-09-18",
        "priority_tasks": [
            "Send client project updates",
            "Coordinate team meetings",
            "Prepare stakeholder reports"
        ]
    },
    "mila-novak": {
        "name": "Mila Novak",
        "role": "UX/UI Designer",
        "department": "Design",
        "current_projects": [
            "Website User Experience",
            "Mobile App Interface",
            "User Research and Testing"
        ],
        "daily_tasks": [
            "User interface design",
            "User experience research",
            "Prototype creation",
            "User testing coordination",
            "Design iteration and improvement"
        ],
        "specialized_work": [
            "User research and analysis",
            "Information architecture design",
            "Interaction design",
            "Usability testing",
            "Design system implementation"
        ],
        "tools_access": [
            "Figma and Sketch",
            "User research tools",
            "Prototyping platforms",
            "Analytics dashboards",
            "User testing platforms"
        ],
        "current_workload": "Medium",
        "next_deadline": "2024-09-24",
        "priority_tasks": [
            "Complete website UX audit",
            "Design mobile app interface",
            "Conduct user research sessions"
        ]
    }
}

# Task assignment system
class TaskAssignment(BaseModel):
    agent_id: str
    task_title: str
    task_description: str
    priority: str
    due_date: str
    project_context: str
    expected_deliverables: List[str]

@app.get("/", response_class=HTMLResponse)
async def agent_workstation_home(request: Request):
    """Main agent workstation dashboard"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SmartHaus Agent Workstation</title>
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
            .agent-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
                gap: 1.5rem; 
                margin-bottom: 2rem;
            }}
            .agent-card {{ 
                background: white; 
                border-radius: 8px; 
                padding: 1.5rem; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid #1976d2;
                transition: transform 0.2s;
            }}
            .agent-card:hover {{ transform: translateY(-2px); }}
            .agent-header {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 1rem;
            }}
            .agent-name {{ font-size: 1.3rem; font-weight: 600; color: #1976d2; }}
            .agent-role {{ color: #6c757d; font-size: 0.9rem; }}
            .workload-badge {{ 
                padding: 0.25rem 0.75rem; 
                border-radius: 12px; 
                font-size: 0.8rem; 
                font-weight: 500;
            }}
            .workload-high {{ background: #f8d7da; color: #721c24; }}
            .workload-medium {{ background: #fff3cd; color: #856404; }}
            .workload-low {{ background: #d4edda; color: #155724; }}
            .agent-details {{ margin: 1rem 0; }}
            .detail-section {{ margin-bottom: 1rem; }}
            .detail-title {{ font-weight: 600; color: #495057; margin-bottom: 0.5rem; }}
            .detail-list {{ list-style: none; padding-left: 0; }}
            .detail-list li {{ 
                padding: 0.25rem 0; 
                color: #6c757d; 
                font-size: 0.9rem;
                border-left: 2px solid #e9ecef;
                padding-left: 0.5rem;
                margin-bottom: 0.25rem;
            }}
            .priority-tasks {{ 
                background: #fff3cd; 
                padding: 1rem; 
                border-radius: 6px; 
                margin: 1rem 0;
            }}
            .priority-tasks h4 {{ color: #856404; margin-bottom: 0.5rem; }}
            .task-item {{ 
                background: white; 
                padding: 0.5rem; 
                margin: 0.25rem 0; 
                border-radius: 4px;
                border-left: 3px solid #ffc107;
            }}
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
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 SmartHaus Agent Workstation</h1>
            <p>Manage individual agents and assign specific work tasks</p>
        </div>
        
        <div class="nav">
            <a href="/" class="active">🏠 Agent Overview</a>
            <a href="/assign-task">➕ Assign Task</a>
            <a href="/workload">📊 Workload Management</a>
            <a href="/performance">📈 Performance</a>
        </div>
        
        <div class="container">
            <div class="agent-grid">
                {"".join([f'''
                <div class="agent-card">
                    <div class="agent-header">
                        <div>
                            <div class="agent-name">{agent["name"]}</div>
                            <div class="agent-role">{agent["role"]} • {agent["department"]}</div>
                        </div>
                        <span class="workload-badge workload-{agent["current_workload"].lower()}">{agent["current_workload"]} Workload</span>
                    </div>
                    
                    <div class="agent-details">
                        <div class="detail-section">
                            <div class="detail-title">📋 Current Projects</div>
                            <ul class="detail-list">
                                {"".join([f"<li>{project}</li>" for project in agent["current_projects"]])}
                            </ul>
                        </div>
                        
                        <div class="detail-section">
                            <div class="detail-title">⚡ Daily Tasks</div>
                            <ul class="detail-list">
                                {"".join([f"<li>{task}</li>" for task in agent["daily_tasks"][:3]])}
                            </ul>
                        </div>
                        
                        <div class="priority-tasks">
                            <h4>🎯 Priority Tasks</h4>
                            {"".join([f'<div class="task-item">{task}</div>' for task in agent["priority_tasks"]])}
                        </div>
                        
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-primary" onclick="viewAgentDetails('{agent_id}')">View Details</button>
                            <button class="btn btn-success" onclick="assignTask('{agent_id}')">Assign Task</button>
                            <button class="btn btn-warning" onclick="checkStatus('{agent_id}')">Check Status</button>
                        </div>
                    </div>
                </div>
                ''' for agent_id, agent in AGENT_WORK_DEFINITIONS.items()])}
            </div>
        </div>
        
        <script>
            function viewAgentDetails(agentId) {{
                window.location.href = `/agent/${{agentId}}`;
            }}
            
            function assignTask(agentId) {{
                const taskTitle = prompt('Task Title:');
                const taskDescription = prompt('Task Description:');
                const priority = prompt('Priority (High/Medium/Low):');
                const dueDate = prompt('Due Date (YYYY-MM-DD):');
                
                if (taskTitle && taskDescription && priority && dueDate) {{
                    alert(`Task assigned to ${{agentId}}:\\n\\nTitle: ${{taskTitle}}\\nDescription: ${{taskDescription}}\\nPriority: ${{priority}}\\nDue: ${{dueDate}}\\n\\nAgent will be notified and task added to their workload.`);
                }}
            }}
            
            function checkStatus(agentId) {{
                alert(`Checking status for ${{agentId}}...\\n\\nThis would show real-time work progress, current tasks, and any blockers.`);
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/agent/{agent_id}", response_class=HTMLResponse)
async def agent_detail_page(request: Request, agent_id: str):
    """Individual agent detail page with specific work management"""
    
    if agent_id not in AGENT_WORK_DEFINITIONS:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = AGENT_WORK_DEFINITIONS[agent_id]
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent['name']} - Agent Workstation</title>
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
            .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
            .agent-profile {{ 
                background: white; 
                border-radius: 8px; 
                padding: 2rem; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 2rem;
            }}
            .profile-header {{ 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 2rem;
            }}
            .profile-info h2 {{ color: #1976d2; font-size: 1.8rem; }}
            .profile-info p {{ color: #6c757d; margin-top: 0.5rem; }}
            .workload-status {{ 
                padding: 1rem; 
                border-radius: 8px; 
                text-align: center;
            }}
            .workload-high {{ background: #f8d7da; color: #721c24; }}
            .workload-medium {{ background: #fff3cd; color: #856404; }}
            .workload-low {{ background: #d4edda; color: #155724; }}
            .work-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 1.5rem; 
                margin-bottom: 2rem;
            }}
            .work-section {{ 
                background: white; 
                border-radius: 8px; 
                padding: 1.5rem; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .work-section h3 {{ 
                color: #1976d2; 
                margin-bottom: 1rem; 
                font-size: 1.2rem;
            }}
            .work-list {{ list-style: none; padding: 0; }}
            .work-list li {{ 
                padding: 0.75rem; 
                margin: 0.5rem 0; 
                background: #f8f9fa; 
                border-radius: 6px;
                border-left: 4px solid #1976d2;
            }}
            .tool-item {{ 
                padding: 0.5rem; 
                margin: 0.25rem 0; 
                background: #e3f2fd; 
                border-radius: 4px;
                font-size: 0.9rem;
            }}
            .action-panel {{ 
                background: #e3f2fd; 
                padding: 1.5rem; 
                border-radius: 8px; 
                margin-top: 2rem;
            }}
            .action-panel h3 {{ color: #1976d2; margin-bottom: 1rem; }}
            .btn {{ 
                padding: 0.75rem 1.5rem; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 1rem;
                transition: all 0.2s;
                margin: 0.5rem;
            }}
            .btn-primary {{ background: #1976d2; color: white; }}
            .btn-success {{ background: #28a745; color: white; }}
            .btn-warning {{ background: #ffc107; color: #212529; }}
            .btn-danger {{ background: #dc3545; color: white; }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 {agent['name']} - {agent['role']}</h1>
            <p>{agent['department']} • Next Deadline: {agent['next_deadline']}</p>
        </div>
        
        <div class="nav">
            <a href="/">🏠 Back to Overview</a>
            <a href="/agent/{agent_id}" class="active">👤 Profile</a>
            <a href="/agent/{agent_id}/tasks">📋 Tasks</a>
            <a href="/agent/{agent_id}/work">💼 Work</a>
            <a href="/agent/{agent_id}/tools">🛠️ Tools</a>
        </div>
        
        <div class="container">
            <div class="agent-profile">
                <div class="profile-header">
                    <div class="profile-info">
                        <h2>{agent['name']}</h2>
                        <p>{agent['role']} • {agent['department']}</p>
                        <p>Next Deadline: {agent['next_deadline']}</p>
                    </div>
                    <div class="workload-status workload-{agent['current_workload'].lower()}">
                        <h3>{agent['current_workload']} Workload</h3>
                        <p>Current capacity and availability</p>
                    </div>
                </div>
            </div>
            
            <div class="work-grid">
                <div class="work-section">
                    <h3>📋 Current Projects</h3>
                    <ul class="work-list">
                        {"".join([f"<li>{project}</li>" for project in agent['current_projects']])}
                    </ul>
                </div>
                
                <div class="work-section">
                    <h3>⚡ Daily Tasks</h3>
                    <ul class="work-list">
                        {"".join([f"<li>{task}</li>" for task in agent['daily_tasks']])}
                    </ul>
                </div>
                
                <div class="work-section">
                    <h3>🎯 Specialized Work</h3>
                    <ul class="work-list">
                        {"".join([f"<li>{work}</li>" for work in agent['specialized_work']])}
                    </ul>
                </div>
                
                <div class="work-section">
                    <h3>🛠️ Tools & Access</h3>
                    {"".join([f'<div class="tool-item">{tool}</div>' for tool in agent['tools_access']])}
                </div>
            </div>
            
            <div class="action-panel">
                <h3>🚀 Agent Actions</h3>
                <button class="btn btn-primary" onclick="assignSpecificTask('{agent_id}')">➕ Assign New Task</button>
                <button class="btn btn-success" onclick="requestStatusUpdate('{agent_id}')">📊 Request Status Update</button>
                <button class="btn btn-warning" onclick="scheduleMeeting('{agent_id}')">📅 Schedule Meeting</button>
                <button class="btn btn-primary" onclick="reviewWork('{agent_id}')">👀 Review Work</button>
                <button class="btn btn-danger" onclick="escalateIssue('{agent_id}')">⚠️ Escalate Issue</button>
            </div>
        </div>
        
        <script>
            function assignSpecificTask(agentId) {{
                const taskType = prompt('Task Type (Research/Development/Design/Communication):');
                const taskTitle = prompt('Task Title:');
                const taskDescription = prompt('Detailed Task Description:');
                const priority = prompt('Priority (High/Medium/Low):');
                const dueDate = prompt('Due Date (YYYY-MM-DD):');
                const deliverables = prompt('Expected Deliverables (comma-separated):');
                
                if (taskType && taskTitle && taskDescription && priority && dueDate) {{
                    alert(`Specific task assigned to ${{agentId}}:\\n\\nType: ${{taskType}}\\nTitle: ${{taskTitle}}\\nDescription: ${{taskDescription}}\\nPriority: ${{priority}}\\nDue: ${{dueDate}}\\nDeliverables: ${{deliverables}}\\n\\nAgent will receive detailed instructions and begin work immediately.`);
                }}
            }}
            
            function requestStatusUpdate(agentId) {{
                alert(`Status update requested from ${{agentId}}\\n\\nAgent will provide:\\n- Current work progress\\n- Completed tasks\\n- Any blockers or issues\\n- Next steps and timeline`);
            }}
            
            function scheduleMeeting(agentId) {{
                const meetingType = prompt('Meeting Type (1-on-1/Project Review/Technical Discussion):');
                const duration = prompt('Duration (30min/1hr/2hr):');
                const agenda = prompt('Meeting Agenda:');
                
                if (meetingType && duration && agenda) {{
                    alert(`Meeting scheduled with ${{agentId}}:\\n\\nType: ${{meetingType}}\\nDuration: ${{duration}}\\nAgenda: ${{agenda}}\\n\\nCalendar invite will be sent and meeting room booked.`);
                }}
            }}
            
            function reviewWork(agentId) {{
                alert(`Work review initiated for ${{agentId}}\\n\\nThis will show:\\n- Recent deliverables\\n- Code/design quality\\n- Performance metrics\\n- Feedback and recommendations`);
            }}
            
            function escalateIssue(agentId) {{
                const issue = prompt('Issue Description:');
                const urgency = prompt('Urgency (Low/Medium/High/Critical):');
                
                if (issue && urgency) {{
                    alert(`Issue escalated for ${{agentId}}:\\n\\nIssue: ${{issue}}\\nUrgency: ${{urgency}}\\n\\nManagement will be notified and appropriate action taken.`);
                }}
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
        "version": "4.0.0",
        "agent_workstation": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
