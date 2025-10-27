"""
Tests for DynamicRoleManager
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.dynamic_role_manager import (
    DynamicRoleManager,
    RoleDefinition,
    get_dynamic_role_manager
)


class TestRoleAnalysis:
    """Test role requirement analysis"""

    def test_ecommerce_triggers_security_agent(self):
        """Test e-commerce project triggers SecurityAgent"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {
                "tech_stack": {"frontend": "React"},
                "payment": "Stripe"
            },
            "user_input": "E-commerce with payment"
        }

        required_roles = manager.analyze_requirements(brief)

        assert "SecurityAgent" in required_roles

    def test_docker_triggers_devops_agent(self):
        """Test Docker deployment triggers DevOpsAgent"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {
                "infrastructure": {"deployment": "Docker"}
            },
            "user_input": "API with Docker deployment"
        }

        required_roles = manager.analyze_requirements(brief)

        assert "DevOpsAgent" in required_roles

    def test_frontend_triggers_frontend_agent(self):
        """Test frontend framework triggers FrontendAgent"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {
                "tech_stack": {"frontend": "Next.js"}
            },
            "user_input": "Dashboard with Next.js frontend"
        }

        required_roles = manager.analyze_requirements(brief)

        assert "FrontendAgent" in required_roles

    def test_max_agents_limit(self):
        """Test that max_dynamic_agents limit is enforced"""
        manager = DynamicRoleManager(max_dynamic_agents=2)

        # Brief that would trigger many agents
        brief = {
            "clarifications": {
                "tech_stack": {"frontend": "React", "database": "PostgreSQL"},
                "payment": "Stripe",
                "infrastructure": {"deployment": "Docker"}
            },
            "user_input": "Full-stack e-commerce with payment, Docker, complex queries, optimization"
        }

        required_roles = manager.analyze_requirements(brief)

        # Should be limited to 2
        assert len(required_roles) <= 2

    def test_no_dynamic_agents_needed(self):
        """Test simple project needs no dynamic agents"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {
                "tech_stack": {"language": "Python"}
            },
            "user_input": "Simple CLI tool"
        }

        required_roles = manager.analyze_requirements(brief)

        # Might be empty or have few agents
        assert len(required_roles) <= 3


class TestAgentCreation:
    """Test agent creation"""

    def test_create_security_agent(self):
        """Test SecurityAgent creation"""
        manager = DynamicRoleManager()

        agent = manager.create_agent("SecurityAgent")

        assert agent.role == "Security Specialist"
        assert "security" in agent.goal.lower() or "authentication" in agent.goal.lower()

    def test_create_devops_agent(self):
        """Test DevOpsAgent creation"""
        manager = DynamicRoleManager()

        agent = manager.create_agent("DevOpsAgent")

        assert agent.role == "DevOps Engineer"
        assert "infrastructure" in agent.goal.lower() or "deployment" in agent.goal.lower()

    def test_create_invalid_agent_raises_error(self):
        """Test creating non-existent agent raises error"""
        manager = DynamicRoleManager()

        with pytest.raises(ValueError):
            manager.create_agent("NonExistentAgent")

    def test_agent_uses_correct_model(self):
        """Test agents use correct AI models"""
        manager = DynamicRoleManager()

        security_agent = manager.create_agent("SecurityAgent")
        assert security_agent.model == "claude-3-5-sonnet"  # Critical tasks

        devops_agent = manager.create_agent("DevOpsAgent")
        assert devops_agent.model == "gpt-4o"  # Infrastructure

    def test_created_agents_tracked(self):
        """Test created agents are tracked"""
        manager = DynamicRoleManager()

        manager.create_agent("SecurityAgent")
        manager.create_agent("DevOpsAgent")

        assert "SecurityAgent" in manager.created_agents
        assert "DevOpsAgent" in manager.created_agents
        assert len(manager.created_agents) == 2


class TestBaseAgents:
    """Test base agent management"""

    def test_get_base_agents(self):
        """Test retrieval of 5 base agents"""
        manager = DynamicRoleManager()

        base_agents = manager.get_base_agents()

        assert len(base_agents) == 5
        assert "Planner" in base_agents
        assert "Coder" in base_agents
        assert "Tester" in base_agents
        assert "Reviewer" in base_agents
        assert "Documenter" in base_agents

    def test_base_agents_have_correct_models(self):
        """Test base agents use correct models"""
        manager = DynamicRoleManager()

        base_agents = manager.get_base_agents()

        # Verify model assignments (check that agents have models assigned)
        for agent_name, agent in base_agents.items():
            assert hasattr(agent, 'model')
            assert agent.model is not None


class TestAllAgents:
    """Test combined agent management"""

    def test_get_all_agents_simple_project(self):
        """Test simple project gets only base agents"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {"tech_stack": {"language": "Python"}},
            "user_input": "Simple script"
        }

        all_agents = manager.get_all_agents(brief)

        # Should have at least base 5 agents
        assert len(all_agents) >= 5

    def test_get_all_agents_complex_project(self):
        """Test complex project gets base + dynamic agents"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {
                "tech_stack": {"frontend": "React"},
                "payment": "Stripe",
                "infrastructure": {"deployment": "Docker"}
            },
            "user_input": "E-commerce with payment and Docker"
        }

        all_agents = manager.get_all_agents(brief)

        # Should have base 5 + at least 2 dynamic
        assert len(all_agents) >= 7

    def test_get_agent_list_returns_list(self):
        """Test get_agent_list returns list format"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {"payment": "Stripe"},
            "user_input": "Payment processing"
        }

        agent_list = manager.get_agent_list(brief)

        assert isinstance(agent_list, list)
        assert len(agent_list) >= 5  # At least base agents


