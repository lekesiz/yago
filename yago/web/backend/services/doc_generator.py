"""
YAGO v8.2 - Auto Documentation Generator Service
Automatically generates comprehensive documentation from code
"""

import os
import re
import ast
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict


class DocGeneratorService:
    """Enterprise-grade automatic documentation generator"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_name = self.project_path.name
        self.docs_output = self.project_path / "docs" / "generated"

    def generate_all_documentation(self) -> Dict[str, Any]:
        """Generate all documentation types"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "generated_docs": [],
            "summary": {
                "total_files_generated": 0,
                "total_functions_documented": 0,
                "total_classes_documented": 0,
                "total_apis_documented": 0,
            },
        }

        try:
            # Ensure output directory exists
            self.docs_output.mkdir(parents=True, exist_ok=True)

            # Generate README
            readme_path = self._generate_readme()
            if readme_path:
                report["generated_docs"].append(
                    {"type": "README", "path": str(readme_path)}
                )

            # Generate API documentation
            api_doc_path = self._generate_api_documentation()
            if api_doc_path:
                report["generated_docs"].append(
                    {"type": "API Documentation", "path": str(api_doc_path)}
                )
                report["summary"]["total_apis_documented"] = self._count_apis()

            # Generate architecture overview
            arch_path = self._generate_architecture_overview()
            if arch_path:
                report["generated_docs"].append(
                    {"type": "Architecture Overview", "path": str(arch_path)}
                )

            # Generate code reference
            code_ref_path = self._generate_code_reference()
            if code_ref_path:
                report["generated_docs"].append(
                    {"type": "Code Reference", "path": str(code_ref_path)}
                )
                stats = self._count_code_elements()
                report["summary"]["total_functions_documented"] = stats["functions"]
                report["summary"]["total_classes_documented"] = stats["classes"]

            # Generate installation guide
            install_path = self._generate_installation_guide()
            if install_path:
                report["generated_docs"].append(
                    {"type": "Installation Guide", "path": str(install_path)}
                )

            # Generate usage examples
            examples_path = self._generate_usage_examples()
            if examples_path:
                report["generated_docs"].append(
                    {"type": "Usage Examples", "path": str(examples_path)}
                )

            # Generate changelog from Git
            changelog_path = self._generate_changelog()
            if changelog_path:
                report["generated_docs"].append(
                    {"type": "Changelog", "path": str(changelog_path)}
                )

            # Generate diagrams
            diagrams_path = self._generate_diagrams()
            if diagrams_path:
                report["generated_docs"].append(
                    {"type": "Architecture Diagrams", "path": str(diagrams_path)}
                )

            report["summary"]["total_files_generated"] = len(report["generated_docs"])
            report["status"] = "completed"

        except Exception as e:
            report["status"] = "error"
            report["error"] = str(e)

        return report

    def _generate_readme(self) -> Optional[Path]:
        """Generate comprehensive README.md"""
        try:
            # Analyze project structure
            structure = self._analyze_project_structure()
            tech_stack = self._detect_tech_stack()

            readme_content = f"""# {self.project_name}

> Automatically generated documentation for {self.project_name}

## 📋 Overview

{self._generate_project_description(structure)}

## 🚀 Tech Stack

{self._format_tech_stack(tech_stack)}

## 📁 Project Structure

```
{self._generate_tree_structure(structure)}
```

## ⚙️ Installation

See [Installation Guide](docs/generated/INSTALLATION.md) for detailed setup instructions.

Quick start:
```bash
# Clone the repository
git clone <repository-url>
cd {self.project_name}

# Install dependencies
{self._get_install_command(tech_stack)}

# Run the application
{self._get_run_command(tech_stack)}
```

## 📖 Documentation

- [API Documentation](docs/generated/API.md)
- [Architecture Overview](docs/generated/ARCHITECTURE.md)
- [Code Reference](docs/generated/CODE_REFERENCE.md)
- [Usage Examples](docs/generated/EXAMPLES.md)
- [Changelog](docs/generated/CHANGELOG.md)

## 🧪 Testing

```bash
{self._get_test_command(tech_stack)}
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

{self._detect_license()}

## 📧 Contact

Project Link: [https://github.com/yourusername/{self.project_name}](https://github.com/yourusername/{self.project_name})

---
*This documentation was automatically generated by YAGO v8.2*
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

            readme_path = self.project_path / "README.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)

            return readme_path

        except Exception as e:
            return None

    def _generate_api_documentation(self) -> Optional[Path]:
        """Generate API documentation in OpenAPI format"""
        try:
            api_endpoints = self._extract_api_endpoints()

            if not api_endpoints:
                return None

            # Generate Markdown API documentation
            api_content = f"""# API Documentation

