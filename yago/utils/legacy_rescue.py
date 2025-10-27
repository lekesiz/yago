"""
Legacy Code Rescue - YAGO's Secret Superpower
Analyzes, completes, and modernizes abandoned/broken projects
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger("YAGO")


class LegacyAnalysis:
    """Results of legacy code analysis"""
    def __init__(self):
        self.total_files = 0
        self.incomplete_functions = []
        self.missing_docstrings = []
        self.deprecated_patterns = []
        self.missing_tests = []
        self.complexity_issues = []
        self.completion_percentage = 0
        self.rescue_plan = []


class LegacyRescue:
    """Analyzes and rescues legacy/incomplete code"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analysis = LegacyAnalysis()

    def analyze_project(self) -> LegacyAnalysis:
        """Analyze project for issues"""
        py_files = list(self.project_path.rglob("*.py"))
        self.analysis.total_files = len(py_files)

        for file in py_files:
            self._analyze_file(file)

        # Calculate completion
        total_issues = (
            len(self.analysis.incomplete_functions) +
            len(self.analysis.missing_docstrings) +
            len(self.analysis.deprecated_patterns) +
            len(self.analysis.missing_tests)
        )

        if self.analysis.total_files > 0:
            max_issues = self.analysis.total_files * 5  # Assume 5 potential issues per file
            self.analysis.completion_percentage = max(0, 100 - (total_issues / max_issues * 100))

        self._generate_rescue_plan()
        return self.analysis

    def _analyze_file(self, file_path: Path):
        """Analyze single file"""
        try:
            code = file_path.read_text()
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check for incomplete functions (pass or ellipsis only)
                    if len(node.body) == 1:
                        if isinstance(node.body[0], ast.Pass) or isinstance(node.body[0], ast.Expr):
                            self.analysis.incomplete_functions.append({
                                'file': str(file_path),
                                'function': node.name,
                                'line': node.lineno
                            })

                    # Check for missing docstrings
                    if not ast.get_docstring(node):
                        self.analysis.missing_docstrings.append({
                            'file': str(file_path),
                            'function': node.name
                        })

            # Check for deprecated patterns
            if 'import urllib2' in code or 'print ' in code:  # Python 2 patterns
                self.analysis.deprecated_patterns.append({
                    'file': str(file_path),
                    'issue': 'Python 2 syntax detected'
                })

        except Exception as e:
            logger.debug(f"Analysis failed for {file_path}: {e}")

    def _generate_rescue_plan(self):
        """Generate step-by-step rescue plan"""
        plan = []

        if self.analysis.incomplete_functions:
            plan.append({
                'step': 1,
                'task': 'Complete incomplete functions',
                'count': len(self.analysis.incomplete_functions),
                'priority': 'HIGH'
            })

        if self.analysis.deprecated_patterns:
            plan.append({
                'step': 2,
                'task': 'Modernize deprecated code',
                'count': len(self.analysis.deprecated_patterns),
                'priority': 'HIGH'
            })

        if self.analysis.missing_docstrings:
            plan.append({
                'step': 3,
                'task': 'Add documentation',
                'count': len(self.analysis.missing_docstrings),
                'priority': 'MEDIUM'
            })

        if self.analysis.missing_tests:
            plan.append({
                'step': 4,
                'task': 'Create test suite',
                'count': len(self.analysis.missing_tests),
                'priority': 'MEDIUM'
            })

        self.analysis.rescue_plan = plan

    def get_rescue_report(self) -> str:
        """Generate rescue report"""
        report = "🦸 LEGACY CODE RESCUE REPORT\n\n"
        report += f"Project: {self.project_path}\n"
        report += f"Files Analyzed: {self.analysis.total_files}\n"
        report += f"Completion: {self.analysis.completion_percentage:.1f}%\n\n"

        report += "ISSUES FOUND:\n"
        report += f"- Incomplete Functions: {len(self.analysis.incomplete_functions)}\n"
        report += f"- Missing Docstrings: {len(self.analysis.missing_docstrings)}\n"
        report += f"- Deprecated Patterns: {len(self.analysis.deprecated_patterns)}\n\n"

        if self.analysis.rescue_plan:
            report += "RESCUE PLAN:\n"
            for item in self.analysis.rescue_plan:
                report += f"{item['step']}. {item['task']} ({item['count']} items) - {item['priority']}\n"

        return report


_legacy_rescue: Optional[LegacyRescue] = None

def get_legacy_rescue(project_path: str) -> LegacyRescue:
    global _legacy_rescue
    _legacy_rescue = LegacyRescue(project_path)
    return _legacy_rescue
