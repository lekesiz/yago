"""
Debug Tools for YAGO Agents
Allows agents to check code for errors and get fix suggestions
"""

from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from utils.auto_debug import get_auto_debugger
from pathlib import Path


class CheckSyntaxInput(BaseModel):
    """Input for CheckSyntaxTool"""

    file_path: str = Field(..., description="Path to Python file to check (relative to workspace)")


class CheckSyntaxTool(BaseTool):
    name: str = "check_syntax"
    description: str = (
        "Check a Python file for syntax errors. "
        "Use this BEFORE running code to catch syntax issues early. "
        "Returns detailed error information if syntax errors found, "
        "or confirmation if code is syntactically correct."
    )
    args_schema: Type[BaseModel] = CheckSyntaxInput

    def _run(self, file_path: str) -> str:
        """Check file syntax"""
        debugger = get_auto_debugger()

        # Make path relative to workspace
        full_path = Path("./workspace") / file_path

        if not full_path.exists():
            return f"❌ File not found: {file_path}"

        analysis = debugger.check_syntax(str(full_path))

        if analysis is None:
            return f"✅ No syntax errors found in {file_path}"

        # Format error message
        result = f"❌ Syntax Error in {file_path}\n\n"
        result += f"Error Type: {analysis.error_type}\n"
        result += f"Message: {analysis.error_message}\n"

        if analysis.line_number:
            result += f"Line: {analysis.line_number}\n"

        if analysis.column:
            result += f"Column: {analysis.column}\n"

        if analysis.code_snippet:
            result += f"\nCode:\n{analysis.code_snippet}\n"

        if analysis.suggested_fix:
            result += f"\nSuggested Fix: {analysis.suggested_fix}\n"

        return result


class CheckImportsInput(BaseModel):
    """Input for CheckImportsTool"""

    file_path: str = Field(..., description="Path to Python file (relative to workspace)")


class CheckImportsTool(BaseTool):
    name: str = "check_imports"
    description: str = (
        "Check if all imports in a Python file are available. "
        "Use this to verify dependencies before running code. "
        "Returns list of missing imports with installation suggestions."
    )
    args_schema: Type[BaseModel] = CheckImportsInput

    def _run(self, file_path: str) -> str:
        """Check file imports"""
        debugger = get_auto_debugger()

        # Make path relative to workspace
        full_path = Path("./workspace") / file_path

        if not full_path.exists():
            return f"❌ File not found: {file_path}"

        errors = debugger.check_imports(str(full_path))

        if not errors:
            return f"✅ All imports are available in {file_path}"

        # Format missing imports
        result = f"❌ Missing Imports in {file_path}\n\n"

        for i, analysis in enumerate(errors, 1):
            result += f"{i}. {analysis.error_message}\n"
            if analysis.suggested_fix:
                result += f"   Fix: {analysis.suggested_fix}\n"

        return result


class RunWithDebugInput(BaseModel):
    """Input for RunWithDebugTool"""

    file_path: str = Field(..., description="Path to Python file to run (relative to workspace)")
    timeout: int = Field(10, description="Execution timeout in seconds (default: 10)")


class RunWithDebugTool(BaseTool):
    name: str = "run_with_debug"
    description: str = (
        "Run a Python file and get detailed error analysis if it fails. "
        "Use this to test code execution and get automatic error diagnosis. "
        "Returns success message or detailed error analysis with fix suggestions."
    )
    args_schema: Type[BaseModel] = RunWithDebugInput

    def _run(self, file_path: str, timeout: int = 10) -> str:
        """Run file with debug"""
        debugger = get_auto_debugger()

        # Make path relative to workspace
        full_path = Path("./workspace") / file_path

        if not full_path.exists():
            return f"❌ File not found: {file_path}"

        success, analysis = debugger.run_file_with_debug(str(full_path), timeout=timeout)

        if success:
            return f"✅ Code executed successfully: {file_path}"

        # Format error analysis
        result = f"❌ Runtime Error in {file_path}\n\n"
        result += f"Error Type: {analysis.error_type}\n"
        result += f"Message: {analysis.error_message}\n"

        if analysis.line_number:
            result += f"Line: {analysis.line_number}\n"

        if analysis.code_snippet:
            result += f"\nCode:\n{analysis.code_snippet}\n"

        # Get multiple fix suggestions
        fixes = debugger.suggest_fixes(analysis)
        if fixes:
            result += f"\n💡 Suggested Fixes:\n"
            for i, fix in enumerate(fixes, 1):
                result += f"{i}. {fix}\n"

        return result


class AutoFixInput(BaseModel):
    """Input for AutoFixTool"""

    file_path: str = Field(..., description="Path to Python file to auto-fix (relative to workspace)")


class AutoFixTool(BaseTool):
    name: str = "auto_fix_common_errors"
    description: str = (
        "Automatically fix common code errors in a file. "
        "Fixes: trailing whitespace, mixed tabs/spaces, missing final newline. "
        "Use this to clean up code before checking syntax. "
        "Returns list of fixes applied or message if no changes needed."
    )
    args_schema: Type[BaseModel] = AutoFixInput

    def _run(self, file_path: str) -> str:
        """Auto-fix common errors"""
        debugger = get_auto_debugger()

        # Make path relative to workspace
        full_path = Path("./workspace") / file_path

        if not full_path.exists():
            return f"❌ File not found: {file_path}"

        changes_made = debugger.auto_fix_common_errors(str(full_path))

        if changes_made:
            return f"✅ Auto-fixed common errors in {file_path}. Check file and re-test."
        else:
            return f"ℹ️  No common errors found in {file_path}. File is clean."


class GetDebugReportInput(BaseModel):
    """Input for GetDebugReportTool"""

    pass  # No input needed


class GetDebugReportTool(BaseTool):
    name: str = "get_debug_report"
    description: str = (
        "Get a summary report of all errors detected during this session. "
        "Use this to review what errors were found and how they were addressed. "
        "Returns statistics and error breakdown."
    )
    args_schema: Type[BaseModel] = GetDebugReportInput

    def _run(self) -> str:
        """Get debug report"""
        debugger = get_auto_debugger()
        report = debugger.get_debug_report()

        result = "📊 Debug Session Report\n\n"
        result += f"Total Errors Detected: {report['total_errors_detected']}\n\n"

        if report['error_breakdown']:
            result += "Error Breakdown:\n"
            for error_type, count in report['error_breakdown'].items():
                result += f"  - {error_type}: {count}\n"
        else:
            result += "No errors detected in this session.\n"

        return result


# Export all debug tools
def get_debug_tools():
    """Get all debug tools for agents"""
    return [
        CheckSyntaxTool(),
        CheckImportsTool(),
        RunWithDebugTool(),
        AutoFixTool(),
        GetDebugReportTool(),
    ]
