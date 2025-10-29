"""
YAGO v8.0 - AI Code Executor Service
Real AI-powered code generation and project execution
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

try:
    from .ai_clarification_service import get_ai_clarification_service
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ai_clarification_service import get_ai_clarification_service


class ProjectFileSystem:
    """Manages project file storage"""

    def __init__(self, base_path: str = "./generated_projects"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_project_directory(self, project_id: str) -> Path:
        """Create project directory structure"""
        project_path = self.base_path / project_id
        project_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        (project_path / "docs").mkdir(exist_ok=True)

        return project_path

    def save_file(self, project_id: str, file_path: str, content: str):
        """Save a file to project directory"""
        project_path = self.base_path / project_id
        full_path = project_path / file_path

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_project_path(self, project_id: str) -> Path:
        """Get project directory path"""
        return self.base_path / project_id


class AICodeExecutor:
    """
    Real AI-powered code generation and execution
    Transforms user requirements into working code
    """

    def __init__(self):
        self.ai_service = get_ai_clarification_service()
        self.file_system = ProjectFileSystem()
        self.progress_callbacks = {}

    def register_progress_callback(self, project_id: str, callback):
        """Register callback for progress updates"""
        self.progress_callbacks[project_id] = callback

    async def update_progress(self, project_id: str, progress: int, message: str):
        """Update project execution progress"""
        if project_id in self.progress_callbacks:
            await self.progress_callbacks[project_id](progress, message)

    async def generate_architecture(self, brief: dict) -> dict:
        """Generate project architecture from brief"""

        prompt = f"""
Based on this project brief, design a complete software architecture.

Project Details:
{json.dumps(brief, indent=2)}

Please provide:
1. Tech stack recommendations (language, frameworks, libraries)
2. Project structure (folders and files)
3. Key components and their responsibilities
4. Data models/schemas
5. API endpoints (if applicable)

Return as structured JSON with keys: tech_stack, structure, components, data_models, apis
"""

        system_message = "You are an expert software architect. Design clean, scalable architectures."

        response = self.ai_service._call_ai_provider(
            provider="openai",
            prompt=prompt,
            system_message=system_message,
            task_type="detailed"
        )

        # Parse response (try to extract JSON, fallback to text)
        try:
            # Look for JSON in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                architecture = json.loads(json_match.group())
            else:
                # Fallback structure
                architecture = {
                    "tech_stack": self._extract_tech_stack(response),
                    "structure": self._extract_structure(response),
                    "components": response,
                    "data_models": {},
                    "apis": []
                }
        except:
            architecture = {
                "tech_stack": "Python/FastAPI",
                "structure": "MVC pattern",
                "components": response,
                "data_models": {},
                "apis": []
            }

        return architecture

    def _extract_tech_stack(self, text: str) -> str:
        """Extract tech stack from AI response"""
        # Simple extraction - look for common patterns
        if "python" in text.lower():
            return "Python"
        elif "node" in text.lower() or "javascript" in text.lower():
            return "Node.js"
        elif "react" in text.lower():
            return "React"
        else:
            return "Python"

    def _extract_structure(self, text: str) -> dict:
        """Extract project structure from AI response"""
        return {
            "src/": "Source code",
            "tests/": "Test files",
            "docs/": "Documentation"
        }

    async def generate_code_files(self, architecture: dict, brief: dict) -> List[dict]:
        """Generate actual code files based on architecture"""

        files = []

        # 1. Generate main application file
        main_file = await self._generate_main_file(architecture, brief)
        files.append(main_file)

        # 2. Generate models/schemas
        models_file = await self._generate_models(architecture, brief)
        files.append(models_file)

        # 3. Generate API endpoints (if applicable)
        if architecture.get("apis"):
            api_file = await self._generate_api(architecture, brief)
            files.append(api_file)

        # 4. Generate README
        readme = await self._generate_readme(architecture, brief)
        files.append(readme)

        # 5. Generate requirements.txt or package.json
        deps_file = await self._generate_dependencies(architecture)
        files.append(deps_file)

        return files

    async def _generate_main_file(self, architecture: dict, brief: dict) -> dict:
        """Generate main application file"""

        tech_stack = architecture.get("tech_stack", "Python")

        prompt = f"""
