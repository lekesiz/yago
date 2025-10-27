"""
Git Project Loader - External Repository Integration
YAGO v5.1.0

Allows YAGO to work on existing Git projects:
- Clone external repositories
- Analyze project structure
- Build context for AI agents
- Work within project directory
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger("YAGO.GitProjectLoader")


class ProjectAnalysis:
    """Project analysis result"""

    def __init__(self):
        self.repo_url: str = ""
        self.repo_name: str = ""
        self.local_path: str = ""
        self.branch: str = "main"
        self.total_files: int = 0
        self.total_lines: int = 0
        self.languages: Dict[str, int] = {}
        self.file_tree: List[str] = []
        self.dependencies: Dict[str, List[str]] = {}
        self.readme_content: Optional[str] = None
        self.has_tests: bool = False
        self.has_docs: bool = False
        self.last_commit: Dict[str, str] = {}


class GitProjectLoader:
    """
    Load and analyze external Git projects for YAGO

    Usage:
        loader = GitProjectLoader()
        analysis = loader.load_project("https://github.com/user/repo.git")
        context = loader.build_context(analysis)
    """

    def __init__(self, workspace_path: str = "./workspace/projects"):
        """
        Initialize Git Project Loader

        Args:
            workspace_path: Where to clone external projects
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"GitProjectLoader initialized: {self.workspace_path}")

    def load_project(self,
                    repo_url: str,
                    branch: Optional[str] = None,
                    depth: Optional[int] = None) -> ProjectAnalysis:
        """
        Clone a Git repository and analyze it

        Args:
            repo_url: Git repository URL (HTTPS or SSH)
            branch: Specific branch to clone (default: main/master)
            depth: Shallow clone depth (default: full clone)

        Returns:
            ProjectAnalysis object with full analysis
        """
        logger.info(f"Loading project: {repo_url}")

        # Extract repo name
        repo_name = self._extract_repo_name(repo_url)
        local_path = self.workspace_path / repo_name

        # Check if already cloned
        if local_path.exists():
            logger.warning(f"Project already exists: {local_path}")

            # Professional mode: auto-update without asking
            try:
                from utils.error_recovery import get_error_recovery
                recovery = get_error_recovery()
                if recovery.professional_mode:
                    logger.info("🤖 Professional mode: Auto-updating existing project")
                    self._git_pull(local_path)
                else:
                    choice = input(f"⚠️  {repo_name} already exists. [u]pdate, [d]elete, [k]eep? ")
                    if choice.lower() == 'u':
                        self._git_pull(local_path)
                    elif choice.lower() == 'd':
                        import shutil
                        shutil.rmtree(local_path)
                        self._git_clone(repo_url, local_path, branch, depth)
                    else:
                        logger.info("Using existing project")
            except EOFError:
                # No input available (background/automated mode)
                logger.info("🤖 Auto-mode: Updating existing project")
                self._git_pull(local_path)
        else:
            self._git_clone(repo_url, local_path, branch, depth)

        # Analyze the project
        analysis = self._analyze_project(repo_url, local_path, branch)

        logger.info(f"✅ Project loaded: {repo_name}")
        logger.info(f"   Files: {analysis.total_files}, Lines: {analysis.total_lines}")
        logger.info(f"   Languages: {', '.join(analysis.languages.keys())}")

        return analysis

    def _is_valid_git_url(self, url: str) -> bool:
        """Validate Git URL (HTTPS or SSH)"""
        import re
        patterns = [
            r"https?://github\.com/[\w-]+/[\w-]+(?:\.git)?",
            r"git@github\.com:[\w-]+/[\w-]+(?:\.git)?",
            r"https?://gitlab\.com/[\w-]+/[\w-]+(?:\.git)?",
            r"git@gitlab\.com:[\w-]+/[\w-]+(?:\.git)?",
        ]
        return any(re.match(pattern, url) for pattern in patterns)

    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL"""
        # https://github.com/user/repo.git -> repo
        # git@github.com:user/repo.git -> repo
        name = repo_url.rstrip('/').split('/')[-1]
        if name.endswith('.git'):
            name = name[:-4]
        return name

    def _git_clone(self,
                  repo_url: str,
                  local_path: Path,
                  branch: Optional[str] = None,
                  depth: Optional[int] = None):
        """Clone a Git repository"""
        cmd = ["git", "clone"]

        if branch:
            cmd.extend(["-b", branch])
        if depth:
            cmd.extend(["--depth", str(depth)])

        cmd.extend([repo_url, str(local_path)])

        logger.info(f"Cloning: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.debug(result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed: {e.stderr}")
            raise RuntimeError(f"Failed to clone repository: {e.stderr}")

    def _git_pull(self, local_path: Path):
        """Update existing repository"""
        logger.info(f"Updating: {local_path}")
        try:
            result = subprocess.run(
                ["git", "-C", str(local_path), "pull"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✅ Updated: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Git pull failed: {e.stderr}")

    def _analyze_project(self,
                        repo_url: str,
                        local_path: Path,
                        branch: Optional[str]) -> ProjectAnalysis:
        """Analyze project structure and content"""
        analysis = ProjectAnalysis()
        analysis.repo_url = repo_url
        analysis.repo_name = local_path.name
        analysis.local_path = str(local_path)

        # Get current branch
        try:
            result = subprocess.run(
                ["git", "-C", str(local_path), "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            analysis.branch = result.stdout.strip() or branch or "main"
        except:
            analysis.branch = branch or "main"

        # Get last commit info
        try:
            result = subprocess.run(
                ["git", "-C", str(local_path), "log", "-1", "--format=%H|%an|%ae|%s|%cd"],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                hash_val, author, email, message, date = result.stdout.strip().split('|')
                analysis.last_commit = {
                    "hash": hash_val,
                    "author": author,
                    "email": email,
                    "message": message,
                    "date": date
                }
        except:
            pass

        # Analyze files
        file_count = 0
        total_lines = 0
        languages = {}

        # Common code extensions and their languages
        lang_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.jsx': 'React', '.tsx': 'React', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.hpp': 'C++',
            '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
            '.cs': 'C#', '.swift': 'Swift', '.kt': 'Kotlin',
            '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
            '.sql': 'SQL', '.sh': 'Shell', '.yml': 'YAML', '.yaml': 'YAML',
            '.json': 'JSON', '.xml': 'XML', '.md': 'Markdown'
        }

        # Scan all files (exclude .git, node_modules, venv, etc.)
        exclude_dirs = {'.git', 'node_modules', 'venv', '__pycache__',
                       'dist', 'build', '.next', '.venv', 'env'}

        for root, dirs, files in os.walk(local_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(local_path)

                # Add to file tree
                analysis.file_tree.append(str(rel_path))
                file_count += 1

                # Count lines
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        total_lines += lines

                        # Track language
                        ext = file_path.suffix.lower()
                        if ext in lang_map:
                            lang = lang_map[ext]
                            languages[lang] = languages.get(lang, 0) + lines
                except:
                    pass

        analysis.total_files = file_count
        analysis.total_lines = total_lines
        analysis.languages = dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))

        # Check for README
        for readme_name in ['README.md', 'README.MD', 'README.txt', 'README']:
            readme_path = local_path / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        analysis.readme_content = f.read()
                    break
                except:
                    pass

        # Check for tests directory
        test_dirs = ['tests', 'test', '__tests__', 'spec']
        analysis.has_tests = any((local_path / d).exists() for d in test_dirs)

        # Check for docs
        docs_dirs = ['docs', 'documentation', 'doc']
        analysis.has_docs = any((local_path / d).exists() for d in docs_dirs)

        # Detect dependencies
        analysis.dependencies = self._detect_dependencies(local_path)

        return analysis

    def _detect_dependencies(self, project_path: Path) -> Dict[str, List[str]]:
        """Detect project dependencies from various config files"""
        deps = {}

        # Python: requirements.txt, setup.py, pyproject.toml
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    deps['python'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except:
                pass

        # Node.js: package.json
        package_file = project_path / "package.json"
        if package_file.exists():
            try:
                with open(package_file, 'r') as f:
                    package_data = json.load(f)
                    node_deps = []
                    if 'dependencies' in package_data:
                        node_deps.extend(package_data['dependencies'].keys())
                    if 'devDependencies' in package_data:
                        node_deps.extend(package_data['devDependencies'].keys())
                    deps['node'] = node_deps
            except:
                pass

        # Go: go.mod
        go_file = project_path / "go.mod"
        if go_file.exists():
            try:
                with open(go_file, 'r') as f:
                    go_deps = []
                    for line in f:
                        if line.strip().startswith('require'):
                            continue
                        if '\t' in line:
                            go_deps.append(line.strip().split()[0])
                    deps['go'] = go_deps
            except:
                pass

        return deps

    def build_context(self, analysis: ProjectAnalysis, max_length: int = 5000) -> str:
        """
        Build context string for AI agents

        Args:
            analysis: ProjectAnalysis object
            max_length: Maximum context length

        Returns:
            Formatted context string for AI
        """
        context_parts = []

        # Header
        context_parts.append(f"# 📦 Project: {analysis.repo_name}")
        context_parts.append(f"Repository: {analysis.repo_url}")
        context_parts.append(f"Branch: {analysis.branch}")
        context_parts.append(f"Local Path: {analysis.local_path}")
        context_parts.append("")

        # Last commit
        if analysis.last_commit:
            context_parts.append("## 📝 Last Commit")
            context_parts.append(f"- Author: {analysis.last_commit.get('author')} <{analysis.last_commit.get('email')}>")
            context_parts.append(f"- Message: {analysis.last_commit.get('message')}")
            context_parts.append(f"- Date: {analysis.last_commit.get('date')}")
            context_parts.append("")

        # Stats
        context_parts.append("## 📊 Statistics")
        context_parts.append(f"- Total Files: {analysis.total_files}")
        context_parts.append(f"- Total Lines: {analysis.total_lines:,}")
        context_parts.append("")

        # Languages
        if analysis.languages:
            context_parts.append("## 💻 Languages")
            for lang, lines in list(analysis.languages.items())[:5]:  # Top 5
                percentage = (lines / analysis.total_lines * 100) if analysis.total_lines else 0
                context_parts.append(f"- {lang}: {lines:,} lines ({percentage:.1f}%)")
            context_parts.append("")

        # Dependencies
        if analysis.dependencies:
            context_parts.append("## 📦 Dependencies")
            for lang, deps in analysis.dependencies.items():
                context_parts.append(f"### {lang.title()}")
                for dep in deps[:10]:  # First 10
                    context_parts.append(f"- {dep}")
                if len(deps) > 10:
                    context_parts.append(f"- ... and {len(deps) - 10} more")
            context_parts.append("")

        # File Tree (first 50 files)
        context_parts.append("## 📁 File Structure (sample)")
        for file_path in analysis.file_tree[:50]:
            context_parts.append(f"- {file_path}")
        if len(analysis.file_tree) > 50:
            context_parts.append(f"- ... and {len(analysis.file_tree) - 50} more files")
        context_parts.append("")

        # README excerpt
        if analysis.readme_content:
            context_parts.append("## 📖 README (excerpt)")
            readme_lines = analysis.readme_content.split('\n')[:20]
            context_parts.extend(readme_lines)
            if len(analysis.readme_content.split('\n')) > 20:
                context_parts.append("\n... (truncated)")
            context_parts.append("")

        # Tests & Docs
        context_parts.append("## ✅ Features")
        context_parts.append(f"- Has Tests: {'Yes' if analysis.has_tests else 'No'}")
        context_parts.append(f"- Has Documentation: {'Yes' if analysis.has_docs else 'No'}")

        # Build final context
        context = '\n'.join(context_parts)

        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length] + "\n\n... (truncated for length)"

        return context

    def get_project_summary(self, analysis: ProjectAnalysis) -> str:
        """Get a short summary for display"""
        langs = ', '.join(list(analysis.languages.keys())[:3])
        return (f"📦 {analysis.repo_name} | "
                f"{analysis.total_files} files | "
                f"{analysis.total_lines:,} lines | "
                f"{langs}")


# Singleton instance
_project_loader_instance = None


def get_project_loader(workspace_path: str = "./workspace/projects") -> GitProjectLoader:
    """Get GitProjectLoader singleton"""
    global _project_loader_instance
    if _project_loader_instance is None:
        _project_loader_instance = GitProjectLoader(workspace_path)
    return _project_loader_instance


def reset_project_loader():
    """Reset singleton (for testing)"""
    global _project_loader_instance
    _project_loader_instance = None


if __name__ == "__main__":
    # CLI for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python git_project_loader.py <repo_url>")
        sys.exit(1)

    repo_url = sys.argv[1]

    loader = get_project_loader()
    analysis = loader.load_project(repo_url)

    print("\n" + "=" * 60)
    print(loader.get_project_summary(analysis))
    print("=" * 60)
    print(loader.build_context(analysis))
