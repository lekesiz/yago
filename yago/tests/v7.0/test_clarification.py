"""
Tests for ClarificationAgent
"""

import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.clarification_agent import (
    ClarificationAgent,
    ProjectAnalysis,
    ClarificationBrief,
    get_clarification_agent
)


class TestProjectAnalysis:
    """Test project input analysis"""

    def test_ecommerce_detection(self):
        """Test e-commerce project type detection"""
        agent = ClarificationAgent(interactive_mode=False)
        analysis = agent.analyze_input("Build an e-commerce site with payment")

        assert analysis.project_type == "e-commerce"
        assert "payment" in analysis.implied_features
        assert analysis.complexity_estimate in ["simple", "medium", "complex"]

    def test_dashboard_detection(self):
        """Test dashboard project type detection"""
        agent = ClarificationAgent(interactive_mode=False)
        analysis = agent.analyze_input("Create analytics dashboard with charts")

        assert analysis.project_type == "dashboard"
        assert len(analysis.keywords) > 0

    def test_api_detection(self):
        """Test API project type detection"""
        agent = ClarificationAgent(interactive_mode=False)
        analysis = agent.analyze_input("Build REST API with authentication")

        assert analysis.project_type == "api"
        assert "authentication" in analysis.implied_features or "api" in analysis.implied_features

    def test_complexity_estimation(self):
        """Test complexity estimation"""
        agent = ClarificationAgent(interactive_mode=False)

        # Simple
        simple_analysis = agent.analyze_input("CLI tool")
        assert simple_analysis.complexity_estimate == "simple"

        # Complex
        complex_analysis = agent.analyze_input(
            "Full-stack e-commerce platform with payment, authentication, "
            "inventory management, admin dashboard, and real-time analytics"
        )
        assert complex_analysis.complexity_estimate in ["medium", "complex"]


class TestQuestionGeneration:
    """Test question generation"""

    def test_basic_questions_generated(self):
        """Test that basic questions are always generated"""
        agent = ClarificationAgent(interactive_mode=False)
        analysis = ProjectAnalysis(
            project_type="general",
            implied_features=[],
            complexity_estimate="simple",
            keywords=[]
        )

        questions = agent.generate_questions(analysis, mode="full")

        # Check basic questions are present
        question_keys = [q["key"] for q in questions]
        assert "language" in question_keys
        assert "frontend" in question_keys
        assert "backend" in question_keys
        assert "database" in question_keys

    def test_ecommerce_specific_questions(self):
        """Test e-commerce specific questions are added"""
        agent = ClarificationAgent(interactive_mode=False)
        analysis = ProjectAnalysis(
            project_type="e-commerce",
            implied_features=["payment"],
            complexity_estimate="medium",
            keywords=["shop", "cart"]
        )

        questions = agent.generate_questions(analysis, mode="full")
        question_keys = [q["key"] for q in questions]

        # E-commerce specific
        assert "payment" in question_keys or len(questions) > 4

    def test_minimal_mode(self):
        """Test minimal mode generates fewer questions"""
        agent = ClarificationAgent(interactive_mode=False)
        analysis = ProjectAnalysis(
            project_type="api",
            implied_features=[],
            complexity_estimate="simple",
            keywords=[]
        )

        full_questions = agent.generate_questions(analysis, mode="full")
        minimal_questions = agent.generate_questions(analysis, mode="minimal")

        assert len(minimal_questions) < len(full_questions)