Create the main application file for this project.

Project: {brief.get('project_idea', 'Application')}
Tech Stack: {tech_stack}
Architecture: {json.dumps(architecture.get('components', {}), indent=2)}

Generate clean, production-ready code with:
- Proper imports
- Error handling
- Comments
- Main entry point

Return ONLY the code, no explanations.
"""

        code = self.ai_service._call_ai_provider(
            provider="openai",
            prompt=prompt,
            system_message="You are an expert software developer. Write clean, efficient code.",
            task_type="detailed"
        )

        # Determine file extension
        tech_stack_str = str(tech_stack) if not isinstance(tech_stack, str) else tech_stack
        ext = ".py" if "python" in tech_stack_str.lower() else ".js"

        return {
            "path": f"src/main{ext}",
            "content": self._clean_code(code),
            "type": "code"
        }

    async def _generate_models(self, architecture: dict, brief: dict) -> dict:
        """Generate data models/schemas"""

        prompt = f"""
Create data models for this project.

Project: {brief.get('project_idea', 'Application')}
Data Requirements: {json.dumps(brief, indent=2)}

Generate data models with:
- Proper field types
- Validations
- Relationships (if any)

Return ONLY the code, no explanations.
"""

        code = self.ai_service._call_ai_provider(
            provider="openai",
            prompt=prompt,
            system_message="You are an expert in data modeling. Create efficient schemas.",
            task_type="detailed"
        )

        return {
            "path": "src/models.py",
            "content": self._clean_code(code),
            "type": "code"
        }

    async def _generate_api(self, architecture: dict, brief: dict) -> dict:
        """Generate API endpoints"""

        prompt = f"""
Create API endpoints for this project.

Project: {brief.get('project_idea', 'Application')}
APIs Needed: {json.dumps(architecture.get('apis', []), indent=2)}

Generate RESTful API with:
- CRUD operations
- Error handling
- Input validation
- Proper status codes

Return ONLY the code, no explanations.
"""

        code = self.ai_service._call_ai_provider(
            provider="anthropic",  # Use Claude for API generation
            prompt=prompt,
            system_message="You are an expert API developer. Create robust, RESTful APIs.",
            task_type="detailed"
        )

        return {
            "path": "src/api.py",
            "content": self._clean_code(code),
            "type": "code"
        }

    async def _generate_readme(self, architecture: dict, brief: dict) -> dict:
        """Generate README documentation"""

        prompt = f"""
Create a comprehensive README.md for this project.

Project: {brief.get('project_idea', 'Application')}
Tech Stack: {architecture.get('tech_stack', 'N/A')}

Include:
- Project description
- Features
- Installation instructions
- Usage examples
- API documentation (if applicable)
- License

