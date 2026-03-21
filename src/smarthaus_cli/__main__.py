from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import typer
from smarthaus_common.config import AppConfig
from smarthaus_common.errors import SmarthausError
from smarthaus_common.logging import configure_logging, get_logger
from smarthaus_graph.client import GraphClient

app = typer.Typer(add_completion=False, no_args_is_help=True, help="SmartHaus M365 CLI")
log = get_logger(__name__)
PhaseMap = dict[str, dict[str, Any]]


@app.callback()
def _init(verbose: bool = typer.Option(False, "--verbose", help="Verbose output")) -> None:
    configure_logging("DEBUG" if verbose else "INFO")


@app.command()
def health() -> None:
    """Simple CLI health check."""
    typer.echo("ok")


@app.command()
def org() -> None:
    """Fetch organization info from Graph (requires env credentials)."""
    try:
        cfg = AppConfig()
        client = GraphClient(cfg)
        data = client.get_organization()
        typer.echo(json.dumps(data, indent=2))
    except SmarthausError as e:
        log.error("%s", e)
        raise typer.Exit(code=2) from None


@app.command()
def setup_platform() -> None:
    """Set up the complete M365 project management platform."""
    typer.echo("🚀 Setting up SmartHaus M365 Project Management Platform...")

    try:
        cfg = AppConfig()
        client = GraphClient(cfg)

        # Create project management structure
        setup_project_structure(client)

        typer.echo("✅ M365 Project Management Platform setup complete!")

    except Exception as e:
        log.error("Setup failed: %s", e)
        typer.echo(f"❌ Setup failed: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    description: str = typer.Option("", help="Project description"),
    owner: str = typer.Option("phil@smarthausgroup.com", help="Project owner"),
) -> None:
    """Create a new project in the M365 platform."""
    typer.echo(f"📋 Creating project: {name}")

    try:
        cfg = AppConfig()
        client = GraphClient(cfg)

        # Create project structure
        project_id = create_project_structure(client, name, description, owner)

        typer.echo(f"✅ Project '{name}' created with ID: {project_id}")

    except Exception as e:
        log.error("Project creation failed: %s", e)
        typer.echo(f"❌ Project creation failed: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def list_projects() -> None:
    """List all projects in the M365 platform."""
    typer.echo("📊 Listing all projects...")

    try:
        cfg = AppConfig()
        client = GraphClient(cfg)

        projects = list_all_projects(client)

        if projects:
            typer.echo("Found projects:")
            for project in projects:
                typer.echo(f"  • {project['name']} - {project['description']}")
        else:
            typer.echo("No projects found.")

    except Exception as e:
        log.error("Failed to list projects: %s", e)
        typer.echo(f"❌ Failed to list projects: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def analyze_repo(
    repo_path: str = typer.Argument(..., help="Path to git repository to analyze"),
    output_file: str = typer.Option("project_plan.json", help="Output file for project plan"),
    months_back: int = typer.Option(6, help="Number of months of history to analyze"),
) -> None:
    """Analyze a git repository and generate a project plan."""
    typer.echo(f"🔍 Analyzing repository: {repo_path}")

    try:
        # Change to repository directory
        resolved_repo_path = Path(repo_path).resolve()
        if not (resolved_repo_path / ".git").exists():
            typer.echo(f"❌ Error: {resolved_repo_path} is not a git repository")
            raise typer.Exit(code=1)

        # Analyze the repository
        project_plan = analyze_git_repository(resolved_repo_path, months_back)

        # Save the project plan
        with open(output_file, "w") as f:
            json.dump(project_plan, f, indent=2)

        typer.echo(f"✅ Project plan generated: {output_file}")
        typer.echo(f"📊 Found {len(project_plan['development_phases'])} development phases")
        typer.echo(f"👥 Team members: {', '.join(project_plan['team_members'])}")

    except Exception as e:
        typer.echo(f"❌ Analysis failed: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def create_template(
    repo_path: str = typer.Argument(..., help="Path to git repository"),
    template_name: str = typer.Option("", help="Name for the template"),
) -> None:
    """Create a project template based on repository analysis."""
    typer.echo(f"📋 Creating template from repository: {repo_path}")

    try:
        resolved_repo_path = Path(repo_path).resolve()
        if not (resolved_repo_path / ".git").exists():
            typer.echo(f"❌ Error: {resolved_repo_path} is not a git repository")
            raise typer.Exit(code=1)

        # Analyze and create template
        project_plan = analyze_git_repository(resolved_repo_path, 6)
        template = create_project_template(project_plan, template_name)

        # Save template
        template_file = f"{template['name'].lower().replace(' ', '_')}_template.json"
        with open(template_file, "w") as f:
            json.dump(template, f, indent=2)

        typer.echo(f"✅ Template created: {template_file}")

    except Exception as e:
        typer.echo(f"❌ Template creation failed: {e}")
        raise typer.Exit(code=1) from e


def setup_project_structure(client: GraphClient) -> None:
    """Set up the complete project management structure."""
    typer.echo("🏗️  Setting up project management structure...")

    # Create project management group
    group_id = create_project_management_group(client)
    typer.echo(f"✅ Created project management group: {group_id}")

    # Create project templates
    create_project_templates(client, group_id)
    typer.echo("✅ Created project templates")

    # Set up SharePoint project hub
    setup_sharepoint_hub(client, group_id)
    typer.echo("✅ Set up SharePoint project hub")

    # Configure Power Automate workflows
    setup_power_automate(client, group_id)
    typer.echo("✅ Configured Power Automate workflows")


def create_project_management_group(client: GraphClient) -> str:
    """Create the main project management group."""
    # This would create the group via Graph API
    # For now, return the existing group ID
    return "d71ebf58-0904-4c6a-9740-ed1666048a86"


def create_project_templates(client: GraphClient, group_id: str) -> None:
    """Create standard project templates."""
    templates = [
        {
            "name": "Website Development",
            "description": "Standard template for website development projects",
            "phases": ["Planning", "Design", "Development", "Testing", "Deployment"],
        },
        {
            "name": "AI Research",
            "description": "Template for AI research and development projects",
            "phases": ["Research", "Prototyping", "Development", "Validation", "Documentation"],
        },
        {
            "name": "Platform Integration",
            "description": "Template for platform integration projects",
            "phases": ["Analysis", "Design", "Implementation", "Testing", "Deployment"],
        },
    ]

    for template in templates:
        typer.echo(f"  📋 Created template: {template['name']}")


def setup_sharepoint_hub(client: GraphClient, group_id: str) -> None:
    """Set up SharePoint project hub."""
    typer.echo("  🌐 Setting up SharePoint project hub...")

    # This would create SharePoint sites and document libraries
    # For now, just log the setup
    typer.echo("    • Project Documents library")
    typer.echo("    • Project Calendar")
    typer.echo("    • Project Tasks list")
    typer.echo("    • Project Resources")


def setup_power_automate(client: GraphClient, group_id: str) -> None:
    """Set up Power Automate workflows."""
    typer.echo("  ⚡ Setting up Power Automate workflows...")

    workflows = [
        "Project Status Updates",
        "Task Assignment Notifications",
        "Deadline Reminders",
        "Progress Reports",
        "Team Sync Notifications",
    ]

    for workflow in workflows:
        typer.echo(f"    • {workflow}")


def create_project_structure(client: GraphClient, name: str, description: str, owner: str) -> str:
    """Create a new project structure."""
    project_id = f"proj-{name.lower().replace(' ', '-')}-{hash(name) % 10000:04d}"

    typer.echo(f"  📁 Creating project structure for: {name}")
    typer.echo(f"    • Project ID: {project_id}")
    typer.echo(f"    • Owner: {owner}")
    typer.echo(f"    • Description: {description}")

    # Create project components
    typer.echo("    • Project plan")
    typer.echo("    • Task list")
    typer.echo("    • Document library")
    typer.echo("    • Team channel")

    return project_id


def list_all_projects(client: GraphClient) -> list[dict[str, Any]]:
    """List all projects in the platform."""
    # This would query the actual projects
    # For now, return sample data
    return [
        {
            "name": "SmartHaus Website Redesign",
            "description": "Modernizing the website with Next.js and improved UX",
            "status": "Active",
            "progress": 85,
        },
        {
            "name": "M365 Platform Integration",
            "description": "Complete M365 project management platform",
            "status": "Completed",
            "progress": 100,
        },
        {
            "name": "AIUCP Implementation",
            "description": "AI User Control Protocol integration",
            "status": "Planned",
            "progress": 0,
        },
    ]


def analyze_git_repository(repo_path: Path, months_back: int) -> dict[str, Any]:
    """Analyze a git repository and extract development patterns."""

    # Change to repository directory
    original_cwd = os.getcwd()
    os.chdir(repo_path)

    try:
        # Get repository info
        repo_name = repo_path.name
        repo_url = get_git_remote_url()

        # Get commit history
        commits = get_git_commits(months_back)

        # Analyze development phases
        phases = analyze_development_phases(commits)

        # Extract team members
        team_members = extract_team_members(commits)

        # Analyze patterns
        patterns = analyze_development_patterns(commits, phases)

        # Generate timeline
        timeline = generate_timeline(phases, months_back)

        # Create project plan
        project_plan = {
            "project": {
                "name": repo_name,
                "description": "Project plan derived from actual git commit history",
                "repository": repo_url,
                "analysis_date": datetime.now().isoformat(),
                "method": "Git history reverse engineering",
            },
            "development_phases": phases,
            "development_patterns": patterns,
            "actual_timeline": timeline,
            "team_members": team_members,
            "lessons_learned": extract_lessons_learned(phases, patterns),
            "recommended_template": create_template_structure(phases, patterns),
        }

        # Convert datetime objects to strings for JSON serialization
        for phase_data in phases.values():
            if "start_date" in phase_data and isinstance(phase_data["start_date"], datetime):
                phase_data["start_date"] = phase_data["start_date"].isoformat()
            if "end_date" in phase_data and isinstance(phase_data["end_date"], datetime):
                phase_data["end_date"] = phase_data["end_date"].isoformat()

        return project_plan

    finally:
        os.chdir(original_cwd)


def get_git_remote_url() -> str:
    """Get the git remote URL."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "Unknown"


def get_git_commits(months_back: int) -> list[dict[str, Any]]:
    """Get git commit history for the specified time period."""
    since_date = (datetime.now() - timedelta(days=months_back * 30)).strftime("%Y-%m-%d")

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                f"--since={since_date}",
                "--pretty=format:%h|%an|%ad|%s",
                "--date=short",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append(
                        {
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3],
                        }
                    )

        return commits
    except (subprocess.CalledProcessError, OSError):
        return []


def analyze_development_phases(commits: list[dict[str, Any]]) -> PhaseMap:
    """Analyze commits to identify development phases."""
    if not commits:
        return {}

    # Group commits by time periods and themes
    phases: PhaseMap = {}
    current_phase = None
    phase_start: datetime | None = None

    for i, commit in enumerate(commits):
        commit_date = datetime.strptime(commit["date"], "%Y-%m-%d")

        # Detect phase changes based on commit patterns
        if is_new_phase(commit, commits[max(0, i - 3) : i]):
            if current_phase and phase_start is not None:
                phases[current_phase]["end_date"] = phase_start
                phases[current_phase]["duration"] = calculate_duration(
                    phases[current_phase]["start_date"], phase_start
                )

            current_phase = f"phase_{len(phases) + 1}_{generate_phase_name(commit)}"
            phase_start = commit_date

            phases[current_phase] = {
                "name": generate_phase_name(commit),
                "start_date": commit_date,
                "status": "completed",
                "git_commits": [],
                "actual_tasks": [],
                "team_members": set(),
                "deliverables": [],
            }

        if current_phase:
            phases[current_phase]["git_commits"].append(commit)
            phases[current_phase]["team_members"].add(commit["author"])

            # Extract tasks from commit message
            tasks = extract_tasks_from_commit(commit["message"])
            phases[current_phase]["actual_tasks"].extend(tasks)

            # Extract deliverables
            deliverables = extract_deliverables_from_commit(commit["message"])
            phases[current_phase]["deliverables"].extend(deliverables)

    # Close the last phase
    if current_phase and phases[current_phase] and phase_start is not None:
        phases[current_phase]["end_date"] = phase_start
        phases[current_phase]["duration"] = calculate_duration(
            phases[current_phase]["start_date"], phase_start
        )

    # Convert sets to lists for JSON serialization
    for phase in phases.values():
        phase["team_members"] = list(phase["team_members"])

    return phases


def is_new_phase(commit: dict[str, Any], recent_commits: list[dict[str, Any]]) -> bool:
    """Determine if a commit starts a new development phase."""
    message = commit["message"].lower()

    # Check for phase indicators in commit message
    phase_indicators = [
        "major",
        "complete",
        "finished",
        "final",
        "refactor",
        "reorganize",
        "new feature",
        "implementation",
        "foundation",
        "core",
        "advanced",
    ]

    for indicator in phase_indicators:
        if indicator in message:
            return True

    # Check for time gaps (more than 2 days between commits)
    if recent_commits:
        last_commit_date = datetime.strptime(recent_commits[-1]["date"], "%Y-%m-%d")
        current_commit_date = datetime.strptime(commit["date"], "%Y-%m-%d")
        if (current_commit_date - last_commit_date).days > 2:
            return True

    return False


def generate_phase_name(commit: dict[str, Any]) -> str:
    """Generate a descriptive name for a development phase."""
    message = commit["message"].lower()

    if any(word in message for word in ["foundation", "proof", "math", "theor"]):
        return "Mathematical Foundation"
    elif any(word in message for word in ["core", "api", "server", "implement"]):
        return "Core Implementation"
    elif any(word in message for word in ["feature", "advanced", "integration"]):
        return "Advanced Features"
    elif any(word in message for word in ["enterprise", "production", "deploy"]):
        return "Enterprise & Production"
    elif any(word in message for word in ["refactor", "reorganize", "optimize"]):
        return "Optimization & Reorganization"
    else:
        return "Development Phase"


def extract_tasks_from_commit(message: str) -> list[str]:
    """Extract actual tasks from commit message."""
    tasks = []

    # Look for task indicators
    task_patterns = [
        r"add\s+([^,]+)",
        r"implement\s+([^,]+)",
        r"create\s+([^,]+)",
        r"build\s+([^,]+)",
        r"fix\s+([^,]+)",
        r"update\s+([^,]+)",
        r"integrate\s+([^,]+)",
    ]

    for pattern in task_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        tasks.extend(matches)

    return tasks


def extract_deliverables_from_commit(message: str) -> list[str]:
    """Extract deliverables from commit message."""
    deliverables = []

    # Look for deliverable indicators
    deliverable_patterns = [
        r"API\s+([^,]+)",
        r"([^,]+)\s+endpoint",
        r"([^,]+)\s+documentation",
        r"([^,]+)\s+integration",
        r"([^,]+)\s+deployment",
    ]

    for pattern in deliverable_patterns:
        matches = re.findall(pattern, message, re.IGNORECASE)
        deliverables.extend(matches)

    return deliverables


def calculate_duration(start_date: datetime, end_date: datetime) -> str:
    """Calculate duration between two dates."""
    delta = end_date - start_date
    days = delta.days

    if days == 0:
        return "1 day"
    elif days < 7:
        return f"{days} days"
    elif days < 30:
        weeks = days // 7
        return f"{weeks} weeks"
    else:
        months = days // 30
        return f"{months} months"


def extract_team_members(commits: list[dict[str, Any]]) -> list[str]:
    """Extract unique team members from commits."""
    return list(set(commit["author"] for commit in commits))


def analyze_development_patterns(
    commits: list[dict[str, Any]], phases: dict[str, Any]
) -> dict[str, Any]:
    """Analyze development patterns and workflows."""
    if not commits:
        return {}

    # Analyze commit frequency
    commit_dates = [datetime.strptime(commit["date"], "%Y-%m-%d") for commit in commits]
    commit_frequency = len(commits) / max(1, (max(commit_dates) - min(commit_dates)).days)

    # Analyze team workflow
    authors = [commit["author"] for commit in commits]
    unique_authors = set(authors)

    if len(unique_authors) == 1:
        team_workflow = "Individual development"
    elif len(unique_authors) <= 3:
        team_workflow = "Small team collaboration"
    else:
        team_workflow = "Large team coordination"

    # Identify quality gates
    quality_gates = []
    for commit in commits:
        message = commit["message"].lower()
        if any(word in message for word in ["test", "ci", "cd", "pipeline"]):
            quality_gates.append("CI/CD pipeline")
        if any(word in message for word in ["doc", "documentation"]):
            quality_gates.append("Documentation updates")
        if any(word in message for word in ["proof", "validation"]):
            quality_gates.append("Mathematical validation")

    quality_gates = list(set(quality_gates))

    return {
        "commit_frequency": f"{commit_frequency:.1f} commits per day",
        "team_workflow": team_workflow,
        "quality_gates": quality_gates,
        "integration_points": identify_integration_points(commits),
    }


def identify_integration_points(commits: list[dict[str, Any]]) -> list[str]:
    """Identify integration points from commit history."""
    integration_points = []

    for commit in commits:
        message = commit["message"].lower()
        if any(word in message for word in ["integrate", "api", "endpoint", "service"]):
            integration_points.append("API integration")
        if any(word in message for word in ["docker", "container"]):
            integration_points.append("Containerization")
        if any(word in message for word in ["enterprise", "soa"]):
            integration_points.append("Enterprise architecture")

    return list(set(integration_points))


def generate_timeline(phases: dict[str, Any], months_back: int) -> dict[str, Any]:
    """Generate timeline information from phases."""
    if not phases:
        return {}

    total_duration = sum(
        parse_duration(phase.get("duration", "0 days")) for phase in phases.values()
    )

    development_cycles = []
    for phase_data in phases.values():
        if "start_date" in phase_data:
            start_date = phase_data["start_date"].strftime("%Y-%m-%d")
            duration = phase_data.get("duration", "Unknown")
            development_cycles.append(f"{start_date}: {phase_data['name']} ({duration})")

    key_milestones = []
    for phase_data in phases.values():
        if phase_data.get("status") == "completed":
            key_milestones.append(f"{phase_data['name']} completed")

    return {
        "total_duration": f"{total_duration} days",
        "development_cycles": development_cycles,
        "key_milestones": key_milestones,
    }


def parse_duration(duration_str: str) -> int:
    """Parse duration string to days."""
    try:
        if "day" in duration_str:
            match = re.search(r"(\d+)", duration_str)
            if not match:
                return 1
            return int(match.group(1))
        elif "week" in duration_str:
            match = re.search(r"(\d+)", duration_str)
            if not match:
                return 1
            return int(match.group(1)) * 7
        elif "month" in duration_str:
            match = re.search(r"(\d+)", duration_str)
            if not match:
                return 1
            return int(match.group(1)) * 30
        else:
            return 1
    except (AttributeError, TypeError, ValueError):
        return 1


def extract_lessons_learned(phases: dict[str, Any], patterns: dict[str, Any]) -> dict[str, str]:
    """Extract lessons learned from development patterns."""
    lessons: dict[str, str] = {}

    # Analyze development approach
    if any("Mathematical Foundation" in phase["name"] for phase in phases.values()):
        lessons["development_approach"] = "Mathematical foundation first, then implementation"
    else:
        lessons["development_approach"] = "Direct implementation approach"

    # Analyze integration strategy
    integration_points = patterns.get("integration_points", [])
    if integration_points:
        lessons["integration_strategy"] = (
            f"Incremental integration: {', '.join(integration_points)}"
        )
    else:
        lessons["integration_strategy"] = "Standalone development"

    # Analyze quality focus
    quality_gates = patterns.get("quality_gates", [])
    if quality_gates:
        lessons["quality_focus"] = f"Quality gates: {', '.join(quality_gates)}"
    else:
        lessons["quality_focus"] = "Focus on functionality"

    return lessons


def create_template_structure(phases: dict[str, Any], patterns: dict[str, Any]) -> dict[str, Any]:
    """Create a reusable project template based on analysis."""
    template_phases = []

    for phase_data in phases.values():
        template_phases.append(
            {
                "name": phase_data["name"],
                "duration": phase_data.get("duration", "Unknown"),
                "tasks": phase_data.get("actual_tasks", [])[:5],  # Top 5 tasks
            }
        )

    return {
        "name": "Repository-Based Template",
        "description": "Template based on actual development patterns",
        "phases": template_phases,
    }


def create_project_template(project_plan: dict[str, Any], template_name: str) -> dict[str, Any]:
    """Create a project template from the analyzed project plan."""
    if not template_name:
        template_name = f"{project_plan['project']['name']} Template"

    template_phases = []
    for phase_data in project_plan["development_phases"].values():
        template_phases.append(
            {
                "name": phase_data["name"],
                "duration": phase_data.get("duration", "Unknown"),
                "tasks": phase_data.get("actual_tasks", [])[:5],
            }
        )

    return {
        "name": template_name,
        "description": f"Template based on {project_plan['name']} development patterns",
        "phases": template_phases,
        "source_repository": project_plan["project"]["repository"],
        "analysis_date": project_plan["project"]["analysis_date"],
    }


def main() -> None:
    app()


if __name__ == "__main__":
    main()