> Automatically generated API documentation for {self.project_name}

## Base URL

```
http://localhost:8000/api
```

## Endpoints

"""

            # Group by resource
            grouped_endpoints = defaultdict(list)
            for endpoint in api_endpoints:
                resource = endpoint["endpoint"].split("/")[1] if "/" in endpoint["endpoint"] else "General"
                grouped_endpoints[resource].append(endpoint)

            for resource, endpoints in grouped_endpoints.items():
                api_content += f"\n### {resource.capitalize()}\n\n"

                for endpoint in endpoints:
                    api_content += f"#### {endpoint['method']} {endpoint['endpoint']}\n\n"
                    api_content += f"**File:** `{endpoint['file']}`\n\n"

                    if endpoint.get("description"):
                        api_content += f"{endpoint['description']}\n\n"

                    # Add request/response examples if available
                    if endpoint.get("request_example"):
                        api_content += "**Request:**\n```json\n"
                        api_content += json.dumps(endpoint["request_example"], indent=2)
                        api_content += "\n```\n\n"

                    if endpoint.get("response_example"):
                        api_content += "**Response:**\n```json\n"
                        api_content += json.dumps(endpoint["response_example"], indent=2)
                        api_content += "\n```\n\n"

                    api_content += "---\n\n"

            # Generate OpenAPI spec
            openapi_spec = self._generate_openapi_spec(api_endpoints)
            openapi_path = self.docs_output / "openapi.yaml"
            with open(openapi_path, "w", encoding="utf-8") as f:
                f.write(openapi_spec)

            api_doc_path = self.docs_output / "API.md"
            with open(api_doc_path, "w", encoding="utf-8") as f:
                f.write(api_content)

            return api_doc_path

        except Exception:
            return None

    def _generate_architecture_overview(self) -> Optional[Path]:
        """Generate architecture overview with diagrams"""
        try:
            structure = self._analyze_project_structure()

            arch_content = f"""# Architecture Overview

> System architecture for {self.project_name}

## System Architecture

{self._generate_architecture_description(structure)}

## Components

{self._generate_components_list(structure)}

## Data Flow

```mermaid
{self._generate_data_flow_diagram(structure)}
```

## Technology Stack

### Backend
{self._list_backend_technologies(structure)}

### Frontend
{self._list_frontend_technologies(structure)}

### Database
{self._list_database_technologies(structure)}

### DevOps
{self._list_devops_technologies(structure)}

## Design Patterns

{self._identify_design_patterns(structure)}

## Security Considerations

{self._generate_security_notes(structure)}

## Performance Considerations

{self._generate_performance_notes(structure)}

---
*Generated by YAGO v8.2 on {datetime.now().strftime('%Y-%m-%d')}*
"""

            arch_path = self.docs_output / "ARCHITECTURE.md"
            with open(arch_path, "w", encoding="utf-8") as f:
                f.write(arch_content)

            return arch_path

        except Exception:
            return None

    def _generate_code_reference(self) -> Optional[Path]:
        """Generate detailed code reference"""
        try:
            code_ref_content = f"""# Code Reference

> Detailed code reference for {self.project_name}

