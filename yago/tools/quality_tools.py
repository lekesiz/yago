"""Quality Tools for YAGO Agents"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from utils.code_quality import get_quality_analyzer


class AnalyzeQualityInput(BaseModel):
    """Input for AnalyzeQualityTool"""
    pass


class AnalyzeQualityTool(BaseTool):
    name: str = "analyze_code_quality"
    description: str = (
        "Analyze code quality of entire project. "
        "Returns quality score, grade, and recommendations."
    )
    args_schema: Type[BaseModel] = AnalyzeQualityInput

    def _run(self) -> str:
        """Analyze project quality"""
        analyzer = get_quality_analyzer()
        result = analyzer.analyze_project()

        if 'error' in result:
            return f"❌ {result['error']}"

        output = f"📊 Code Quality Report\n\n"
        output += f"Files Analyzed: {result['num_files']}\n"
        output += f"Total Lines: {result['total_lines']}\n"
        output += f"Quality Score: {result['avg_quality_score']}/100\n"
        output += f"Grade: {result['overall_grade']}\n\n"

        if result.get('recommendations'):
            output += "💡 Recommendations:\n"
            for rec in result['recommendations']:
                output += f"  - {rec}\n"

        return output


def get_quality_tools():
    return [AnalyzeQualityTool()]