class TestBriefGeneration:
    """Test brief generation"""

    def test_brief_structure(self):
        """Test brief has correct structure"""
        agent = ClarificationAgent(interactive_mode=False)

        analysis = ProjectAnalysis(
            project_type="e-commerce",
            implied_features=["payment", "authentication"],
            complexity_estimate="medium",
            keywords=["shop"]
        )

        answers = {
            "language": "Python",
            "frontend": "Next.js",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "payment": "Stripe",
            "deployment": "Docker",
        }

        brief = agent.generate_brief("E-commerce site", analysis, answers)

        assert brief.project_id.startswith("e-commerce_")
        assert brief.user_input == "E-commerce site"
        assert "tech_stack" in brief.clarifications
        assert "auto_generated" in brief.dict()

    def test_required_agents_detection(self):
        """Test correct agents are identified"""
        agent = ClarificationAgent(interactive_mode=False)

        analysis = ProjectAnalysis(
            project_type="e-commerce",
            implied_features=["payment"],
            complexity_estimate="medium",
            keywords=[]
        )

        answers = {
            "payment": "Stripe",
            "deployment": "Docker",
            "frontend": "React",
        }

        brief = agent.generate_brief("E-commerce", analysis, answers)

        required_agents = brief.auto_generated["required_agents"]

        # Base agents should always be present
        assert "Planner" in required_agents
        assert "Coder" in required_agents

        # Payment triggers SecurityAgent
        assert "SecurityAgent" in required_agents

        # Docker triggers DevOpsAgent
        assert "DevOpsAgent" in required_agents

    def test_todo_list_generation(self):
        """Test TODO list is generated"""
        agent = ClarificationAgent(interactive_mode=False)

        clarifications = {
            "tech_stack": {"frontend": "React", "backend": "FastAPI"},
            "payment": "Stripe",
            "infrastructure": {"deployment": "Docker"}
        }

        todos = agent.generate_todo_list(clarifications, ["Planner", "Coder", "SecurityAgent"])

        assert len(todos) > 0
        assert all("task" in todo for todo in todos)
        assert all("agent" in todo for todo in todos)
        assert all("priority" in todo for todo in todos)

        # Check payment task exists
        payment_tasks = [t for t in todos if "Stripe" in t["task"] or "payment" in t["task"].lower()]
        assert len(payment_tasks) > 0


class TestBriefStorage:
    """Test brief storage and retrieval"""

    def test_save_and_load_brief(self, tmp_path):
        """Test saving and loading briefs"""
        agent = ClarificationAgent(interactive_mode=False)
        agent.storage_path = tmp_path  # Use temp directory

        # Create brief
        analysis = ProjectAnalysis(
            project_type="api",
            implied_features=[],
            complexity_estimate="simple",
            keywords=[]
        )

        brief = agent.generate_brief("Simple API", analysis, {"language": "Python"})

        # Save
        saved_path = agent.save_brief(brief)
        assert saved_path.exists()

        # Load
        loaded_brief = agent.load_brief(brief.project_id)
        assert loaded_brief is not None
        assert loaded_brief.project_id == brief.project_id
        assert loaded_brief.user_input == brief.user_input

    def test_load_nonexistent_brief(self):
        """Test loading non-existent brief returns None"""
        agent = ClarificationAgent(interactive_mode=False)
        loaded = agent.load_brief("nonexistent_12345")

        assert loaded is None


class TestIntegration:
    """Integration tests"""

    def test_full_clarification_flow_auto_mode(self):
        """Test complete clarification flow in auto mode"""
        agent = ClarificationAgent(interactive_mode=False, clarification_depth="auto")

        brief = agent.clarify_requirements("Build an e-commerce site with Stripe")

        # Verify brief structure
        assert brief.project_id
        assert brief.timestamp
        assert brief.clarifications
        assert brief.auto_generated

        # Verify auto-generated data
        assert "required_agents" in brief.auto_generated
        assert "todo_list" in brief.auto_generated
        assert "estimated_total_cost" in brief.auto_generated

    def test_factory_function(self):
        """Test factory function works"""
        agent = get_clarification_agent(interactive=False, depth="minimal")

        assert isinstance(agent, ClarificationAgent)
        assert agent.interactive_mode is False
        assert agent.clarification_depth == "minimal"


# Fixtures
@pytest.fixture
def sample_agent():
    """Create sample agent for testing"""
    return ClarificationAgent(interactive_mode=False, clarification_depth="full")


@pytest.fixture
def sample_analysis():
    """Create sample analysis"""
    return ProjectAnalysis(
        project_type="e-commerce",
        implied_features=["payment", "authentication"],
        complexity_estimate="medium",
        keywords=["shop", "cart", "payment"]
    )


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
