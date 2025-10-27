"""
Project Tools - External Git Project Integration Tools
YAGO v5.1.0

Tools for agents to work with external Git repositories.
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from utils.git_project_loader import get_project_loader


# Tool 1: Load Project
class LoadProjectInput(BaseModel):
    """Input for LoadProjectTool"""
    repo_url: str = Field(..., description="Git repository URL (HTTPS or SSH)")
    branch: Optional[str] = Field(None, description="Specific branch to clone (optional)")
    depth: Optional[int] = Field(None, description="Shallow clone depth (optional)")


class LoadProjectTool(BaseTool):
    name: str = "Load External Project"
    description: str = (
        "Clone and analyze an external Git repository. "
        "Provide a Git URL (HTTPS or SSH) to clone the project into workspace. "
        "Returns detailed project analysis including file structure, languages, dependencies, etc. "
        "Example: repo_url='https://github.com/user/repo.git'"
    )
    args_schema: Type[BaseModel] = LoadProjectInput

    def _run(self, repo_url: str, branch: Optional[str] = None, depth: Optional[int] = None) -> str:
        """Clone and analyze a Git repository"""
        try:
            loader = get_project_loader()
            analysis = loader.load_project(repo_url, branch, depth)

            # Build context
            context = loader.build_context(analysis)

            # Add summary at top
            summary = loader.get_project_summary(analysis)

            return f"{summary}\n\n{context}\n\n✅ Project loaded successfully at: {analysis.local_path}"

        except Exception as e:
            return f"❌ Error loading project: {str(e)}"


# Tool 2: Get Project Context
class GetProjectContextInput(BaseModel):
    """Input for GetProjectContextTool"""
    repo_name: str = Field(..., description="Repository name (e.g., 'yago' from 'https://github.com/user/yago.git')")


class GetProjectContextTool(BaseTool):
    name: str = "Get Project Context"
    description: str = (
        "Get detailed context about a previously loaded project. "
        "Provide the repository name to get file structure, dependencies, README, etc. "
        "Use this before making changes to understand the project."
    )
    args_schema: Type[BaseModel] = GetProjectContextInput

    def _run(self, repo_name: str) -> str:
        """Get context for a loaded project"""
        try:
            from pathlib import Path
            loader = get_project_loader()

            # Find project path
            project_path = Path(loader.workspace_path) / repo_name

            if not project_path.exists():
                available = [p.name for p in Path(loader.workspace_path).iterdir() if p.is_dir()]
                return (f"❌ Project '{repo_name}' not found. "
                       f"Available projects: {', '.join(available) if available else 'None'}\n"
                       f"Use 'Load External Project' tool first to clone a repository.")

            # Re-analyze project
            # Build a fake URL just to analyze
            fake_url = f"file://{project_path}"
            analysis = loader._analyze_project(fake_url, project_path, None)

            # Build context
            context = loader.build_context(analysis)
            summary = loader.get_project_summary(analysis)

            return f"{summary}\n\n{context}"

        except Exception as e:
            return f"❌ Error getting project context: {str(e)}"


# Tool 3: List Projects
class ListProjectsInput(BaseModel):
    """Input for ListProjectsTool"""
    pass  # No input needed


class ListProjectsTool(BaseTool):
    name: str = "List Loaded Projects"
    description: str = (
        "List all Git projects that have been loaded into YAGO workspace. "
        "Shows repository names and basic stats."
    )
    args_schema: Type[BaseModel] = ListProjectsInput

    def _run(self) -> str:
        """List all loaded projects"""
        try:
            from pathlib import Path
            loader = get_project_loader()

            projects_path = Path(loader.workspace_path)

            if not projects_path.exists():
                return "No projects loaded yet. Use 'Load External Project' to clone a repository."

            # List all directories
            projects = [p for p in projects_path.iterdir() if p.is_dir() and not p.name.startswith('.')]

            if not projects:
                return "No projects loaded yet. Use 'Load External Project' to clone a repository."

            result = ["📦 Loaded Projects:\n"]

            for i, project_path in enumerate(projects, 1):
                # Quick analysis
                total_files = sum(1 for _ in project_path.rglob('*') if _.is_file() and '.git' not in str(_))
                result.append(f"{i}. {project_path.name} ({total_files} files) - {project_path}")

            return '\n'.join(result)

        except Exception as e:
            return f"❌ Error listing projects: {str(e)}"


def get_project_tools():
    """Get all project tools"""
    return [
        LoadProjectTool(),
        GetProjectContextTool(),
        ListProjectsTool(),
    ]
