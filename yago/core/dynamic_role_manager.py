"""
YAGO v7.0 - Dynamic Role Manager
Dynamically creates specialized agents based on project requirements
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from crewai import Agent

# Import base agents
from agents.yago_agents import YagoAgents

logger = logging.getLogger("YAGO.DynamicRoleManager")


@dataclass
class RoleDefinition:
    """Definition for a dynamic role"""
    name: str
    role: str
    goal: str
    backstory: str
    model: str
    temperature: float = 0.3
    tools: List[Any] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)  # Conditions that trigger this role
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW


class DynamicRoleManager:
    """
    Manages dynamic creation of specialized agents based on project needs
    """

    # Model assignment strategy
    MODEL_ASSIGNMENT = {
        "Planner": "claude-3-5-sonnet",      # Best for architecture
        "Coder": "gpt-4o",                   # Fastest for code generation
        "Tester": "gemini-2.0-flash-exp",    # Fast and cost-effective
        "Reviewer": "claude-3-5-sonnet",     # Most thorough
        "Documenter": "gpt-4o-mini",         # Fast and cheap for docs

        # Dynamic agents
        "SecurityAgent": "claude-3-5-sonnet",  # Critical - best model
        "DevOpsAgent": "gpt-4o",              # Infrastructure expertise
        "FrontendAgent": "gpt-4o",            # UI/UX focus
        "DatabaseAgent": "claude-3-5-sonnet",  # Complex queries
        "PerformanceAgent": "gpt-4o",         # Optimization
        "APIDesignAgent": "claude-3-5-sonnet", # Architecture
    }

    # Fallback chain for each model
    FALLBACK_CHAIN = {
        "claude-3-5-sonnet": ["gpt-4o", "gemini-2.0-flash-exp"],
        "gpt-4o": ["claude-3-5-sonnet", "gemini-2.0-flash-exp"],
        "gemini-2.0-flash-exp": ["gpt-4o", "claude-3-5-sonnet"],
        "gpt-4o-mini": ["gemini-2.0-flash-exp", "gpt-4o"],
    }

    # Role templates
    ROLE_TEMPLATES = {
        "SecurityAgent": RoleDefinition(
            name="SecurityAgent",
            role="Security Specialist",
            goal="Ensure code security, implement authentication, and handle sensitive data properly",
            backstory="""You are a cybersecurity expert with OWASP Top 10 expertise.
                        You specialize in secure authentication, payment processing, and
                        data protection. You never compromise on security best practices.""",
            model="claude-3-5-sonnet",
            temperature=0.2,  # Very focused for security
            triggers=["payment", "authentication", "auth", "stripe", "paypal", "login", "password"],
            priority="HIGH"
        ),

        "DevOpsAgent": RoleDefinition(
            name="DevOpsAgent",
            role="DevOps Engineer",
            goal="Setup infrastructure, CI/CD pipelines, and deployment configurations",
            backstory="""You are a DevOps expert with experience in Docker, Kubernetes, AWS, and CI/CD.
                        You create production-ready infrastructure with monitoring, logging, and scalability.""",
            model="gpt-4o",
            temperature=0.3,
            triggers=["docker", "kubernetes", "aws", "deployment", "ci/cd", "infrastructure", "devops"],
            priority="MEDIUM"
        ),

        "FrontendAgent": RoleDefinition(
            name="FrontendAgent",
            role="Frontend Developer",
            goal="Create beautiful, responsive, and accessible user interfaces",
            backstory="""You are a frontend expert specializing in React, Vue, Next.js, and modern CSS.
                        You build pixel-perfect UIs with excellent UX and accessibility (WCAG compliant).""",
            model="gpt-4o",
            temperature=0.4,  # Slightly creative for UI
            triggers=["frontend", "react", "vue", "nextjs", "ui", "ux", "interface", "dashboard"],
            priority="HIGH"
        ),

        "DatabaseAgent": RoleDefinition(
            name="DatabaseAgent",
            role="Database Specialist",
            goal="Design efficient database schemas, write optimized queries, and ensure data integrity",
            backstory="""You are a database expert with deep knowledge of PostgreSQL, MongoDB, and MySQL.
                        You design normalized schemas, write performant queries, and implement proper indexing.""",
            model="claude-3-5-sonnet",
            temperature=0.2,
            triggers=["database", "schema", "query", "sql", "postgres", "mongodb", "migration"],
            priority="HIGH"
        ),

        "PerformanceAgent": RoleDefinition(
            name="PerformanceAgent",
            role="Performance Engineer",
            goal="Optimize code performance, reduce latency, and improve scalability",
            backstory="""You are a performance optimization expert. You profile code, identify bottlenecks,
                        implement caching strategies, and ensure applications scale efficiently.""",
            model="gpt-4o",
            temperature=0.3,
            triggers=["performance", "optimization", "cache", "scale", "latency", "speed"],
            priority="MEDIUM"
        ),

        "APIDesignAgent": RoleDefinition(
            name="APIDesignAgent",
            role="API Architect",
            goal="Design clean, RESTful APIs with proper versioning and documentation",
            backstory="""You are an API design expert following REST best practices, OpenAPI standards,
                        and proper HTTP semantics. You create developer-friendly APIs.""",
            model="claude-3-5-sonnet",
            temperature=0.3,
            triggers=["api", "rest", "graphql", "endpoint", "swagger", "openapi"],
            priority="HIGH"
        ),
    }

    def __init__(
        self,
        base_agents: Optional[YagoAgents] = None,
        max_dynamic_agents: int = None,  # NO LIMIT by default
        cost_limit: float = None  # NO LIMIT by default
    ):
        """
        Initialize DynamicRoleManager

        Args:
            base_agents: YagoAgents instance (for base 5 agents)
            max_dynamic_agents: Maximum number of dynamic agents (None = unlimited, scales with project)
            cost_limit: Maximum API cost budget (None = unlimited)
        """
        self.base_agents = base_agents or YagoAgents()
        self.max_dynamic_agents = max_dynamic_agents  # Can be None (unlimited)
        self.cost_limit = cost_limit  # Can be None (unlimited)
        self.created_agents: Dict[str, Agent] = {}

    def analyze_requirements(self, clarification_brief: Dict[str, Any]) -> List[str]:
        """
        Analyze project requirements and determine needed roles

        Args:
            clarification_brief: ClarificationBrief dictionary

        Returns:
            List of required dynamic agent names
        """
        required_roles = []

        # Convert brief to lowercase text for keyword matching
        brief_text = str(clarification_brief).lower()

        # Check each role template's triggers
        for role_name, role_def in self.ROLE_TEMPLATES.items():
            for trigger in role_def.triggers:
                if trigger in brief_text:
                    if role_name not in required_roles:
                        required_roles.append(role_name)
                        logger.info(f"✅ {role_name} triggered by keyword: '{trigger}'")
                    break  # One trigger is enough

        # Apply max limit ONLY if specified (None = unlimited)
        if self.max_dynamic_agents is not None and len(required_roles) > self.max_dynamic_agents:
            logger.warning(f"⚠️ Limiting dynamic agents from {len(required_roles)} to {self.max_dynamic_agents}")
            # Prioritize HIGH priority roles
            prioritized = sorted(
                required_roles,
                key=lambda r: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(
                    self.ROLE_TEMPLATES[r].priority, 3
                )
            )
            required_roles = prioritized[:self.max_dynamic_agents]
        else:
            # NO LIMIT - create ALL needed agents
            logger.info(f"✅ No agent limit - creating all {len(required_roles)} required dynamic agents")

        return required_roles

    def create_agent(self, role_name: str, tools: Optional[List[Any]] = None) -> Agent:
        """
        Create a dynamic agent from template

        Args:
            role_name: Name of role to create
            tools: Optional list of tools for the agent

        Returns:
            Configured Agent instance
        """
        if role_name not in self.ROLE_TEMPLATES:
            raise ValueError(f"Unknown role: {role_name}")

        role_def = self.ROLE_TEMPLATES[role_name]

        # Use provided tools or template default
        agent_tools = tools or role_def.tools

        agent = Agent(
            role=role_def.role,
            goal=role_def.goal,
            backstory=role_def.backstory,
            model=role_def.model,
            temperature=role_def.temperature,
            tools=agent_tools,
            verbose=True,
            allow_delegation=False,
        )

        logger.info(f"🤖 Created {role_name} with model {role_def.model}")
        self.created_agents[role_name] = agent

        return agent

    def create_all_required_agents(
        self,
        clarification_brief: Dict[str, Any],
        tools: Optional[Dict[str, List[Any]]] = None
    ) -> Dict[str, Agent]:
        """
        Create all required agents based on clarification brief

        Args:
            clarification_brief: Project clarification brief
            tools: Optional dict mapping role names to tool lists

        Returns:
            Dictionary of created agents
        """
        # Analyze requirements
        required_roles = self.analyze_requirements(clarification_brief)

        logger.info(f"📋 Required dynamic agents: {', '.join(required_roles) if required_roles else 'None'}")

        # Create agents
        agents = {}
        for role_name in required_roles:
            role_tools = tools.get(role_name) if tools else None
            agents[role_name] = self.create_agent(role_name, role_tools)

        return agents

    def get_base_agents(self) -> Dict[str, Agent]:
        """
        Get the 5 base agents (Planner, Coder, Tester, Reviewer, Documenter)

        Returns:
            Dictionary of base agents
        """
        return {
            "Planner": self.base_agents.planner(),
            "Coder": self.base_agents.coder(),
            "Tester": self.base_agents.tester(),
            "Reviewer": self.base_agents.reviewer(),
            "Documenter": self.base_agents.documenter(),
        }

    def get_all_agents(
        self,
        clarification_brief: Dict[str, Any],
        tools: Optional[Dict[str, List[Any]]] = None
    ) -> Dict[str, Agent]:
        """
        Get both base and dynamic agents

        Args:
            clarification_brief: Project clarification brief
            tools: Optional dict of tools per agent

        Returns:
            Complete dictionary of all agents
        """
        # Get base agents
        all_agents = self.get_base_agents()

        # Add dynamic agents
        dynamic_agents = self.create_all_required_agents(clarification_brief, tools)
        all_agents.update(dynamic_agents)

        logger.info(f"🎯 Total agents: {len(all_agents)} (5 base + {len(dynamic_agents)} dynamic)")

        return all_agents

    def get_agent_list(
        self,
        clarification_brief: Dict[str, Any],
        tools: Optional[Dict[str, List[Any]]] = None
    ) -> List[Agent]:
        """
        Get list of all agents (for CrewAI Crew)

        Args:
            clarification_brief: Project clarification brief
            tools: Optional dict of tools per agent

        Returns:
            List of Agent instances
        """
        agents_dict = self.get_all_agents(clarification_brief, tools)
        return list(agents_dict.values())

    def estimate_cost(self, clarification_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate API costs based on required agents and tasks

        Args:
            clarification_brief: Project clarification brief

        Returns:
            Cost estimation dictionary
        """
        required_roles = self.analyze_requirements(clarification_brief)
        num_total_agents = 5 + len(required_roles)  # Base + dynamic

        # Rough cost estimates ($/agent)
        model_costs = {
            "claude-3-5-sonnet": 0.50,
            "gpt-4o": 0.30,
            "gpt-4o-mini": 0.10,
            "gemini-2.0-flash-exp": 0.15,
        }

        total_cost = 0.0
        cost_breakdown = {}

        # Base agents
        for agent_name in ["Planner", "Coder", "Tester", "Reviewer", "Documenter"]:
            model = self.MODEL_ASSIGNMENT.get(agent_name, "gpt-4o")
            cost = model_costs.get(model, 0.25)
            total_cost += cost
            cost_breakdown[agent_name] = {"model": model, "cost": cost}

        # Dynamic agents
        for role_name in required_roles:
            model = self.MODEL_ASSIGNMENT.get(role_name, "gpt-4o")
            cost = model_costs.get(model, 0.25)
            total_cost += cost
            cost_breakdown[role_name] = {"model": model, "cost": cost}

        # Check budget only if limit is set
        within_budget = True if self.cost_limit is None else (total_cost <= self.cost_limit)

        return {
            "total_agents": num_total_agents,
            "base_agents": 5,
            "dynamic_agents": len(required_roles),
            "estimated_cost": f"${total_cost:.2f}",
            "cost_breakdown": cost_breakdown,
            "within_budget": within_budget,
            "cost_limit": self.cost_limit if self.cost_limit else "unlimited",
        }

    def print_summary(self, clarification_brief: Dict[str, Any]):
        """
        Print a summary of agents to be created

        Args:
            clarification_brief: Project clarification brief
        """
        required_roles = self.analyze_requirements(clarification_brief)
        cost_estimate = self.estimate_cost(clarification_brief)

        print("\n" + "=" * 60)
        print("🎯 DYNAMIC ROLE MANAGER SUMMARY")
        print("=" * 60)

        print("\n📊 Base Agents (Always Active):")
        for name in ["Planner", "Coder", "Tester", "Reviewer", "Documenter"]:
            model = self.MODEL_ASSIGNMENT[name]
            print(f"  ✅ {name:<15} → {model}")

        if required_roles:
            print(f"\n🚀 Dynamic Agents (Project-Specific):")
            for role_name in required_roles:
                role_def = self.ROLE_TEMPLATES[role_name]
                print(f"  ✅ {role_name:<15} → {role_def.model} (Priority: {role_def.priority})")
        else:
            print("\n🚀 Dynamic Agents: None required")

        print(f"\n💰 Cost Estimate:")
        print(f"  Total Agents: {cost_estimate['total_agents']}")
        print(f"  Estimated Cost: {cost_estimate['estimated_cost']}")
        print(f"  Budget Status: {'✅ Within budget' if cost_estimate['within_budget'] else '❌ Over budget'}")

        print("=" * 60 + "\n")


