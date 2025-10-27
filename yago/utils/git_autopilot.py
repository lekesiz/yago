"""
Git Auto-Pilot for YAGO
Automatically manages git operations for generated code
"""

import subprocess
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from datetime import datetime
import logging

logger = logging.getLogger("YAGO")


class GitAutoPilot:
    """Automatic Git operations manager"""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace = Path(workspace_path).resolve()
        self.enabled = False
        self.repo_initialized = False

    def is_git_repo(self) -> bool:
        """Check if workspace is a git repository"""
        git_dir = self.workspace / ".git"
        return git_dir.exists()

    def init_repo(self, initial_commit: bool = True) -> bool:
        """
        Initialize git repository in workspace

        Args:
            initial_commit: Create initial commit

        Returns:
            Success status
        """
        try:
            if self.is_git_repo():
                logger.info("📦 Git repository already exists")
                self.repo_initialized = True
                return True

            # Git init
            result = subprocess.run(
                ["git", "init"],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"Failed to init git: {result.stderr}")
                return False

            logger.info("📦 Git repository initialized")

            # Create .gitignore
            self._create_gitignore()

            # Initial commit
            if initial_commit:
                self.commit(
                    message="Initial commit - YAGO generated project",
                    add_all=True
                )

            self.repo_initialized = True
            return True

        except Exception as e:
            logger.error(f"Git init error: {e}")
            return False

    def _create_gitignore(self):
        """Create sensible .gitignore file"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Env
.env
.env.local

# Logs
*.log
logs/

# Test
.pytest_cache/
.coverage
htmlcov/
"""
        gitignore_path = self.workspace / ".gitignore"
        gitignore_path.write_text(gitignore_content)
        logger.debug("Created .gitignore")

    def status(self) -> Dict[str, List[str]]:
        """
        Get git status

        Returns:
            Dictionary with file lists by status
        """
        if not self.is_git_repo():
            return {"error": ["Not a git repository"]}

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.workspace,
            capture_output=True,
            text=True
        )

        status = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": []
        }

        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            code = line[:2]
            filename = line[3:]

            if code == "??":
                status["untracked"].append(filename)
            elif code[0] == "M" or code[1] == "M":
                status["modified"].append(filename)
            elif code[0] == "A":
                status["added"].append(filename)
            elif code[0] == "D":
                status["deleted"].append(filename)

        return status

    def add(self, files: Optional[List[str]] = None, all: bool = False) -> bool:
        """
        Add files to staging

        Args:
            files: List of file paths to add
            all: Add all changes

        Returns:
            Success status
        """
        if not self.is_git_repo():
            logger.warning("Not a git repository")
            return False

        try:
            if all:
                cmd = ["git", "add", "-A"]
            elif files:
                cmd = ["git", "add"] + files
            else:
                logger.warning("No files specified and all=False")
                return False

            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"Git add failed: {result.stderr}")
                return False

            logger.debug(f"✅ Staged files")
            return True

        except Exception as e:
            logger.error(f"Git add error: {e}")
            return False

    def generate_commit_message(
        self,
        files_changed: List[str],
        project_idea: Optional[str] = None
    ) -> str:
        """
        Generate intelligent commit message

        Args:
            files_changed: List of changed files
            project_idea: Original project idea

        Returns:
            Generated commit message
        """
        # Analyze file types
        file_types = set()
        for file in files_changed:
            ext = Path(file).suffix
            if ext:
                file_types.add(ext[1:])  # Remove dot

        # Count files
        num_files = len(files_changed)

        # Generate message based on context
        if project_idea:
            summary = f"Implement {project_idea}"
        else:
            summary = "Add generated code"

        # Add details
        details = []
        if "py" in file_types:
            py_files = [f for f in files_changed if f.endswith(".py")]
            details.append(f"- {len(py_files)} Python file(s)")

        if "md" in file_types:
            details.append(f"- Documentation")

        if "txt" in file_types or "requirements.txt" in files_changed:
            details.append(f"- Dependencies")

        if "json" in file_types or "yaml" in file_types or "yml" in file_types:
            details.append(f"- Configuration")

        # Build final message
        message = summary + "\n\n"
        if details:
            message += "\n".join(details) + "\n\n"

        message += f"Generated by YAGO ({num_files} file(s) changed)\n"
        message += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return message

    def commit(
        self,
        message: Optional[str] = None,
        add_all: bool = True,
        files: Optional[List[str]] = None,
        project_idea: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Create git commit

        Args:
            message: Commit message (auto-generated if None)
            add_all: Add all changes before commit
            files: Specific files to add (if not add_all)
            project_idea: Project idea for commit message generation

        Returns:
            (success, commit_hash or error)
        """
        if not self.is_git_repo():
            logger.warning("Not a git repository")
            return False, "Not a git repository"

        try:
            # Add files
            if add_all:
                self.add(all=True)
            elif files:
                self.add(files=files)

            # Check if there are changes to commit
            status = self.status()
            total_changes = (
                len(status.get("modified", [])) +
                len(status.get("added", [])) +
                len(status.get("deleted", [])) +
                len(status.get("untracked", []))
            )

            if total_changes == 0:
                logger.info("No changes to commit")
                return True, "no_changes"

            # Generate message if not provided
            if not message:
                all_files = (
                    status.get("modified", []) +
                    status.get("added", []) +
                    status.get("deleted", []) +
                    status.get("untracked", [])
                )
                message = self.generate_commit_message(all_files, project_idea)

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"Git commit failed: {result.stderr}")
                return False, result.stderr

            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )

            commit_hash = hash_result.stdout.strip()[:7]
            logger.info(f"📝 Committed: {commit_hash}")

            return True, commit_hash

        except Exception as e:
            logger.error(f"Git commit error: {e}")
            return False, str(e)

    def create_branch(self, branch_name: str, checkout: bool = True) -> bool:
        """
        Create new branch

        Args:
            branch_name: Name of new branch
            checkout: Switch to new branch

        Returns:
            Success status
        """
        if not self.is_git_repo():
            return False

        try:
            # Create branch
            cmd = ["git", "branch", branch_name]
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"Branch creation failed: {result.stderr}")
                return False

            logger.info(f"🌿 Created branch: {branch_name}")

            # Checkout if requested
            if checkout:
                checkout_result = subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=self.workspace,
                    capture_output=True,
                    text=True
                )

                if checkout_result.returncode != 0:
                    logger.error(f"Checkout failed: {checkout_result.stderr}")
                    return False

                logger.info(f"✅ Switched to branch: {branch_name}")

            return True

        except Exception as e:
            logger.error(f"Branch creation error: {e}")
            return False

    def get_log(self, num_commits: int = 5) -> List[Dict[str, str]]:
        """
        Get commit history

        Args:
            num_commits: Number of recent commits to retrieve

        Returns:
            List of commit info dicts
        """
        if not self.is_git_repo():
            return []

        try:
            result = subprocess.run(
                ["git", "log", f"-{num_commits}", "--pretty=format:%h|%an|%ae|%ad|%s"],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })

            return commits

        except Exception as e:
            logger.error(f"Git log error: {e}")
            return []


# Singleton instance
_git_autopilot: Optional[GitAutoPilot] = None


def get_git_autopilot(workspace_path: str = "./workspace") -> GitAutoPilot:
    """Get or create Git Auto-Pilot singleton"""
    global _git_autopilot
    if _git_autopilot is None:
        _git_autopilot = GitAutoPilot(workspace_path=workspace_path)
    return _git_autopilot


def reset_git_autopilot(workspace_path: str = "./workspace"):
    """Reset Git Auto-Pilot (for new project)"""
    global _git_autopilot
    _git_autopilot = GitAutoPilot(workspace_path=workspace_path)
