"""
Auto-Debug System for YAGO
Automatically detects, analyzes, and fixes code errors
"""

import re
import ast
import traceback
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger("YAGO")


class ErrorType:
    """Error type classifications"""
    SYNTAX = "syntax"
    IMPORT = "import"
    RUNTIME = "runtime"
    TYPE = "type"
    ATTRIBUTE = "attribute"
    NAME = "name"
    INDENTATION = "indentation"
    FILE_NOT_FOUND = "file_not_found"
    UNKNOWN = "unknown"


class ErrorAnalysis:
    """Result of error analysis"""

    def __init__(
        self,
        error_type: str,
        error_message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
        code_snippet: Optional[str] = None,
        suggested_fix: Optional[str] = None,
        confidence: float = 0.0,
    ):
        self.error_type = error_type
        self.error_message = error_message
        self.file_path = file_path
        self.line_number = line_number
        self.column = column
        self.code_snippet = code_snippet
        self.suggested_fix = suggested_fix
        self.confidence = confidence
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "error_type": self.error_type,
            "error_message": self.error_message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
            "code_snippet": self.code_snippet,
            "suggested_fix": self.suggested_fix,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


class AutoDebugger:
    """Automatic debugging system"""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.error_history = []
        self.fix_success_rate = {}
        self.common_patterns = self._load_common_patterns()

    def _load_common_patterns(self) -> Dict[str, Dict[str, str]]:
        """Load common error patterns and their fixes"""
        return {
            # Import errors
            r"No module named ['\"]([^'\"]+)['\"]": {
                "type": ErrorType.IMPORT,
                "fix_template": "Missing dependency: {0}. Try: pip install {0}",
            },
            r"cannot import name ['\"]([^'\"]+)['\"]": {
                "type": ErrorType.IMPORT,
                "fix_template": "Import '{0}' not found. Check spelling or module structure.",
            },
            # Syntax errors
            r"invalid syntax": {
                "type": ErrorType.SYNTAX,
                "fix_template": "Syntax error detected. Check for missing colons, parentheses, or quotes.",
            },
            r"unexpected EOF": {
                "type": ErrorType.SYNTAX,
                "fix_template": "Unexpected end of file. Missing closing bracket/parenthesis/quote.",
            },
            # Name errors
            r"name ['\"]([^'\"]+)['\"] is not defined": {
                "type": ErrorType.NAME,
                "fix_template": "Variable '{0}' not defined. Check for typos or missing imports.",
            },
            # Attribute errors
            r"'([^']+)' object has no attribute ['\"]([^'\"]+)['\"]": {
                "type": ErrorType.ATTRIBUTE,
                "fix_template": "Object '{0}' has no attribute '{1}'. Check API documentation.",
            },
            # Type errors
            r"unsupported operand type": {
                "type": ErrorType.TYPE,
                "fix_template": "Type mismatch in operation. Check variable types.",
            },
            # Indentation errors
            r"unexpected indent": {
                "type": ErrorType.INDENTATION,
                "fix_template": "Indentation error. Use consistent spaces or tabs (prefer 4 spaces).",
            },
            # File errors
            r"No such file or directory: ['\"]([^'\"]+)['\"]": {
                "type": ErrorType.FILE_NOT_FOUND,
                "fix_template": "File not found: '{0}'. Check path or create file.",
            },
        }

    def analyze_error(self, error_output: str, file_path: Optional[str] = None) -> ErrorAnalysis:
        """
        Analyze error output and extract information

        Args:
            error_output: Raw error output from execution
            file_path: File that caused the error

        Returns:
            ErrorAnalysis object with details and suggestions
        """
        # Extract error type and message
        error_type = ErrorType.UNKNOWN
        error_message = error_output.strip()
        suggested_fix = None
        confidence = 0.5

        # Try to match common patterns
        for pattern, info in self.common_patterns.items():
            match = re.search(pattern, error_output, re.IGNORECASE)
            if match:
                error_type = info["type"]
                confidence = 0.8

                # Format fix template with captured groups
                try:
                    suggested_fix = info["fix_template"].format(*match.groups())
                except:
                    suggested_fix = info["fix_template"]
                break

        # Extract file, line, column from traceback
        line_number = None
        column = None
        code_snippet = None

        # Parse traceback format: File "path", line X
        traceback_match = re.search(r'File "([^"]+)", line (\d+)', error_output)
        if traceback_match:
            file_path = traceback_match.group(1)
            line_number = int(traceback_match.group(2))

            # Try to extract code snippet
            if Path(file_path).exists():
                code_snippet = self._extract_code_snippet(file_path, line_number)

        # Column number (for syntax errors)
        column_match = re.search(r"column (\d+)", error_output)
        if column_match:
            column = int(column_match.group(1))

        analysis = ErrorAnalysis(
            error_type=error_type,
            error_message=error_message,
            file_path=file_path,
            line_number=line_number,
            column=column,
            code_snippet=code_snippet,
            suggested_fix=suggested_fix,
            confidence=confidence,
        )

        # Record in history
        self.error_history.append(analysis)

        return analysis

    def _extract_code_snippet(self, file_path: str, line_number: int, context: int = 3) -> str:
        """Extract code snippet around error line"""
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            start = max(0, line_number - context - 1)
            end = min(len(lines), line_number + context)

            snippet_lines = []
            for i in range(start, end):
                marker = ">>> " if i == line_number - 1 else "    "
                snippet_lines.append(f"{marker}{i+1:4d} | {lines[i].rstrip()}")

            return "\n".join(snippet_lines)
        except Exception as e:
            logger.debug(f"Failed to extract code snippet: {e}")
            return None

    def check_syntax(self, file_path: str) -> Optional[ErrorAnalysis]:
        """
        Check Python file for syntax errors

        Args:
            file_path: Path to Python file

        Returns:
            ErrorAnalysis if syntax error found, None otherwise
        """
        try:
            with open(file_path, "r") as f:
                code = f.read()

            ast.parse(code)
            return None  # No syntax errors

        except SyntaxError as e:
            error_output = f"SyntaxError: {e.msg}\n  File \"{file_path}\", line {e.lineno}"
            if e.offset:
                error_output += f", column {e.offset}"

            return self.analyze_error(error_output, file_path)

        except Exception as e:
            error_output = f"Error parsing file: {str(e)}"
            return self.analyze_error(error_output, file_path)

    def check_imports(self, file_path: str) -> List[ErrorAnalysis]:
        """
        Check if all imports in file are available

        Args:
            file_path: Path to Python file

        Returns:
            List of ErrorAnalysis for missing imports
        """
        errors = []

        try:
            with open(file_path, "r") as f:
                code = f.read()

            # Parse and find imports
            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])

            # Check each import
            for imp in set(imports):
                if not self._is_import_available(imp):
                    error_output = f"ModuleNotFoundError: No module named '{imp}'"
                    analysis = self.analyze_error(error_output, file_path)
                    errors.append(analysis)

        except Exception as e:
            logger.debug(f"Failed to check imports: {e}")

        return errors

    def _is_import_available(self, module_name: str) -> bool:
        """Check if a module can be imported"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def run_file_with_debug(self, file_path: str, timeout: int = 10) -> Tuple[bool, Optional[ErrorAnalysis]]:
        """
        Run Python file and capture any errors

        Args:
            file_path: Path to Python file
            timeout: Execution timeout in seconds

        Returns:
            (success, error_analysis) tuple
        """
        try:
            result = subprocess.run(
                ["python", file_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace_path,
            )

            if result.returncode != 0:
                # Error occurred
                error_output = result.stderr or result.stdout
                analysis = self.analyze_error(error_output, file_path)
                return False, analysis
            else:
                # Success
                return True, None

        except subprocess.TimeoutExpired:
            error_output = f"Execution timeout after {timeout} seconds"
            analysis = self.analyze_error(error_output, file_path)
            return False, analysis

        except Exception as e:
            error_output = f"Failed to run file: {str(e)}"
            analysis = self.analyze_error(error_output, file_path)
            return False, analysis

    def suggest_fixes(self, analysis: ErrorAnalysis) -> List[str]:
        """
        Generate multiple fix suggestions for an error

        Args:
            analysis: ErrorAnalysis object

        Returns:
            List of suggested fixes (code or instructions)
        """
        fixes = []

        # Add pattern-based fix if available
        if analysis.suggested_fix:
            fixes.append(analysis.suggested_fix)

        # Add error-type specific fixes
        if analysis.error_type == ErrorType.IMPORT:
            # Extract module name
            match = re.search(r"['\"]([^'\"]+)['\"]", analysis.error_message)
            if match:
                module = match.group(1)
                fixes.append(f"Install missing package: pip install {module}")
                fixes.append(f"Check if package name is correct (typo?)")

        elif analysis.error_type == ErrorType.INDENTATION:
            fixes.append("Fix indentation: Use 4 spaces consistently")
            fixes.append("Remove tabs and use spaces only")

        elif analysis.error_type == ErrorType.SYNTAX:
            fixes.append("Check for missing colons at end of if/for/def statements")
            fixes.append("Verify all parentheses/brackets/quotes are properly closed")

        elif analysis.error_type == ErrorType.NAME:
            fixes.append("Check variable spelling")
            fixes.append("Ensure variable is defined before use")
            fixes.append("Check import statements")

        elif analysis.error_type == ErrorType.ATTRIBUTE:
            fixes.append("Verify object type and available methods")
            fixes.append("Check API documentation for correct attribute name")

        # Add code snippet context if available
        if analysis.code_snippet:
            fixes.append(f"\nProblem area:\n{analysis.code_snippet}")

        return fixes

    def auto_fix_common_errors(self, file_path: str) -> bool:
        """
        Attempt to automatically fix common errors

        Args:
            file_path: Path to file to fix

        Returns:
            True if fixes were applied, False otherwise
        """
        try:
            with open(file_path, "r") as f:
                original_content = f.read()

            modified_content = original_content
            changes_made = False

            # Fix 1: Remove trailing whitespace
            lines = modified_content.split("\n")
            lines = [line.rstrip() for line in lines]
            new_content = "\n".join(lines)
            if new_content != modified_content:
                modified_content = new_content
                changes_made = True
                logger.info(f"🔧 Fixed: Removed trailing whitespace")

            # Fix 2: Fix mixed tabs/spaces
            if "\t" in modified_content:
                modified_content = modified_content.replace("\t", "    ")
                changes_made = True
                logger.info(f"🔧 Fixed: Converted tabs to spaces")

            # Fix 3: Ensure file ends with newline
            if modified_content and not modified_content.endswith("\n"):
                modified_content += "\n"
                changes_made = True
                logger.info(f"🔧 Fixed: Added final newline")

            # Save if changes made
            if changes_made:
                with open(file_path, "w") as f:
                    f.write(modified_content)
                return True

            return False

        except Exception as e:
            logger.debug(f"Auto-fix failed: {e}")
            return False

    def get_debug_report(self) -> Dict[str, Any]:
        """Generate debug session report"""
        total_errors = len(self.error_history)
        error_types = {}

        for analysis in self.error_history:
            error_types[analysis.error_type] = error_types.get(analysis.error_type, 0) + 1

        return {
            "total_errors_detected": total_errors,
            "error_breakdown": error_types,
            "fix_success_rate": self.fix_success_rate,
            "error_history": [e.to_dict() for e in self.error_history],
        }


# Singleton instance
_auto_debugger: Optional[AutoDebugger] = None


def get_auto_debugger(workspace_path: str = "./workspace") -> AutoDebugger:
    """Get or create auto debugger singleton"""
    global _auto_debugger
    if _auto_debugger is None:
        _auto_debugger = AutoDebugger(workspace_path=workspace_path)
    return _auto_debugger


def reset_auto_debugger(workspace_path: str = "./workspace"):
    """Reset auto debugger (for new session)"""
    global _auto_debugger
    _auto_debugger = AutoDebugger(workspace_path=workspace_path)
