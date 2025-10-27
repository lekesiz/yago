"""
Code Quality Analyzer for YAGO
Analyzes generated code quality with multiple metrics
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import logging

logger = logging.getLogger("YAGO")


class QualityMetrics:
    """Code quality metrics container"""

    def __init__(self):
        self.lines_of_code = 0
        self.num_functions = 0
        self.num_classes = 0
        self.num_comments = 0
        self.num_docstrings = 0
        self.complexity = 0
        self.avg_function_length = 0.0
        self.has_main = False
        self.has_tests = False
        self.quality_score = 0.0


class CodeQualityAnalyzer:
    """Analyzes Python code quality"""

    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace = Path(workspace_path)

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze single Python file"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()

            tree = ast.parse(code)

            metrics = QualityMetrics()

            # Count lines (excluding blanks)
            lines = [l for l in code.split('\n') if l.strip()]
            metrics.lines_of_code = len(lines)

            # Count comments
            metrics.num_comments = sum(1 for l in lines if l.strip().startswith('#'))

            # Analyze AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics.num_functions += 1
                    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                        metrics.num_docstrings += 1
                    # Check for main
                    if node.name == 'main':
                        metrics.has_main = True

                elif isinstance(node, ast.ClassDef):
                    metrics.num_classes += 1
                    if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                        metrics.num_docstrings += 1

            # Avg function length
            if metrics.num_functions > 0:
                metrics.avg_function_length = metrics.lines_of_code / metrics.num_functions

            # Calculate quality score (0-100)
            score = 0

            # Has functions/classes (30 points)
            if metrics.num_functions > 0 or metrics.num_classes > 0:
                score += 30

            # Has docstrings (25 points)
            if metrics.num_docstrings > 0:
                doc_ratio = metrics.num_docstrings / max(metrics.num_functions + metrics.num_classes, 1)
                score += min(25, int(doc_ratio * 25))

            # Has comments (15 points)
            if metrics.num_comments > 0:
                comment_ratio = metrics.num_comments / max(metrics.lines_of_code, 1)
                score += min(15, int(comment_ratio * 100))

            # Has main (10 points)
            if metrics.has_main:
                score += 10

            # Function length (20 points - shorter is better)
            if metrics.avg_function_length > 0:
                if metrics.avg_function_length < 20:
                    score += 20
                elif metrics.avg_function_length < 50:
                    score += 15
                else:
                    score += 5

            metrics.quality_score = score

            return {
                'file': file_path,
                'lines_of_code': metrics.lines_of_code,
                'functions': metrics.num_functions,
                'classes': metrics.num_classes,
                'comments': metrics.num_comments,
                'docstrings': metrics.num_docstrings,
                'avg_function_length': round(metrics.avg_function_length, 1),
                'has_main': metrics.has_main,
                'quality_score': metrics.quality_score,
                'grade': self._get_grade(metrics.quality_score)
            }

        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {e}")
            return {'file': file_path, 'error': str(e)}

    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90: return 'A+'
        if score >= 80: return 'A'
        if score >= 70: return 'B'
        if score >= 60: return 'C'
        if score >= 50: return 'D'
        return 'F'

    def analyze_project(self) -> Dict[str, Any]:
        """Analyze entire project in workspace"""
        py_files = list(self.workspace.rglob("*.py"))

        if not py_files:
            return {'error': 'No Python files found'}

        file_results = []
        total_score = 0
        total_lines = 0

        for py_file in py_files:
            result = self.analyze_file(str(py_file))
            if 'error' not in result:
                file_results.append(result)
                total_score += result['quality_score']
                total_lines += result['lines_of_code']

        avg_score = total_score / len(file_results) if file_results else 0

        return {
            'num_files': len(file_results),
            'total_lines': total_lines,
            'avg_quality_score': round(avg_score, 1),
            'overall_grade': self._get_grade(avg_score),
            'files': file_results,
            'recommendations': self._get_recommendations(file_results)
        }

    def _get_recommendations(self, files: List[Dict]) -> List[str]:
        """Generate improvement recommendations"""
        recs = []

        for f in files:
            if f.get('quality_score', 0) < 70:
                if f.get('docstrings', 0) == 0:
                    recs.append(f"{Path(f['file']).name}: Add docstrings")
                if f.get('comments', 0) == 0:
                    recs.append(f"{Path(f['file']).name}: Add comments")
                if f.get('avg_function_length', 0) > 50:
                    recs.append(f"{Path(f['file']).name}: Reduce function complexity")

        return recs[:5]  # Top 5


_quality_analyzer: Optional[CodeQualityAnalyzer] = None

def get_quality_analyzer(workspace: str = "./workspace") -> CodeQualityAnalyzer:
    global _quality_analyzer
    if _quality_analyzer is None:
        _quality_analyzer = CodeQualityAnalyzer(workspace)
    return _quality_analyzer