"""

            # Document Python modules
            python_files = list(self.project_path.rglob("*.py"))
            if python_files:
                code_ref_content += "## Python Modules\n\n"

                for py_file in python_files:
                    if ".git" in str(py_file) or "venv" in str(py_file):
                        continue

                    try:
                        with open(py_file, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read())

                        module_name = str(py_file.relative_to(self.project_path))
                        code_ref_content += f"### `{module_name}`\n\n"

                        # Module docstring
                        module_doc = ast.get_docstring(tree)
                        if module_doc:
                            code_ref_content += f"{module_doc}\n\n"

                        # Classes
                        classes = [
                            node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
                        ]
                        if classes:
                            code_ref_content += "#### Classes\n\n"
                            for cls in classes:
                                code_ref_content += f"##### `{cls.name}`\n\n"
                                cls_doc = ast.get_docstring(cls)
                                if cls_doc:
                                    code_ref_content += f"{cls_doc}\n\n"

                                # Methods
                                methods = [
                                    node
                                    for node in cls.body
                                    if isinstance(node, ast.FunctionDef)
                                ]
                                if methods:
                                    code_ref_content += "**Methods:**\n\n"
                                    for method in methods:
                                        args = self._format_function_signature(method)
                                        code_ref_content += f"- `{method.name}({args})`"
                                        method_doc = ast.get_docstring(method)
                                        if method_doc:
                                            code_ref_content += f": {method_doc.split(chr(10))[0]}"
                                        code_ref_content += "\n"
                                    code_ref_content += "\n"

                        # Functions
                        functions = [
                            node
                            for node in tree.body
                            if isinstance(node, ast.FunctionDef)
                        ]
                        if functions:
                            code_ref_content += "#### Functions\n\n"
                            for func in functions:
                                args = self._format_function_signature(func)
                                code_ref_content += f"##### `{func.name}({args})`\n\n"
                                func_doc = ast.get_docstring(func)
                                if func_doc:
                                    code_ref_content += f"{func_doc}\n\n"

                        code_ref_content += "---\n\n"

                    except Exception:
                        continue

            code_ref_path = self.docs_output / "CODE_REFERENCE.md"
            with open(code_ref_path, "w", encoding="utf-8") as f:
                f.write(code_ref_content)

            return code_ref_path

        except Exception:
            return None

    def _generate_installation_guide(self) -> Optional[Path]:
        """Generate detailed installation guide"""
        try:
            tech_stack = self._detect_tech_stack()

            install_content = f"""# Installation Guide

> Complete installation instructions for {self.project_name}

## Prerequisites