def get_dynamic_role_manager(
    base_agents: Optional[YagoAgents] = None,
    max_dynamic_agents: int = 5,
    cost_limit: float = 10.0
) -> DynamicRoleManager:
    """
    Factory function to create DynamicRoleManager

    Args:
        base_agents: YagoAgents instance
        max_dynamic_agents: Maximum dynamic agents
        cost_limit: Cost budget limit

    Returns:
        Configured DynamicRoleManager
    """
    return DynamicRoleManager(
        base_agents=base_agents,
        max_dynamic_agents=max_dynamic_agents,
        cost_limit=cost_limit
    )


# Standalone usage example
if __name__ == "__main__":
    # Example: Analyze an e-commerce project
    example_brief = {
        "clarifications": {
            "tech_stack": {
                "frontend": "Next.js",
                "backend": "FastAPI",
                "database": "PostgreSQL"
            },
            "features": ["payment", "authentication", "admin"],
            "infrastructure": {
                "deployment": "Docker",
                "ci_cd": True
            }
        },
        "user_input": "E-commerce site with Stripe payment and admin dashboard"
    }

    manager = get_dynamic_role_manager()
    manager.print_summary(example_brief)

    # Create agents
    agents = manager.get_all_agents(example_brief)
    print(f"\n✅ Created {len(agents)} agents successfully")
