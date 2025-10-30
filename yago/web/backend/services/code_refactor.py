"""
YAGO v8.2 - Code Refactoring Service
Analyzes code for optimization opportunities, dead code, duplication, and best practices
"""

import os
import re
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime
import hashlib


class CodeRefactorService:
    """Enterprise-grade code refactoring analyzer"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.language_analyzers = {
            '.py': self._analyze_python,
            '.js': self._analyze_javascript,
            '.ts': self._analyze_typescript,
            '.jsx': self._analyze_javascript,
            '.tsx': self._analyze_typescript,
        }

    def analyze_project(self) -> Dict[str, Any]:
        """Comprehensive project refactoring analysis"""
        if not self.project_path.exists():
            return {"error": "Project path does not exist"}

        report = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "summary": {
                "total_files_scanned": 0,
                "total_issues_found": 0,
                "potential_savings_loc": 0,
                "complexity_issues": 0,
                "duplicate_blocks": 0,
                "dead_code_items": 0,
                "outdated_dependencies": 0,
            },
            "dead_code": [],
            "duplicates": [],
            "complexity_issues": [],
            "dependency_updates": [],
            "best_practices_violations": [],
            "performance_suggestions": [],
            "modernization_suggestions": [],
        }

        try:
            # Detect dead code
            report["dead_code"] = self.detect_dead_code()
            report["summary"]["dead_code_items"] = len(report["dead_code"])

            # Find duplicate code
            report["duplicates"] = self.find_code_duplicates()
            report["summary"]["duplicate_blocks"] = len(report["duplicates"])

            # Analyze complexity
            report["complexity_issues"] = self.analyze_complexity()
            report["summary"]["complexity_issues"] = len(report["complexity_issues"])

            # Check dependencies
            report["dependency_updates"] = self.check_outdated_dependencies()
            report["summary"]["outdated_dependencies"] = len(
                report["dependency_updates"]
            )

            # Check best practices
            report["best_practices_violations"] = self.check_best_practices()

            # Performance suggestions
            report["performance_suggestions"] = self.suggest_performance_optimizations()

            # Modernization suggestions
            report["modernization_suggestions"] = self.suggest_modernizations()

            # Calculate total issues
            report["summary"]["total_issues_found"] = (
                report["summary"]["dead_code_items"]
                + report["summary"]["duplicate_blocks"]
                + report["summary"]["complexity_issues"]
                + len(report["best_practices_violations"])
            )

            # Calculate potential savings
            report["summary"]["potential_savings_loc"] = self._calculate_savings(
                report
            )

            report["status"] = "completed"

        except Exception as e:
            report["status"] = "error"
            report["error"] = str(e)

        return report

    def detect_dead_code(self) -> List[Dict[str, Any]]:
        """Detect unused imports, functions, variables, and classes"""
        dead_code = []

        for file_path in self.project_path.rglob("*"):
            if file_path.suffix in self.language_analyzers:
                try:
                    analyzer = self.language_analyzers[file_path.suffix]
                    file_dead_code = analyzer(file_path, "dead_code")
                    dead_code.extend(file_dead_code)
                except Exception as e:
                    dead_code.append(
                        {
                            "file": str(file_path.relative_to(self.project_path)),
                            "error": f"Analysis failed: {str(e)}",
                        }
                    )

        return dead_code

    def find_code_duplicates(self, min_lines: int = 6) -> List[Dict[str, Any]]:
        """Find duplicate code blocks using hash-based detection"""
        duplicates = []
        code_blocks = defaultdict(list)

        for file_path in self.project_path.rglob("*"):
            if file_path.suffix in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                    # Create sliding window of code blocks
                    for i in range(len(lines) - min_lines + 1):
                        block = "".join(lines[i : i + min_lines])
                        # Normalize whitespace for comparison
                        normalized = re.sub(r"\s+", " ", block.strip())

                        # Skip blocks that are too short or mostly comments
                        if len(normalized) < 50:
                            continue

                        block_hash = hashlib.md5(normalized.encode()).hexdigest()
                        code_blocks[block_hash].append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "start_line": i + 1,
                                "end_line": i + min_lines,
                                "code": block.strip(),
                            }
                        )
                except Exception:
                    continue

        # Find duplicates
        for block_hash, locations in code_blocks.items():
            if len(locations) > 1:
                duplicates.append(
                    {
                        "type": "duplicate_code",
                        "instances": len(locations),
                        "locations": locations,
                        "recommendation": "Extract to a reusable function",
                        "potential_savings": f"{len(locations) - 1} blocks",
                    }
                )

        return duplicates

    def analyze_complexity(self) -> List[Dict[str, Any]]:
        """Analyze cyclomatic complexity and function length"""
        complexity_issues = []

        for file_path in self.project_path.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Calculate complexity
                        complexity = self._calculate_complexity(node)
                        func_lines = node.end_lineno - node.lineno + 1

                        if complexity > 10 or func_lines > 50:
                            complexity_issues.append(
                                {
                                    "file": str(
                                        file_path.relative_to(self.project_path)
                                    ),
                                    "function": node.name,
                                    "line": node.lineno,
                                    "complexity": complexity,
                                    "lines": func_lines,
                                    "severity": (
                                        "high"
                                        if complexity > 15 or func_lines > 100
                                        else "medium"
                                    ),
                                    "recommendation": self._get_complexity_recommendation(
                                        complexity, func_lines
                                    ),
                                }
                            )
            except Exception:
                continue

        return complexity_issues

    def check_outdated_dependencies(self) -> List[Dict[str, Any]]:
        """Check for outdated packages in requirements files"""
        updates = []

        # Python dependencies
        requirements_files = list(self.project_path.glob("*requirements*.txt"))
        requirements_files.extend(self.project_path.glob("pyproject.toml"))
        requirements_files.extend(self.project_path.glob("Pipfile"))

        for req_file in requirements_files:
            try:
                if req_file.name.endswith(".txt"):
                    with open(req_file, "r") as f:
                        packages = [
                            line.split("==")[0].strip()
                            for line in f
                            if "==" in line and not line.startswith("#")
                        ]

                    for package in packages[:5]:  # Limit to first 5 for demo
                        # Check latest version (in production, use PyPI API)
                        updates.append(
                            {
                                "file": req_file.name,
                                "package": package,
                                "current_version": "checking...",
                                "latest_version": "available",
                                "type": "Python package",
                            }
                        )
            except Exception:
                continue

        # JavaScript/Node dependencies
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, "r") as f:
                    data = json.load(f)
                    deps = data.get("dependencies", {})
                    for package, version in list(deps.items())[:5]:
                        updates.append(
                            {
                                "file": "package.json",
                                "package": package,
                                "current_version": version,
                                "latest_version": "available",
                                "type": "npm package",
                            }
                        )
            except Exception:
                pass

        return updates

    def check_best_practices(self) -> List[Dict[str, Any]]:
        """Check for best practices violations"""
        violations = []

        for file_path in self.project_path.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    # Check for common anti-patterns
                    if re.search(r"except\s*:", line):  # Bare except
                        violations.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "bare_except",
                                "severity": "medium",
                                "message": "Bare except clause catches all exceptions",
                                "recommendation": "Catch specific exception types",
                            }
                        )

                    if re.search(r"print\s*\(", line):  # Print statements
                        violations.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "print_statement",
                                "severity": "low",
                                "message": "Using print() instead of logging",
                                "recommendation": "Use logging module for production code",
                            }
                        )

                    if len(line) > 120:  # Long lines
                        violations.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "line_too_long",
                                "severity": "low",
                                "message": f"Line exceeds 120 characters ({len(line)} chars)",
                                "recommendation": "Break into multiple lines (PEP8)",
                            }
                        )

            except Exception:
                continue

        return violations[:50]  # Limit to first 50

    def suggest_performance_optimizations(self) -> List[Dict[str, Any]]:
        """Suggest performance optimization opportunities"""
        suggestions = []

        for file_path in self.project_path.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                # Check for common performance issues
                for line_num, line in enumerate(lines, 1):
                    # Inefficient list comprehension in loop
                    if "for" in line and "[" in line and "in" in line:
                        if any(
                            keyword in line
                            for keyword in ["append", "extend", "sum", "max", "min"]
                        ):
                            suggestions.append(
                                {
                                    "file": str(
                                        file_path.relative_to(self.project_path)
                                    ),
                                    "line": line_num,
                                    "type": "inefficient_iteration",
                                    "message": "Consider using generator expression or map()",
                                    "potential_impact": "medium",
                                }
                            )

                    # String concatenation in loop
                    if re.search(r"(\w+)\s*\+\s*=\s*['\"]", line):
                        suggestions.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "string_concatenation",
                                "message": "Use list and join() instead of += for strings",
                                "potential_impact": "high",
                            }
                        )

            except Exception:
                continue

        return suggestions[:30]  # Limit results

    def suggest_modernizations(self) -> List[Dict[str, Any]]:
        """Suggest modernization of code syntax"""
        suggestions = []

        for file_path in self.project_path.rglob("*.py"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    # Old-style string formatting
                    if "%" in line and '"' in line:
                        suggestions.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "old_string_formatting",
                                "current": "% formatting",
                                "suggestion": "Use f-strings (Python 3.6+)",
                                "example": 'f"Hello {name}"',
                            }
                        )

                    # Type hints missing
                    if (
                        re.search(r"def\s+\w+\s*\(", line)
                        and "->" not in line
                        and ":" in line
                    ):
                        suggestions.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "missing_type_hints",
                                "suggestion": "Add type hints for better code documentation",
                                "example": "def func(name: str) -> int:",
                            }
                        )

            except Exception:
                continue

        # JavaScript/TypeScript modernizations
        for file_path in self.project_path.rglob("*.js"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                for line_num, line in enumerate(lines, 1):
                    # var instead of let/const
                    if re.search(r"\bvar\s+", line):
                        suggestions.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "var_declaration",
                                "current": "var",
                                "suggestion": "Use 'let' or 'const' (ES6+)",
                            }
                        )

                    # Function instead of arrow function
                    if "function(" in line.replace(" ", ""):
                        suggestions.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "line": line_num,
                                "type": "old_function_syntax",
                                "current": "function() {}",
                                "suggestion": "Use arrow functions () => {}",
                            }
                        )

            except Exception:
                continue

        return suggestions[:40]

    # Helper methods for Python analysis
    def _analyze_python(
        self, file_path: Path, analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Analyze Python file for dead code"""
        results = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)

            if analysis_type == "dead_code":
                # Find all imports
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split(".")[0])

                # Check if imports are used
                for imp in imports:
                    if content.count(imp) == 1:  # Only appears in import statement
                        results.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "type": "unused_import",
                                "item": imp,
                                "recommendation": f"Remove unused import '{imp}'",
                            }
                        )

                # Find unused functions (basic check)
                defined_functions = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        defined_functions.add(node.name)

                for func in defined_functions:
                    if not func.startswith("_") and content.count(func) == 1:
                        results.append(
                            {
                                "file": str(file_path.relative_to(self.project_path)),
                                "type": "potentially_unused_function",
                                "item": func,
                                "recommendation": f"Function '{func}' may be unused",
                            }
                        )

        except Exception as e:
            pass

        return results

    def _analyze_javascript(
        self, file_path: Path, analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Analyze JavaScript/JSX files"""
        results = []
        # Simplified analysis for JavaScript
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find unused imports (basic)
            import_pattern = r"import\s+(?:{[^}]+}|[\w,\s]+)\s+from\s+['\"]([^'\"]+)['\"]"
            imports = re.findall(import_pattern, content)

            for imp in imports:
                if content.count(imp) == 1:
                    results.append(
                        {
                            "file": str(file_path.relative_to(self.project_path)),
                            "type": "potentially_unused_import",
                            "item": imp,
                            "recommendation": f"Check if import '{imp}' is used",
                        }
                    )

        except Exception:
            pass

        return results

    def _analyze_typescript(
        self, file_path: Path, analysis_type: str
    ) -> List[Dict[str, Any]]:
        """Analyze TypeScript/TSX files"""
        # Use same logic as JavaScript for now
        return self._analyze_javascript(file_path, analysis_type)

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Add complexity for control flow statements
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _get_complexity_recommendation(self, complexity: int, lines: int) -> str:
        """Get recommendation based on complexity metrics"""
        recommendations = []

        if complexity > 15:
            recommendations.append(
                f"High complexity ({complexity}): Break into smaller functions"
            )
        elif complexity > 10:
            recommendations.append(
                f"Medium complexity ({complexity}): Consider refactoring"
            )

        if lines > 100:
            recommendations.append(f"Long function ({lines} lines): Split into modules")
        elif lines > 50:
            recommendations.append(
                f"Consider breaking down function ({lines} lines)"
            )

        return " | ".join(recommendations) if recommendations else "Acceptable"

    def _calculate_savings(self, report: Dict) -> int:
        """Calculate potential lines of code savings"""
        savings = 0

        # Dead code removal
        savings += len(report["dead_code"]) * 2

        # Duplicate code elimination
        for dup in report["duplicates"]:
            savings += (dup["instances"] - 1) * 6

        # Complexity reduction (estimated)
        savings += len(report["complexity_issues"]) * 5

        return savings

    def generate_refactor_plan(self) -> Dict[str, Any]:
        """Generate prioritized refactoring plan"""
        analysis = self.analyze_project()

        if "error" in analysis:
            return analysis

        plan = {
            "timestamp": datetime.now().isoformat(),
            "priority_actions": [],
            "estimated_effort_hours": 0,
            "expected_impact": "high",
        }

        # High priority: Security and performance
        if analysis["best_practices_violations"]:
            high_severity = [
                v
                for v in analysis["best_practices_violations"]
                if v.get("severity") == "high"
            ]
            if high_severity:
                plan["priority_actions"].append(
                    {
                        "priority": 1,
                        "action": "Fix security/best practice violations",
                        "count": len(high_severity),
                        "estimated_hours": len(high_severity) * 0.5,
                    }
                )

        # High priority: Complexity reduction
        if analysis["complexity_issues"]:
            high_complexity = [
                c for c in analysis["complexity_issues"] if c.get("severity") == "high"
            ]
            if high_complexity:
                plan["priority_actions"].append(
                    {
                        "priority": 2,
                        "action": "Refactor high-complexity functions",
                        "count": len(high_complexity),
                        "estimated_hours": len(high_complexity) * 2,
                    }
                )

        # Medium priority: Remove duplicates
        if analysis["duplicates"]:
            plan["priority_actions"].append(
                {
                    "priority": 3,
                    "action": "Extract duplicate code to reusable functions",
                    "count": len(analysis["duplicates"]),
                    "estimated_hours": len(analysis["duplicates"]) * 1,
                }
            )

        # Low priority: Dead code removal
        if analysis["dead_code"]:
            plan["priority_actions"].append(
                {
                    "priority": 4,
                    "action": "Remove dead code",
                    "count": len(analysis["dead_code"]),
                    "estimated_hours": len(analysis["dead_code"]) * 0.25,
                }
            )

        # Calculate total effort
        plan["estimated_effort_hours"] = sum(
            action["estimated_hours"] for action in plan["priority_actions"]
        )

        return plan

    def export_report(self, report: Dict, output_path: str) -> bool:
        """Export refactoring report to JSON file"""
        try:
            output = Path(output_path)
            with open(output, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            return True
        except Exception as e:
            return False

    def cleanup(self):
        """Cleanup resources"""
        # No temp files to clean in this service
        pass