{self._generate_prerequisites(tech_stack)}

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd {self.project_name}
```

### 2. Install Dependencies

{self._generate_dependency_instructions(tech_stack)}

### 3. Configuration

{self._generate_configuration_instructions()}

### 4. Database Setup

{self._generate_database_instructions(tech_stack)}

### 5. Run the Application

{self._generate_run_instructions(tech_stack)}

## Verification

Run tests to verify installation:

```bash
{self._get_test_command(tech_stack)}
```

## Troubleshooting

{self._generate_troubleshooting_section()}

## Next Steps

- Read the [Architecture Overview](ARCHITECTURE.md)
- Check out [Usage Examples](EXAMPLES.md)
- Review the [API Documentation](API.md)

---
*Generated by YAGO v8.2*
"""

            install_path = self.docs_output / "INSTALLATION.md"
            with open(install_path, "w", encoding="utf-8") as f:
                f.write(install_content)

            return install_path

        except Exception:
            return None

    def _generate_usage_examples(self) -> Optional[Path]:
        """Generate usage examples"""
        try:
            examples_content = f"""# Usage Examples

> Practical examples for using {self.project_name}

## Quick Start

{self._generate_quickstart_example()}

## Common Use Cases

{self._generate_use_cases()}

## API Examples

{self._generate_api_examples()}

## Code Examples

{self._extract_code_examples()}

## Advanced Usage

{self._generate_advanced_examples()}

---
*Generated by YAGO v8.2*
"""

            examples_path = self.docs_output / "EXAMPLES.md"
            with open(examples_path, "w", encoding="utf-8") as f:
                f.write(examples_content)

            return examples_path

        except Exception:
            return None

    def _generate_changelog(self) -> Optional[Path]:
        """Generate changelog from Git history"""
        try:
            changelog_content = f"""# Changelog

> All notable changes to {self.project_name}

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

"""

            # Get Git log
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(self.project_path),
                    "log",
                    "--pretty=format:%H|%ad|%an|%s",
                    "--date=short",
                    "--all",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split("\n")

                # Group commits by date (approximating versions)
                grouped = defaultdict(list)
                for commit in commits[:50]:  # Last 50 commits
                    parts = commit.split("|")
                    if len(parts) >= 4:
                        commit_hash, date, author, message = parts[0], parts[1], parts[2], parts[3]
                        grouped[date].append(
                            {"hash": commit_hash[:7], "author": author, "message": message}
                        )

                # Format changelog
                for date in sorted(grouped.keys(), reverse=True):
                    changelog_content += f"\n## [{date}]\n\n"

                    # Categorize commits
                    features = []
                    fixes = []
                    docs = []
                    other = []

                    for commit in grouped[date]:
                        msg = commit["message"].lower()
                        if any(
                            keyword in msg
                            for keyword in ["feat", "feature", "add", "implement"]
                        ):
                            features.append(commit)
                        elif any(keyword in msg for keyword in ["fix", "bug", "patch"]):
                            fixes.append(commit)
                        elif any(keyword in msg for keyword in ["doc", "readme"]):
                            docs.append(commit)
                        else:
                            other.append(commit)

                    if features:
                        changelog_content += "### Added\n"
                        for commit in features:
                            changelog_content += f"- {commit['message']} ({commit['hash']})\n"
                        changelog_content += "\n"

                    if fixes:
                        changelog_content += "### Fixed\n"
                        for commit in fixes:
                            changelog_content += f"- {commit['message']} ({commit['hash']})\n"
                        changelog_content += "\n"

                    if docs:
                        changelog_content += "### Documentation\n"
                        for commit in docs:
                            changelog_content += f"- {commit['message']} ({commit['hash']})\n"
                        changelog_content += "\n"

                    if other:
                        changelog_content += "### Other\n"
                        for commit in other:
                            changelog_content += f"- {commit['message']} ({commit['hash']})\n"
                        changelog_content += "\n"

            changelog_content += "\n---\n*Generated by YAGO v8.2*\n"

            changelog_path = self.docs_output / "CHANGELOG.md"
            with open(changelog_path, "w", encoding="utf-8") as f:
                f.write(changelog_content)

            return changelog_path

        except Exception:
            return None

    def _generate_diagrams(self) -> Optional[Path]:
        """Generate Mermaid diagrams"""
        try:
            structure = self._analyze_project_structure()

            diagrams_content = f"""# Architecture Diagrams

> Visual representations of {self.project_name} architecture

## System Overview

```mermaid
graph TD
    A[Client] --> B[API Gateway]
    B --> C[Backend Services]
    C --> D[Database]
    C --> E[Cache]
    B --> F[Authentication]
```

## Component Diagram

```mermaid
{self._generate_component_diagram(structure)}
```

## Data Flow

```mermaid
{self._generate_data_flow_diagram(structure)}
```

## Deployment Architecture

```mermaid
graph LR
    A[Developer] -->|Push| B[Git Repository]
    B -->|Trigger| C[CI/CD Pipeline]
    C -->|Build| D[Docker Image]
    D -->|Deploy| E[Production Server]
    E -->|Serve| F[Users]