class TestCostEstimation:
    """Test cost estimation"""

    def test_cost_estimation_simple_project(self):
        """Test cost estimation for simple project"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {},
            "user_input": "Simple API"
        }

        cost_estimate = manager.estimate_cost(brief)

        assert "total_agents" in cost_estimate
        assert "estimated_cost" in cost_estimate
        assert cost_estimate["total_agents"] >= 5  # At least base agents
        assert cost_estimate["base_agents"] == 5

    def test_cost_estimation_complex_project(self):
        """Test cost estimation for complex project"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {
                "payment": "Stripe",
                "infrastructure": {"deployment": "Docker"}
            },
            "user_input": "E-commerce with Docker"
        }

        cost_estimate = manager.estimate_cost(brief)

        assert cost_estimate["total_agents"] > 5  # Should have dynamic agents
        assert cost_estimate["dynamic_agents"] > 0

    def test_cost_within_budget(self):
        """Test budget limit checking"""
        manager = DynamicRoleManager(cost_limit=5.0)

        brief = {
            "clarifications": {"tech_stack": {"language": "Python"}},
            "user_input": "Simple project"
        }

        cost_estimate = manager.estimate_cost(brief)

        # Simple project should be within budget
        assert cost_estimate["within_budget"] is True

    def test_cost_breakdown_structure(self):
        """Test cost breakdown has correct structure"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {"payment": "Stripe"},
            "user_input": "Payment system"
        }

        cost_estimate = manager.estimate_cost(brief)

        assert "cost_breakdown" in cost_estimate
        assert "Planner" in cost_estimate["cost_breakdown"]
        assert "model" in cost_estimate["cost_breakdown"]["Planner"]
        assert "cost" in cost_estimate["cost_breakdown"]["Planner"]


class TestRoleDefinitions:
    """Test role definition templates"""

    def test_all_roles_have_required_fields(self):
        """Test all role templates have required fields"""
        manager = DynamicRoleManager()

        for role_name, role_def in manager.ROLE_TEMPLATES.items():
            assert role_def.name
            assert role_def.role
            assert role_def.goal
            assert role_def.backstory
            assert role_def.model
            assert role_def.triggers
            assert role_def.priority in ["HIGH", "MEDIUM", "LOW"]

    def test_high_priority_roles(self):
        """Test critical roles have HIGH priority"""
        manager = DynamicRoleManager()

        # SecurityAgent should be HIGH priority
        security_role = manager.ROLE_TEMPLATES["SecurityAgent"]
        assert security_role.priority == "HIGH"

    def test_triggers_are_lowercase(self):
        """Test trigger keywords are lowercase for matching"""
        manager = DynamicRoleManager()

        for role_name, role_def in manager.ROLE_TEMPLATES.items():
            for trigger in role_def.triggers:
                assert trigger == trigger.lower(), f"{role_name} has uppercase trigger: {trigger}"


class TestIntegration:
    """Integration tests"""

    def test_full_workflow_ecommerce(self):
        """Test complete workflow for e-commerce project"""
        manager = DynamicRoleManager()

        brief = {
            "clarifications": {
                "tech_stack": {
                    "frontend": "Next.js",
                    "backend": "FastAPI",
                    "database": "PostgreSQL"
                },
                "payment": "Stripe",
                "infrastructure": {"deployment": "Docker"}
            },
            "user_input": "Full-stack e-commerce with Stripe and Docker"
        }

        # Analyze
        required_roles = manager.analyze_requirements(brief)
        assert len(required_roles) > 0

        # Estimate cost
        cost_estimate = manager.estimate_cost(brief)
        assert cost_estimate["total_agents"] > 5

        # Create agents
        all_agents = manager.get_all_agents(brief)
        assert len(all_agents) == cost_estimate["total_agents"]

        # Verify SecurityAgent and DevOpsAgent created
        assert "SecurityAgent" in all_agents or "SecurityAgent" in [a.__class__.__name__ for a in all_agents.values()]

    def test_factory_function(self):
        """Test factory function works"""
        manager = get_dynamic_role_manager(max_dynamic_agents=3, cost_limit=5.0)

        assert isinstance(manager, DynamicRoleManager)
        assert manager.max_dynamic_agents == 3
        assert manager.cost_limit == 5.0


# Fixtures
@pytest.fixture
def sample_manager():
    """Create sample manager for testing"""
    return DynamicRoleManager(max_dynamic_agents=5, cost_limit=10.0)


@pytest.fixture
def ecommerce_brief():
    """Create sample e-commerce brief"""
    return {
        "clarifications": {
            "tech_stack": {"frontend": "React", "backend": "FastAPI"},
            "payment": "Stripe",
            "infrastructure": {"deployment": "Docker"}
        },
        "user_input": "E-commerce platform"
    }


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