Use markdown format.
"""

        content = self.ai_service._call_ai_provider(
            provider="openai",
            prompt=prompt,
            system_message="You are a technical writer. Create clear, comprehensive documentation.",
            task_type="detailed"
        )

        return {
            "path": "README.md",
            "content": content,
            "type": "documentation"
        }

    async def _generate_dependencies(self, architecture: dict) -> dict:
        """Generate dependencies file"""

        tech_stack = architecture.get("tech_stack", "Python")
        tech_stack_str = str(tech_stack) if not isinstance(tech_stack, str) else tech_stack

        if "python" in tech_stack_str.lower():
            # Generate requirements.txt
            content = """# YAGO v8.0 Generated Requirements
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
"""
            return {
                "path": "requirements.txt",
                "content": content,
                "type": "config"
            }
        else:
            # Generate package.json
            content = """{
  "name": "yago-generated-project",
  "version": "1.0.0",
  "description": "YAGO v8.0 Generated Project",
  "main": "src/main.js",
  "dependencies": {
    "express": "^4.18.2"
  }
}
"""
            return {
                "path": "package.json",
                "content": content,
                "type": "config"
            }

    def _clean_code(self, code: str) -> str:
        """Clean AI-generated code (remove markdown formatting)"""
        # Remove markdown code blocks
        code = code.strip()

        # Remove ```python, ```javascript, etc.
        import re
        code = re.sub(r'^```[\w]*\n', '', code)
        code = re.sub(r'\n```$', '', code)

        return code.strip()

    async def generate_tests(self, files: List[dict], brief: dict) -> List[dict]:
        """Generate test files"""

        tests = []

        # Find main code files
        code_files = [f for f in files if f["type"] == "code"]

        for code_file in code_files[:2]:  # Test first 2 files to save time
            prompt = f"""
Create unit tests for this code.

File: {code_file['path']}
Code:
{code_file['content'][:1000]}  # First 1000 chars

Generate comprehensive tests with:
- Test setup/teardown
- Happy path tests
- Edge case tests
- Error handling tests

Return ONLY the test code, no explanations.
"""

            test_code = self.ai_service._call_ai_provider(
                provider="openai",
                prompt=prompt,
                system_message="You are a testing expert. Write thorough, maintainable tests.",
                task_type="detailed"
            )

            # Determine test file name
            original_name = Path(code_file['path']).stem
            test_path = f"tests/test_{original_name}.py"

            tests.append({
                "path": test_path,
                "content": self._clean_code(test_code),
                "type": "test"
            })

        return tests

    async def execute_project(self, project_id: str, brief: dict, config: dict) -> dict:
        """
        Main execution pipeline:
        1. Generate architecture
        2. Generate code files
        3. Generate tests
        4. Save to filesystem
        5. Return project summary
        """

        try:
            # Step 1: Architecture (20%)
            await self.update_progress(project_id, 10, "Analyzing requirements...")
            architecture = await self.generate_architecture(brief)
            await self.update_progress(project_id, 20, "Architecture designed")

            # Step 2: Code generation (60%)
            await self.update_progress(project_id, 30, "Generating code files...")
            files = await self.generate_code_files(architecture, brief)
            await self.update_progress(project_id, 60, f"Generated {len(files)} files")

            # Step 3: Test generation (80%)
            await self.update_progress(project_id, 70, "Generating tests...")
            tests = await self.generate_tests(files, brief)
            await self.update_progress(project_id, 80, f"Generated {len(tests)} test files")

            # Step 4: Save to filesystem (95%)
            await self.update_progress(project_id, 85, "Saving project files...")
            project_path = self.file_system.create_project_directory(project_id)

            all_files = files + tests
            for file_data in all_files:
                self.file_system.save_file(
                    project_id,
                    file_data['path'],
                    file_data['content']
                )

            await self.update_progress(project_id, 95, "Project saved")

            # Step 5: Calculate statistics
            total_lines = sum(len(f['content'].split('\n')) for f in all_files)
            code_files = [f for f in all_files if f['type'] == 'code']
            test_files = [f for f in all_files if f['type'] == 'test']

            result = {
                "status": "success",
                "project_path": str(project_path),
                "files_generated": len(all_files),
                "code_files": len(code_files),
                "test_files": len(test_files),
                "lines_of_code": total_lines,
                "architecture": architecture,
                "files": [{"path": f['path'], "type": f['type']} for f in all_files]
            }

            await self.update_progress(project_id, 100, "✅ Project completed!")

            return result

        except Exception as e:
            await self.update_progress(project_id, -1, f"❌ Error: {str(e)}")
            raise


# Singleton instance
_executor_instance = None

def get_code_executor() -> AICodeExecutor:
    """Get singleton instance of AICodeExecutor"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = AICodeExecutor()
    return _executor_instance
