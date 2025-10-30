"""
YAGO v8.2 - Documentation Compliance Service
Compares code implementation against technical documentation to ensure compliance
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict
import hashlib


class DocComplianceService:
    """Enterprise-grade documentation compliance analyzer"""

    def __init__(self, project_path: str, docs_path: Optional[str] = None):
        self.project_path = Path(project_path)
        self.docs_path = Path(docs_path) if docs_path else self.project_path / "docs"
        self.requirements = []
        self.implementations = []

    def analyze_compliance(self) -> Dict[str, Any]:
        """Comprehensive documentation compliance analysis"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "docs_path": str(self.docs_path),
            "summary": {
                "total_requirements": 0,
                "implemented_requirements": 0,
                "missing_implementations": 0,
                "undocumented_features": 0,
                "compliance_score": 0.0,
            },
            "requirements_analysis": [],
            "missing_implementations": [],
            "undocumented_features": [],
            "api_compliance": [],
            "configuration_compliance": [],
            "recommendations": [],
        }

        try:
            # Parse documentation
            docs_found = self._parse_documentation()
            if not docs_found:
                report["warning"] = "No documentation found. Analyzing code only."
                report["requirements_analysis"] = [
                    {"type": "warning", "message": "No documentation files found"}
                ]
            else:
                # Extract requirements from documentation
                report["requirements_analysis"] = self._extract_requirements()
                report["summary"]["total_requirements"] = len(
                    report["requirements_analysis"]
                )

            # Analyze code implementation
            code_analysis = self._analyze_implementation()

            # Compare documentation vs implementation
            compliance = self._compare_docs_to_code(
                report["requirements_analysis"], code_analysis
            )

            report["missing_implementations"] = compliance["missing"]
            report["undocumented_features"] = compliance["undocumented"]
            report["summary"]["missing_implementations"] = len(compliance["missing"])
            report["summary"]["undocumented_features"] = len(
                compliance["undocumented"]
            )

            # API compliance check
            report["api_compliance"] = self._check_api_compliance()

            # Configuration compliance
            report["configuration_compliance"] = self._check_configuration_compliance()

            # Calculate compliance score
            if report["summary"]["total_requirements"] > 0:
                implemented = (
                    report["summary"]["total_requirements"]
                    - report["summary"]["missing_implementations"]
                )
                report["summary"]["implemented_requirements"] = implemented
                report["summary"]["compliance_score"] = round(
                    (implemented / report["summary"]["total_requirements"]) * 100, 2
                )
            else:
                report["summary"]["compliance_score"] = 100.0

            # Generate recommendations
            report["recommendations"] = self._generate_compliance_recommendations(
                report
            )

            report["status"] = "completed"

        except Exception as e:
            report["status"] = "error"
            report["error"] = str(e)

        return report

    def _parse_documentation(self) -> bool:
        """Parse all documentation files"""
        doc_files = []

        # Look for common documentation files
        patterns = [
            "**/*.md",
            "**/*.rst",
            "**/*.txt",
            "**/README*",
            "**/SPEC*",
            "**/requirements*.md",
        ]

        for pattern in patterns:
            doc_files.extend(self.project_path.glob(pattern))
            if self.docs_path.exists():
                doc_files.extend(self.docs_path.glob(pattern))

        # Remove duplicates
        doc_files = list(set(doc_files))

        # Also check root directory
        for filename in ["README.md", "REQUIREMENTS.md", "SPECIFICATION.md", "API.md"]:
            filepath = self.project_path / filename
            if filepath.exists() and filepath not in doc_files:
                doc_files.append(filepath)

        return len(doc_files) > 0

    def _extract_requirements(self) -> List[Dict[str, Any]]:
        """Extract requirements from documentation"""
        requirements = []

        doc_patterns = [
            "**/*.md",
            "**/*.rst",
            "**/SPEC*.md",
            "**/requirements*.md",
            "**/API*.md",
        ]

        doc_files = []
        for pattern in doc_patterns:
            doc_files.extend(self.project_path.glob(pattern))
            if self.docs_path.exists():
                doc_files.extend(self.docs_path.glob(pattern))

        for doc_file in doc_files:
            try:
                with open(doc_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Extract different types of requirements
                requirements.extend(self._extract_functional_requirements(content, doc_file))
                requirements.extend(self._extract_api_requirements(content, doc_file))
                requirements.extend(
                    self._extract_configuration_requirements(content, doc_file)
                )
                requirements.extend(self._extract_feature_requirements(content, doc_file))

            except Exception:
                continue

        return requirements

    def _extract_functional_requirements(
        self, content: str, source_file: Path
    ) -> List[Dict[str, Any]]:
        """Extract functional requirements from documentation"""
        requirements = []

        # Pattern: "The system must/should/shall..."
        patterns = [
            r"(?:system|application|software)\s+(?:must|should|shall)\s+([^.]+)",
            r"(?:must|should|shall)\s+(?:be able to|support|implement|provide)\s+([^.]+)",
            r"requirement[:\s]+([^.\n]+)",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                req_text = match.group(1).strip()
                if len(req_text) > 10:  # Filter out too short matches
                    requirements.append(
                        {
                            "type": "functional",
                            "source": source_file.name,
                            "requirement": req_text,
                            "priority": self._determine_priority(match.group(0)),
                            "keywords": self._extract_keywords(req_text),
                        }
                    )

        return requirements

    def _extract_api_requirements(
        self, content: str, source_file: Path
    ) -> List[Dict[str, Any]]:
        """Extract API requirements from documentation"""
        requirements = []

        # Pattern: API endpoint definitions
        # Example: GET /api/users, POST /api/login
        api_pattern = r"(?:GET|POST|PUT|DELETE|PATCH)\s+([/\w\-{}:]+)"
        matches = re.finditer(api_pattern, content, re.IGNORECASE)

        for match in matches:
            endpoint = match.group(1).strip()
            method = match.group(0).split()[0].upper()

            requirements.append(
                {
                    "type": "api_endpoint",
                    "source": source_file.name,
                    "method": method,
                    "endpoint": endpoint,
                    "requirement": f"{method} endpoint for {endpoint}",
                    "keywords": [endpoint.split("/")[-1], method.lower()],
                }
            )

        # Pattern: Function/method signatures in docs
        # Example: `getUserById(id: string): User`
        func_pattern = r"`?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?`?"
        matches = re.finditer(func_pattern, content)

        for match in matches:
            func_name = match.group(1)
            if (
                not func_name.startswith("_")
                and func_name[0].islower()
                and len(func_name) > 3
            ):
                requirements.append(
                    {
                        "type": "function",
                        "source": source_file.name,
                        "function": func_name,
                        "requirement": f"Function {func_name} should be implemented",
                        "keywords": [func_name],
                    }
                )

        return requirements

    def _extract_configuration_requirements(
        self, content: str, source_file: Path
    ) -> List[Dict[str, Any]]:
        """Extract configuration requirements"""
        requirements = []

        # Pattern: Environment variables
        # Example: DATABASE_URL, API_KEY
        env_pattern = r"(?:env|environment|config|configuration)[:\s]+`?([A-Z_][A-Z0-9_]*)`?"
        matches = re.finditer(env_pattern, content, re.IGNORECASE)

        for match in matches:
            var_name = match.group(1)
            requirements.append(
                {
                    "type": "configuration",
                    "source": source_file.name,
                    "config_key": var_name,
                    "requirement": f"Configuration variable {var_name} required",
                    "keywords": [var_name.lower()],
                }
            )

        return requirements

    def _extract_feature_requirements(
        self, content: str, source_file: Path
    ) -> List[Dict[str, Any]]:
        """Extract feature requirements from headers and lists"""
        requirements = []

        # Pattern: Features section with bullet points
        # Example: - User authentication
        lines = content.split("\n")
        in_features_section = False

        for i, line in enumerate(lines):
            # Detect features section
            if re.search(r"#+\s*(?:features?|capabilities?)", line, re.IGNORECASE):
                in_features_section = True
                continue

            # Exit features section on next header
            if in_features_section and line.startswith("#"):
                in_features_section = False
                continue

            # Extract bullet points in features section
            if in_features_section and re.match(r"^\s*[-*]\s+(.+)", line):
                feature = re.match(r"^\s*[-*]\s+(.+)", line).group(1).strip()
                if len(feature) > 5:
                    requirements.append(
                        {
                            "type": "feature",
                            "source": source_file.name,
                            "feature": feature,
                            "requirement": feature,
                            "keywords": self._extract_keywords(feature),
                        }
                    )

        return requirements

    def _analyze_implementation(self) -> Dict[str, Any]:
        """Analyze code implementation"""
        implementation = {
            "functions": [],
            "classes": [],
            "api_endpoints": [],
            "configurations": [],
            "features": [],
        }

        # Analyze Python files
        for py_file in self.project_path.rglob("*.py"):
            if ".git" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)

                # Extract functions and classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        implementation["functions"].append(
                            {
                                "name": node.name,
                                "file": str(py_file.relative_to(self.project_path)),
                                "line": node.lineno,
                                "docstring": ast.get_docstring(node),
                            }
                        )

                    elif isinstance(node, ast.ClassDef):
                        implementation["classes"].append(
                            {
                                "name": node.name,
                                "file": str(py_file.relative_to(self.project_path)),
                                "line": node.lineno,
                                "docstring": ast.get_docstring(node),
                            }
                        )

                # Extract API endpoints (Flask/FastAPI patterns)
                api_patterns = [
                    r"@app\.route\(['\"]([^'\"]+)['\"].*methods=\[([^\]]+)\]",
                    r"@router\.(get|post|put|delete|patch)\(['\"]([^'\"]+)",
                ]

                for pattern in api_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        if "route" in pattern:
                            endpoint = match.group(1)
                            methods = match.group(2).replace("'", "").replace('"', "")
                        else:
                            endpoint = match.group(2)
                            methods = match.group(1).upper()

                        implementation["api_endpoints"].append(
                            {
                                "endpoint": endpoint,
                                "methods": methods,
                                "file": str(py_file.relative_to(self.project_path)),
                            }
                        )

            except Exception:
                continue

        # Analyze JavaScript/TypeScript files
        for js_file in self.project_path.rglob("*.[jt]s*"):
            if ".git" in str(js_file) or "node_modules" in str(js_file):
                continue

            try:
                with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Extract Express/Fastify routes
                route_patterns = [
                    r"(?:app|router)\.(get|post|put|delete|patch)\(['\"]([^'\"]+)",
                    r"@(?:Get|Post|Put|Delete|Patch)\(['\"]([^'\"]+)",
                ]

                for pattern in route_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        if "app" in pattern or "router" in pattern:
                            method = match.group(1).upper()
                            endpoint = match.group(2)
                        else:
                            method = match.group(0).split("(")[0].replace("@", "")
                            endpoint = match.group(1)

                        implementation["api_endpoints"].append(
                            {
                                "endpoint": endpoint,
                                "methods": method,
                                "file": str(js_file.relative_to(self.project_path)),
                            }
                        )

            except Exception:
                continue

        # Check for configuration files
        config_files = [
            ".env",
            ".env.example",
            "config.py",
            "config.json",
            "settings.py",
        ]
        for config_file in config_files:
            filepath = self.project_path / config_file
            if filepath.exists():
                implementation["configurations"].append(
                    {"file": config_file, "exists": True}
                )

        return implementation

    def _compare_docs_to_code(
        self, requirements: List[Dict], implementation: Dict
    ) -> Dict[str, List]:
        """Compare documentation requirements against implementation"""
        missing = []
        undocumented = []

        # Check if documented APIs are implemented
        documented_endpoints = {
            req["endpoint"]: req
            for req in requirements
            if req.get("type") == "api_endpoint"
        }
        implemented_endpoints = {
            api["endpoint"]: api for api in implementation["api_endpoints"]
        }

        for endpoint, req in documented_endpoints.items():
            if endpoint not in implemented_endpoints:
                missing.append(
                    {
                        "type": "missing_api",
                        "endpoint": endpoint,
                        "method": req.get("method", "N/A"),
                        "source": req.get("source"),
                        "severity": "high",
                    }
                )

        # Check if documented functions are implemented
        documented_functions = {
            req["function"]: req
            for req in requirements
            if req.get("type") == "function"
        }
        implemented_functions = {func["name"]: func for func in implementation["functions"]}

        for func_name, req in documented_functions.items():
            if func_name not in implemented_functions:
                missing.append(
                    {
                        "type": "missing_function",
                        "function": func_name,
                        "source": req.get("source"),
                        "severity": "medium",
                    }
                )

        # Find undocumented implementations
        for endpoint, impl in implemented_endpoints.items():
            if endpoint not in documented_endpoints:
                undocumented.append(
                    {
                        "type": "undocumented_api",
                        "endpoint": endpoint,
                        "methods": impl.get("methods"),
                        "file": impl.get("file"),
                        "recommendation": f"Add {endpoint} to API documentation",
                    }
                )

        # Find undocumented public functions
        for func_name, impl in implemented_functions.items():
            if (
                not func_name.startswith("_")
                and func_name not in documented_functions
                and not impl.get("docstring")
            ):
                undocumented.append(
                    {
                        "type": "undocumented_function",
                        "function": func_name,
                        "file": impl.get("file"),
                        "line": impl.get("line"),
                        "recommendation": f"Add docstring and/or documentation for {func_name}",
                    }
                )

        return {"missing": missing, "undocumented": undocumented}

    def _check_api_compliance(self) -> List[Dict[str, Any]]:
        """Check API documentation compliance"""
        compliance_issues = []

        # Check for OpenAPI/Swagger specification
        openapi_files = list(self.project_path.glob("**/openapi.{yaml,yml,json}"))
        openapi_files.extend(self.project_path.glob("**/swagger.{yaml,yml,json}"))

        if not openapi_files:
            compliance_issues.append(
                {
                    "type": "missing_api_spec",
                    "severity": "medium",
                    "message": "No OpenAPI/Swagger specification found",
                    "recommendation": "Create openapi.yaml for API documentation",
                }
            )

        # Check for API versioning
        api_files = list(self.project_path.rglob("**/api/**/*.py"))
        api_files.extend(self.project_path.rglob("**/routes/**/*.py"))

        has_versioning = False
        for api_file in api_files:
            try:
                with open(api_file, "r") as f:
                    content = f.read()
                    if re.search(r"/v\d+/", content):
                        has_versioning = True
                        break
            except Exception:
                continue

        if api_files and not has_versioning:
            compliance_issues.append(
                {
                    "type": "missing_api_versioning",
                    "severity": "low",
                    "message": "API versioning not detected",
                    "recommendation": "Consider implementing API versioning (e.g., /api/v1/)",
                }
            )

        return compliance_issues

    def _check_configuration_compliance(self) -> List[Dict[str, Any]]:
        """Check configuration documentation compliance"""
        compliance_issues = []

        # Check if .env.example exists when .env is used
        env_file = self.project_path / ".env"
        env_example = self.project_path / ".env.example"

        if env_file.exists() and not env_example.exists():
            compliance_issues.append(
                {
                    "type": "missing_env_example",
                    "severity": "medium",
                    "message": ".env.example file missing",
                    "recommendation": "Create .env.example with all required variables",
                }
            )

        # Check for configuration documentation
        config_docs = list(self.project_path.glob("**/CONFIGURATION.md"))
        config_docs.extend(self.project_path.glob("**/CONFIG.md"))

        if not config_docs and env_file.exists():
            compliance_issues.append(
                {
                    "type": "missing_config_docs",
                    "severity": "low",
                    "message": "No configuration documentation found",
                    "recommendation": "Create CONFIGURATION.md to document environment variables",
                }
            )

        return compliance_issues

    def _generate_compliance_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on compliance analysis"""
        recommendations = []

        compliance_score = report["summary"]["compliance_score"]

        if compliance_score < 50:
            recommendations.append(
                "CRITICAL: Low compliance score. Prioritize implementing missing features."
            )
        elif compliance_score < 75:
            recommendations.append(
                "MODERATE: Several requirements are missing. Review and implement them."
            )

        if report["summary"]["missing_implementations"] > 0:
            recommendations.append(
                f"Implement {report['summary']['missing_implementations']} missing documented features"
            )

        if report["summary"]["undocumented_features"] > 5:
            recommendations.append(
                f"Document {report['summary']['undocumented_features']} implemented but undocumented features"
            )

        if report["api_compliance"]:
            high_severity = [c for c in report["api_compliance"] if c.get("severity") == "high"]
            if high_severity:
                recommendations.append(
                    f"Address {len(high_severity)} high-severity API compliance issues"
                )

        if not recommendations:
            recommendations.append(
                "Good compliance! Keep documentation updated as code evolves."
            )

        return recommendations

    def _determine_priority(self, requirement_text: str) -> str:
        """Determine priority based on requirement language"""
        if "must" in requirement_text.lower() or "shall" in requirement_text.lower():
            return "high"
        elif "should" in requirement_text.lower():
            return "medium"
        return "low"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common words
        common_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "be",
            "are",
        }

        words = re.findall(r"\b\w+\b", text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in common_words]

        return keywords[:5]  # Return top 5 keywords

    def generate_compliance_report(self) -> str:
        """Generate human-readable compliance report"""
        analysis = self.analyze_compliance()

        report_lines = [
            "=" * 80,
            "DOCUMENTATION COMPLIANCE REPORT",
            "=" * 80,
            f"\nGenerated: {analysis['timestamp']}",
            f"Project: {analysis['project_path']}\n",
            "\nSUMMARY",
            "-" * 80,
            f"Total Requirements: {analysis['summary']['total_requirements']}",
            f"Implemented: {analysis['summary']['implemented_requirements']}",
            f"Missing: {analysis['summary']['missing_implementations']}",
            f"Undocumented Features: {analysis['summary']['undocumented_features']}",
            f"Compliance Score: {analysis['summary']['compliance_score']}%\n",
        ]

        if analysis["missing_implementations"]:
            report_lines.extend(
                [
                    "\nMISSING IMPLEMENTATIONS",
                    "-" * 80,
                ]
            )
            for item in analysis["missing_implementations"][:10]:
                report_lines.append(
                    f"  [{item['severity'].upper()}] {item['type']}: {item.get('endpoint', item.get('function', 'N/A'))}"
                )

        if analysis["undocumented_features"]:
            report_lines.extend(
                [
                    "\n\nUNDOCUMENTED FEATURES",
                    "-" * 80,
                ]
            )
            for item in analysis["undocumented_features"][:10]:
                report_lines.append(f"  {item['type']}: {item.get('endpoint', item.get('function', 'N/A'))}")

        if analysis["recommendations"]:
            report_lines.extend(
                [
                    "\n\nRECOMMENDATIONS",
                    "-" * 80,
                ]
            )
            for i, rec in enumerate(analysis["recommendations"], 1):
                report_lines.append(f"  {i}. {rec}")

        report_lines.append("\n" + "=" * 80)

        return "\n".join(report_lines)

    def export_report(self, report: Dict, output_path: str) -> bool:
        """Export compliance report to JSON file"""
        try:
            output = Path(output_path)
            with open(output, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            return True
        except Exception:
            return False

    def cleanup(self):
        """Cleanup resources"""
        # No temp files to clean in this service
        pass