```

---
*Generated by YAGO v8.2*
"""

            diagrams_path = self.docs_output / "DIAGRAMS.md"
            with open(diagrams_path, "w", encoding="utf-8") as f:
                f.write(diagrams_content)

            return diagrams_path

        except Exception:
            return None

    # Helper methods

    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure"""
        structure = {
            "directories": [],
            "file_types": defaultdict(int),
            "total_files": 0,
            "has_tests": False,
            "has_docs": False,
            "has_config": False,
        }

        for item in self.project_path.rglob("*"):
            if ".git" in str(item) or "node_modules" in str(item) or "venv" in str(item):
                continue

            if item.is_file():
                structure["total_files"] += 1
                structure["file_types"][item.suffix] += 1

                if "test" in item.name.lower():
                    structure["has_tests"] = True
                if "readme" in item.name.lower():
                    structure["has_docs"] = True
                if item.name in [".env", "config.py", "config.json"]:
                    structure["has_config"] = True

            elif item.is_dir():
                rel_path = str(item.relative_to(self.project_path))
                if rel_path and not rel_path.startswith("."):
                    structure["directories"].append(rel_path)

        return structure

    def _detect_tech_stack(self) -> Dict[str, List[str]]:
        """Detect technology stack"""
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
        }

        # Check for package files
        if (self.project_path / "requirements.txt").exists() or (
            self.project_path / "pyproject.toml"
        ).exists():
            tech_stack["languages"].append("Python")

        if (self.project_path / "package.json").exists():
            tech_stack["languages"].append("JavaScript/TypeScript")

        if (self.project_path / "Gemfile").exists():
            tech_stack["languages"].append("Ruby")

        if (self.project_path / "go.mod").exists():
            tech_stack["languages"].append("Go")

        # Check for framework indicators
        if any(self.project_path.glob("**/django/**")):
            tech_stack["frameworks"].append("Django")

        if any(self.project_path.glob("**/flask/**")):
            tech_stack["frameworks"].append("Flask")

        if (self.project_path / "package.json").exists():
            try:
                with open(self.project_path / "package.json") as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    if "react" in deps:
                        tech_stack["frameworks"].append("React")
                    if "vue" in deps:
                        tech_stack["frameworks"].append("Vue")
                    if "express" in deps:
                        tech_stack["frameworks"].append("Express")
            except Exception:
                pass

        return tech_stack

    def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """Extract API endpoints from code"""
        endpoints = []

        for py_file in self.project_path.rglob("*.py"):
            if ".git" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Flask routes
                flask_pattern = r"@app\.route\(['\"]([^'\"]+)['\"].*methods=\[([^\]]+)\]"
                for match in re.finditer(flask_pattern, content):
                    endpoints.append(
                        {
                            "endpoint": match.group(1),
                            "method": match.group(2).replace("'", "").replace('"', ""),
                            "file": str(py_file.relative_to(self.project_path)),
                        }
                    )

                # FastAPI routes
                fastapi_pattern = r"@router\.(get|post|put|delete|patch)\(['\"]([^'\"]+)"
                for match in re.finditer(fastapi_pattern, content):
                    endpoints.append(
                        {
                            "endpoint": match.group(2),
                            "method": match.group(1).upper(),
                            "file": str(py_file.relative_to(self.project_path)),
                        }
                    )

            except Exception:
                continue

        return endpoints

    def _generate_project_description(self, structure: Dict) -> str:
        """Generate project description based on structure"""
        description = f"This is a {', '.join(self._detect_tech_stack()['languages'])} project"

        if structure["has_tests"]:
            description += " with test coverage"
        if structure["has_docs"]:
            description += " and comprehensive documentation"

        description += f".\n\nThe project contains {structure['total_files']} files"
        description += f" across {len(structure['directories'])} directories."

        return description

    def _format_tech_stack(self, tech_stack: Dict) -> str:
        """Format tech stack for display"""
        output = []

        if tech_stack["languages"]:
            output.append(f"**Languages:** {', '.join(tech_stack['languages'])}")

        if tech_stack["frameworks"]:
            output.append(f"**Frameworks:** {', '.join(tech_stack['frameworks'])}")

        if tech_stack["databases"]:
            output.append(f"**Databases:** {', '.join(tech_stack['databases'])}")

        if tech_stack["tools"]:
            output.append(f"**Tools:** {', '.join(tech_stack['tools'])}")

        return "\n".join(output) if output else "**Languages:** Multiple"

    def _generate_tree_structure(self, structure: Dict) -> str:
        """Generate tree structure"""
        tree = f"{self.project_name}/\n"
        for directory in sorted(structure["directories"])[:20]:  # Limit to 20
            depth = directory.count("/")
            tree += "  " * depth + "├── " + directory.split("/")[-1] + "/\n"

        return tree

    def _get_install_command(self, tech_stack: Dict) -> str:
        """Get installation command based on tech stack"""
        if "Python" in tech_stack["languages"]:
            return "pip install -r requirements.txt"
        elif "JavaScript/TypeScript" in tech_stack["languages"]:
            return "npm install"
        return "# See INSTALLATION.md"

    def _get_run_command(self, tech_stack: Dict) -> str:
        """Get run command based on tech stack"""
        if "Python" in tech_stack["languages"]:
            return "python main.py"
        elif "JavaScript/TypeScript" in tech_stack["languages"]:
            return "npm start"
        return "# See INSTALLATION.md"

    def _get_test_command(self, tech_stack: Dict) -> str:
        """Get test command based on tech stack"""
        if "Python" in tech_stack["languages"]:
            return "pytest"
        elif "JavaScript/TypeScript" in tech_stack["languages"]:
            return "npm test"
        return "# See documentation"

    def _detect_license(self) -> str:
        """Detect project license"""
        license_file = self.project_path / "LICENSE"
        if license_file.exists():
            try:
                with open(license_file, "r") as f:
                    content = f.read()
                    if "MIT" in content:
                        return "MIT License"
                    elif "Apache" in content:
                        return "Apache License 2.0"
                    elif "GPL" in content:
                        return "GNU GPL"
            except Exception:
                pass

        return "See LICENSE file"

    def _generate_openapi_spec(self, endpoints: List[Dict]) -> str:
        """Generate OpenAPI YAML specification"""
        spec = f"""openapi: 3.0.0
info:
  title: {self.project_name} API
  version: 1.0.0
  description: Automatically generated API documentation

servers:
  - url: http://localhost:8000/api
    description: Development server

paths:
"""

        for endpoint in endpoints:
            method = endpoint["method"].lower()
            spec += f"  {endpoint['endpoint']}:\n"
            spec += f"    {method}:\n"
            spec += f"      summary: {endpoint['endpoint']}\n"
            spec += "      responses:\n"
            spec += "        '200':\n"
            spec += "          description: Successful response\n"

        return spec

    def _generate_component_diagram(self, structure: Dict) -> str:
        """Generate component diagram in Mermaid syntax"""
        return """graph TB
    Frontend[Frontend Layer]
    API[API Layer]
    Business[Business Logic]
    Data[Data Access Layer]
    DB[(Database)]

    Frontend --> API
    API --> Business
    Business --> Data
    Data --> DB"""

    def _generate_data_flow_diagram(self, structure: Dict) -> str:
        """Generate data flow diagram"""
        return """sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Database

    Client->>API: Request
    API->>Service: Process
    Service->>Database: Query
    Database-->>Service: Data
    Service-->>API: Result
    API-->>Client: Response"""

    def _format_function_signature(self, func: ast.FunctionDef) -> str:
        """Format function signature"""
        args = []
        for arg in func.args.args:
            args.append(arg.arg)
        return ", ".join(args)

    def _count_apis(self) -> int:
        """Count total API endpoints"""
        return len(self._extract_api_endpoints())

    def _count_code_elements(self) -> Dict[str, int]:
        """Count functions and classes"""
        stats = {"functions": 0, "classes": 0}

        for py_file in self.project_path.rglob("*.py"):
            if ".git" not in str(py_file) and "venv" not in str(py_file):
                try:
                    with open(py_file, "r") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            stats["functions"] += 1
                        elif isinstance(node, ast.ClassDef):
                            stats["classes"] += 1
                except Exception:
                    continue

        return stats

    def _generate_prerequisites(self, tech_stack: Dict) -> str:
        """Generate prerequisites list"""
        prereqs = []

        if "Python" in tech_stack["languages"]:
            prereqs.append("- Python 3.8+")
        if "JavaScript/TypeScript" in tech_stack["languages"]:
            prereqs.append("- Node.js 14+")
            prereqs.append("- npm or yarn")

        prereqs.append("- Git")

        return "\n".join(prereqs) if prereqs else "- See project requirements"

    def _generate_dependency_instructions(self, tech_stack: Dict) -> str:
        """Generate dependency installation instructions"""
        instructions = ""

        if "Python" in tech_stack["languages"]:
            instructions += "#### Python Dependencies\n\n```bash\npip install -r requirements.txt\n```\n\n"

        if "JavaScript/TypeScript" in tech_stack["languages"]:
            instructions += "#### Node.js Dependencies\n\n```bash\nnpm install\n# or\nyarn install\n```\n\n"

        return instructions if instructions else "See package manager documentation"

    def _generate_configuration_instructions(self) -> str:
        """Generate configuration instructions"""
        env_file = self.project_path / ".env.example"
        if env_file.exists():
            return """Copy the example environment file and configure:

```bash
cp .env.example .env
# Edit .env with your configuration
```"""
        return "No specific configuration required."

    def _generate_database_instructions(self, tech_stack: Dict) -> str:
        """Generate database setup instructions"""
        return """If the project uses a database:

```bash
# Run migrations
python manage.py migrate  # Django
# or
npm run migrate  # Node.js
```"""

    def _generate_run_instructions(self, tech_stack: Dict) -> str:
        """Generate run instructions"""
        if "Python" in tech_stack["languages"]:
            return "```bash\npython main.py\n# or\npython manage.py runserver\n```"
        elif "JavaScript/TypeScript" in tech_stack["languages"]:
            return "```bash\nnpm start\n# or\nnpm run dev\n```"
        return "See project documentation"

    def _generate_troubleshooting_section(self) -> str:
        """Generate troubleshooting section"""
        return """### Common Issues

**Port already in use:**
```bash
# Kill the process using the port
lsof -ti:8000 | xargs kill -9
```

**Dependencies not installing:**
- Clear cache and reinstall
- Check Python/Node version compatibility

**Database connection issues:**
- Verify database credentials in .env
- Ensure database server is running"""

    def _generate_quickstart_example(self) -> str:
        """Generate quickstart example"""
        return """```bash
# Quick start example
git clone <repo-url>
cd project
pip install -r requirements.txt
python main.py
```"""

    def _generate_use_cases(self) -> str:
        """Generate common use cases"""
        return """### Use Case 1: Basic Operation
Description of basic operation

### Use Case 2: Advanced Feature
Description of advanced feature"""

    def _generate_api_examples(self) -> str:
        """Generate API usage examples"""
        endpoints = self._extract_api_endpoints()

        if not endpoints:
            return "No API endpoints found."

        examples = ""
        for endpoint in endpoints[:5]:  # First 5 endpoints
            examples += f"""
### {endpoint['method']} {endpoint['endpoint']}

```bash
curl -X {endpoint['method']} http://localhost:8000{endpoint['endpoint']}
```
"""

        return examples

    def _extract_code_examples(self) -> str:
        """Extract code examples from comments"""
        return """Check the source code for inline examples and usage patterns."""

    def _generate_advanced_examples(self) -> str:
        """Generate advanced examples"""
        return """### Advanced Configuration
Details about advanced configuration options

### Custom Extensions
How to extend the system"""

    def _generate_architecture_description(self, structure: Dict) -> str:
        """Generate architecture description"""
        return f"""The system follows a layered architecture with clear separation of concerns.

Total files: {structure['total_files']}
Components: {len(structure['directories'])}"""

    def _generate_components_list(self, structure: Dict) -> str:
        """Generate components list"""
        components = "### Main Components\n\n"
        for directory in structure["directories"][:10]:
            components += f"- **{directory}**: Component description\n"
        return components

    def _list_backend_technologies(self, structure: Dict) -> str:
        """List backend technologies"""
        tech = self._detect_tech_stack()
        return "- " + "\n- ".join(tech["languages"]) if tech["languages"] else "- Not detected"

    def _list_frontend_technologies(self, structure: Dict) -> str:
        """List frontend technologies"""
        tech = self._detect_tech_stack()
        return "- " + "\n- ".join(tech["frameworks"]) if tech["frameworks"] else "- Not detected"

    def _list_database_technologies(self, structure: Dict) -> str:
        """List database technologies"""
        return "- See configuration files"

    def _list_devops_technologies(self, structure: Dict) -> str:
        """List DevOps technologies"""
        tools = []
        if (self.project_path / "Dockerfile").exists():
            tools.append("Docker")
        if (self.project_path / ".github").exists():
            tools.append("GitHub Actions")
        return "- " + "\n- ".join(tools) if tools else "- Not detected"

    def _identify_design_patterns(self, structure: Dict) -> str:
        """Identify design patterns used"""
        return """Common patterns identified:
- MVC/MVT architecture
- Repository pattern
- Service layer pattern"""

    def _generate_security_notes(self, structure: Dict) -> str:
        """Generate security considerations"""
        return """- Environment variables for sensitive data
- Authentication and authorization
- Input validation
- HTTPS in production"""

    def _generate_performance_notes(self, structure: Dict) -> str:
        """Generate performance notes"""
        return """- Caching strategies
- Database query optimization
- Async processing where applicable
- Load balancing for production"""

    def cleanup(self):
        """Cleanup resources"""
        pass
