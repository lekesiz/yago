"""
Git Tools for YAGO Agents
Allows agents to use git operations
"""

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from utils.git_autopilot import get_git_autopilot


class GitInitInput(BaseModel):
    """Input for GitInitTool"""
    initial_commit: bool = Field(True, description="Create initial commit")


class GitInitTool(BaseTool):
    name: str = "git_init"
    description: str = (
        "Initialize git repository in workspace. "
        "Creates .gitignore and optionally makes initial commit. "
        "Use this at the start of a new project."
    )
    args_schema: Type[BaseModel] = GitInitInput

    def _run(self, initial_commit: bool = True) -> str:
        """Initialize git repository"""
        git = get_git_autopilot()
        success = git.init_repo(initial_commit=initial_commit)

        if success:
            return "✅ Git repository initialized successfully"
        else:
            return "❌ Failed to initialize git repository"


class GitCommitInput(BaseModel):
    """Input for GitCommitTool"""
    message: Optional[str] = Field(None, description="Commit message (auto-generated if not provided)")
    project_idea: Optional[str] = Field(None, description="Project idea for message generation")


class GitCommitTool(BaseTool):
    name: str = "git_commit"
    description: str = (
        "Create git commit with all changes. "
        "Auto-generates intelligent commit message if not provided. "
        "Use this after completing a feature or milestone."
    )
    args_schema: Type[BaseModel] = GitCommitInput

    def _run(self, message: Optional[str] = None, project_idea: Optional[str] = None) -> str:
        """Create commit"""
        git = get_git_autopilot()

        if not git.is_git_repo():
            return "❌ Not a git repository. Use git_init first."

        success, result = git.commit(message=message, add_all=True, project_idea=project_idea)

        if success:
            if result == "no_changes":
                return "ℹ️  No changes to commit"
            return f"✅ Created commit: {result}"
        else:
            return f"❌ Commit failed: {result}"


class GitStatusInput(BaseModel):
    """Input for GitStatusTool"""
    pass  # No input needed


class GitStatusTool(BaseTool):
    name: str = "git_status"
    description: str = (
        "Check git repository status. "
        "Shows modified, added, deleted, and untracked files. "
        "Use this to see what changes are pending."
    )
    args_schema: Type[BaseModel] = GitStatusInput

    def _run(self) -> str:
        """Get git status"""
        git = get_git_autopilot()

        if not git.is_git_repo():
            return "❌ Not a git repository"

        status = git.status()

        if "error" in status:
            return f"❌ {status['error'][0]}"

        # Format output
        result = "📊 Git Status:\n\n"

        if status["modified"]:
            result += f"Modified ({len(status['modified'])}):\n"
            for file in status["modified"][:10]:  # Limit to 10
                result += f"  - {file}\n"

        if status["untracked"]:
            result += f"\nUntracked ({len(status['untracked'])}):\n"
            for file in status["untracked"][:10]:
                result += f"  - {file}\n"

        if status["added"]:
            result += f"\nAdded ({len(status['added'])}):\n"
            for file in status["added"][:10]:
                result += f"  - {file}\n"

        if status["deleted"]:
            result += f"\nDeleted ({len(status['deleted'])}):\n"
            for file in status["deleted"][:10]:
                result += f"  - {file}\n"

        if not any([status["modified"], status["untracked"], status["added"], status["deleted"]]):
            result += "Working tree clean ✅"

        return result


class GitLogInput(BaseModel):
    """Input for GitLogTool"""
    num_commits: int = Field(5, description="Number of recent commits to show")


class GitLogTool(BaseTool):
    name: str = "git_log"
    description: str = (
        "View commit history. "
        "Shows recent commits with hash, author, date, and message. "
        "Use this to review project history."
    )
    args_schema: Type[BaseModel] = GitLogInput

    def _run(self, num_commits: int = 5) -> str:
        """Get commit log"""
        git = get_git_autopilot()

        if not git.is_git_repo():
            return "❌ Not a git repository"

        commits = git.get_log(num_commits=num_commits)

        if not commits:
            return "ℹ️  No commits yet"

        result = f"📜 Recent Commits (last {num_commits}):\n\n"

        for commit in commits:
            result += f"{commit['hash']} - {commit['date']}\n"
            result += f"  Author: {commit['author']}\n"
            result += f"  Message: {commit['message']}\n\n"

        return result


# Export all git tools
def get_git_tools():
    """Get all git tools for agents"""
    return [
        GitInitTool(),
        GitCommitTool(),
        GitStatusTool(),
        GitLogTool(),
    ]
