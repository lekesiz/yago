"""
YAGO v8.2 - Git Project Analyzer
Analyzes existing Git projects to find issues, TODOs, and incomplete features
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import shutil
from datetime import datetime


class GitProjectAnalyzer:
    """Analyzes Git projects for completion opportunities"""

    def __init__(self):
        self.temp_dir = None
        self.project_path = None

    def clone_repository(self, git_url: str) -> Dict[str, Any]:
        """Clone a Git repository for analysis"""
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="yago_git_")

            # Extract repo name from URL
            repo_name = git_url.rstrip('/').split('/')[-1].replace('.git', '')
            self.project_path = Path(self.temp_dir) / repo_name

            # Clone repository
            result = subprocess.run(
                ['git', 'clone', git_url, str(self.project_path)],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Git clone failed: {result.stderr}"
                }

            return {
                "success": True,
                "path": str(self.project_path),
                "repo_name": repo_name
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Git clone timeout (>5 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Clone error: {str(e)}"
            }

    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure and identify technology stack"""
        if not self.project_path or not self.project_path.exists():
            return {"error": "Project path not found"}

        analysis = {
            "languages": {},
            "frameworks": [],
            "package_managers": [],
            "config_files": [],
            "has_tests": False,
            "has_docs": False,
            "total_files": 0,
            "total_lines": 0
        }

        # Detect package managers and frameworks
        config_files_map = {
            'package.json': ('Node.js', 'npm'),
            'requirements.txt': ('Python', 'pip'),
            'Pipfile': ('Python', 'pipenv'),
            'pyproject.toml': ('Python', 'poetry'),
            'Gemfile': ('Ruby', 'bundler'),
            'pom.xml': ('Java', 'maven'),
            'build.gradle': ('Java', 'gradle'),
            'Cargo.toml': ('Rust', 'cargo'),
            'go.mod': ('Go', 'go modules'),
            'composer.json': ('PHP', 'composer')
        }

        # Scan project files
        for file_path in self.project_path.rglob('*'):
            if file_path.is_file():
                # Skip hidden files and git directory
                if any(part.startswith('.') for part in file_path.parts):
                    if '.git' in file_path.parts:
                        continue

                analysis['total_files'] += 1

                # Detect config files
                if file_path.name in config_files_map:
                    lang, pm = config_files_map[file_path.name]
                    analysis['config_files'].append(file_path.name)
                    if pm not in analysis['package_managers']:
                        analysis['package_managers'].append(pm)

                # Detect languages by extension
                ext = file_path.suffix.lower()
                if ext:
                    analysis['languages'][ext] = analysis['languages'].get(ext, 0) + 1

                # Count lines of code
                try:
                    if ext in ['.py', '.js', '.ts', '.java', '.go', '.rs', '.rb', '.php']:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            analysis['total_lines'] += len(f.readlines())
                except:
                    pass

                # Detect tests
                if 'test' in file_path.name.lower() or 'spec' in file_path.name.lower():
                    analysis['has_tests'] = True

                # Detect documentation
                if file_path.name.lower() in ['readme.md', 'readme.rst', 'readme.txt']:
                    analysis['has_docs'] = True

        return analysis

    def find_todos_and_fixmes(self) -> List[Dict[str, Any]]:
        """Find TODO, FIXME, HACK comments in code"""
        todos = []
        patterns = [
            (r'TODO[:\s]+(.*)', 'TODO'),
            (r'FIXME[:\s]+(.*)', 'FIXME'),
            (r'HACK[:\s]+(.*)', 'HACK'),
            (r'XXX[:\s]+(.*)', 'XXX'),
            (r'BUG[:\s]+(.*)', 'BUG'),
            (r'NOTE[:\s]+(.*)', 'NOTE')
        ]

        if not self.project_path:
            return []

        for file_path in self.project_path.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.git') for part in file_path.parts):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line_num, line in enumerate(lines, 1):
                            for pattern, tag_type in patterns:
                                matches = re.findall(pattern, line, re.IGNORECASE)
                                if matches:
                                    todos.append({
                                        'type': tag_type,
                                        'file': str(file_path.relative_to(self.project_path)),
                                        'line': line_num,
                                        'content': line.strip(),
                                        'message': matches[0].strip()
                                    })
                except:
                    continue

        return todos

    def find_incomplete_features(self) -> List[Dict[str, Any]]:
        """Find incomplete features by analyzing code patterns"""
        incomplete = []

        if not self.project_path:
            return []

        # Patterns that indicate incomplete work
        patterns = [
            (r'raise NotImplementedError', 'Not implemented'),
            (r'pass\s*#.*implement', 'Empty implementation'),
            (r'def\s+(\w+).*:\s*pass', 'Empty function'),
            (r'class\s+(\w+).*:\s*pass', 'Empty class'),
            (r'#\s*TODO.*implement', 'TODO implementation'),
        ]

        for file_path in self.project_path.rglob('*.py'):  # Start with Python
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    for line_num, line in enumerate(lines, 1):
                        for pattern, description in patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                incomplete.append({
                                    'file': str(file_path.relative_to(self.project_path)),
                                    'line': line_num,
                                    'type': description,
                                    'code_snippet': line.strip()
                                })
            except:
                continue

        return incomplete

    def analyze_git_history(self) -> Dict[str, Any]:
        """Analyze Git commit history"""
        if not self.project_path:
            return {}

        try:
            # Get commit count
            result = subprocess.run(
                ['git', '-C', str(self.project_path), 'rev-list', '--count', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            commit_count = int(result.stdout.strip()) if result.returncode == 0 else 0

            # Get contributors
            result = subprocess.run(
                ['git', '-C', str(self.project_path), 'log', '--format=%an', '--all'],
                capture_output=True,
                text=True,
                timeout=10
            )
            contributors = list(set(result.stdout.strip().split('\n'))) if result.returncode == 0 else []

            # Get last commit date
            result = subprocess.run(
                ['git', '-C', str(self.project_path), 'log', '-1', '--format=%ci'],
                capture_output=True,
                text=True,
                timeout=10
            )
            last_commit = result.stdout.strip() if result.returncode == 0 else None

            return {
                'commit_count': commit_count,
                'contributors': contributors,
                'contributor_count': len(contributors),
                'last_commit': last_commit
            }
        except:
            return {}

    def generate_completion_report(self, git_url: str) -> Dict[str, Any]:
        """Generate comprehensive completion report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'git_url': git_url,
            'status': 'analyzing'
        }

        # Clone repository
        clone_result = self.clone_repository(git_url)
        if not clone_result.get('success'):
            report['status'] = 'error'
            report['error'] = clone_result.get('error')
            return report

        report['repo_name'] = clone_result['repo_name']
        report['local_path'] = clone_result['path']

        # Analyze structure
        report['structure'] = self.analyze_project_structure()

        # Find TODOs
        report['todos'] = self.find_todos_and_fixmes()
        report['todo_count'] = len(report['todos'])

        # Find incomplete features
        report['incomplete_features'] = self.find_incomplete_features()
        report['incomplete_count'] = len(report['incomplete_features'])

        # Analyze Git history
        report['git_history'] = self.analyze_git_history()

        # Calculate completion score
        total_issues = report['todo_count'] + report['incomplete_count']
        has_tests = report['structure'].get('has_tests', False)
        has_docs = report['structure'].get('has_docs', False)

        completion_score = 100
        completion_score -= min(total_issues * 2, 40)  # Max 40 points for issues
        if not has_tests:
            completion_score -= 20
        if not has_docs:
            completion_score -= 10

        report['completion_score'] = max(0, completion_score)
        report['status'] = 'completed'

        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)

        return report

    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        if report['todo_count'] > 0:
            recommendations.append(f"Complete {report['todo_count']} TODO items")

        if report['incomplete_count'] > 0:
            recommendations.append(f"Implement {report['incomplete_count']} incomplete features")

        if not report['structure'].get('has_tests'):
            recommendations.append("Add unit tests for better code coverage")

        if not report['structure'].get('has_docs'):
            recommendations.append("Create comprehensive documentation (README.md)")

        if report['structure'].get('total_files', 0) > 0:
            avg_lines = report['structure']['total_lines'] / report['structure']['total_files']
            if avg_lines > 500:
                recommendations.append("Consider refactoring large files for better maintainability")

        return recommendations

    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
