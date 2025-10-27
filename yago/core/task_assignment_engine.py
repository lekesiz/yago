"""
YAGO v7.0 - Task Assignment Engine
Intelligently routes tasks to the most suitable agents (base or dynamic)
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from crewai import Task, Agent

logger = logging.getLogger("YAGO.TaskAssignment")


@dataclass
class TaskDefinition:
    """Definition for a task"""
    title: str
    description: str
    expected_output: str
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    keywords: List[str] = None
    dependencies: List[str] = None  # Task titles this depends on


class TaskAssignmentEngine:
    """
    Intelligently assigns tasks to the most suitable agents
    based on task requirements and agent capabilities
    """

    # Task type → Agent role mapping
    TASK_ROUTING_RULES = {
        # Security-related tasks
        "security": ["SecurityAgent", "Reviewer", "Coder"],
        "authentication": ["SecurityAgent", "Coder"],
        "authorization": ["SecurityAgent", "Coder"],
        "encryption": ["SecurityAgent", "Coder"],
        "payment": ["SecurityAgent", "Coder"],
        "oauth": ["SecurityAgent", "Coder"],

        # DevOps-related tasks
        "docker": ["DevOpsAgent", "Coder"],
        "kubernetes": ["DevOpsAgent", "Coder"],
        "deployment": ["DevOpsAgent", "Coder"],
        "ci/cd": ["DevOpsAgent", "Coder"],
        "infrastructure": ["DevOpsAgent", "Coder"],
        "monitoring": ["DevOpsAgent", "Coder"],

        # Database-related tasks
        "database": ["DatabaseAgent", "Coder"],
        "schema": ["DatabaseAgent", "Coder"],
        "migration": ["DatabaseAgent", "Coder"],
        "query": ["DatabaseAgent", "Coder"],
        "optimization": ["PerformanceAgent", "DatabaseAgent", "Coder"],

        # Frontend-related tasks
        "ui": ["FrontendAgent", "Coder"],
        "ux": ["FrontendAgent", "Coder"],
        "component": ["FrontendAgent", "Coder"],
        "frontend": ["FrontendAgent", "Coder"],
        "dashboard": ["FrontendAgent", "Coder"],
        "react": ["FrontendAgent", "Coder"],
        "vue": ["FrontendAgent", "Coder"],

        # API-related tasks
        "api": ["APIDesignAgent", "Coder"],
        "endpoint": ["APIDesignAgent", "Coder"],
        "rest": ["APIDesignAgent", "Coder"],
        "graphql": ["APIDesignAgent", "Coder"],

        # Performance-related tasks
        "performance": ["PerformanceAgent", "Coder"],
        "caching": ["PerformanceAgent", "Coder"],
        "scaling": ["PerformanceAgent", "DevOpsAgent", "Coder"],

        # Testing-related tasks
        "test": ["Tester"],
        "testing": ["Tester"],
        "unittest": ["Tester"],
        "integration": ["Tester"],

        # Review-related tasks
        "review": ["Reviewer"],
        "audit": ["SecurityAgent", "Reviewer"],
        "quality": ["Reviewer"],

        # Documentation-related tasks
        "documentation": ["Documenter"],
        "docs": ["Documenter"],
        "readme": ["Documenter"],
    }

    def __init__(self, agents: Dict[str, Agent], todos: List[Dict[str, Any]] = None):
        """
        Initialize TaskAssignmentEngine

        Args:
            agents: Dictionary of available agents {"role_name": Agent}
            todos: Optional list of TODO items from clarification
        """
        self.agents = agents
        self.todos = todos or []
        self.assigned_tasks: List[Task] = []

    def find_best_agent(self, task_def: TaskDefinition) -> Agent:
        """
        Find the best agent for a task based on keywords and routing rules

        Args:
            task_def: Task definition

        Returns:
            Best matching Agent
        """
        # Extract keywords from task title and description
        task_text = f"{task_def.title} {task_def.description}".lower()
        task_keywords = set(task_text.split())

        best_match = None
        best_score = 0

        # Check each routing rule
        for keyword, preferred_agents in self.TASK_ROUTING_RULES.items():
            if keyword in task_text:
                # Found a matching keyword, check if preferred agents exist
                for agent_role in preferred_agents:
                    if agent_role in self.agents:
                        # Agent exists, calculate score
                        score = 10  # Base score for keyword match

                        # Bonus if it's the first preference
                        if agent_role == preferred_agents[0]:
                            score += 5

                        # Bonus for HIGH priority agent roles
                        if agent_role in ["SecurityAgent", "Planner", "Coder"]:
                            score += 3

                        if score > best_score:
                            best_score = score
                            best_match = self.agents[agent_role]
                            logger.debug(f"Task '{task_def.title[:30]}...' matched '{agent_role}' (score: {score})")

        # Fallback: Use Coder if no specific match
        if best_match is None:
            best_match = self.agents.get("Coder")
            logger.debug(f"Task '{task_def.title[:30]}...' fallback to Coder")

        return best_match

    def create_task_from_todo(self, todo: Dict[str, Any]) -> TaskDefinition:
        """
        Convert TODO item to TaskDefinition

        Args:
            todo: TODO dictionary from clarification

        Returns:
            TaskDefinition
        """
        return TaskDefinition(
            title=todo.get("task", todo.get("title", "Untitled Task")),
            description=todo.get("description", todo.get("task", "")),
            expected_output=todo.get("expected_output", "Completed implementation"),
            priority=todo.get("priority", "MEDIUM"),
            keywords=todo.get("keywords", []),
            dependencies=todo.get("dependencies", [])
        )

    def create_crewai_task(self, task_def: TaskDefinition, agent: Agent) -> Task:
        """
        Create CrewAI Task from TaskDefinition

        Args:
            task_def: Task definition
            agent: Assigned agent

        Returns:
            CrewAI Task
        """
        return Task(
            description=f"{task_def.title}\n\n{task_def.description}",
            expected_output=task_def.expected_output,
            agent=agent,
        )

    def assign_all_tasks(self) -> List[Task]:
        """
        Assign all TODO items to appropriate agents

        Returns:
            List of CrewAI Tasks with agents assigned
        """
        tasks = []

        logger.info(f"📋 Assigning {len(self.todos)} tasks to agents...")

        for idx, todo in enumerate(self.todos, 1):
            # Convert TODO to TaskDefinition
            task_def = self.create_task_from_todo(todo)

            # Find best agent
            agent = self.find_best_agent(task_def)

            # Create CrewAI task
            task = self.create_crewai_task(task_def, agent)
            tasks.append(task)

            logger.info(f"  [{idx}/{len(self.todos)}] '{task_def.title[:40]}...' → {agent.role}")

        self.assigned_tasks = tasks
        return tasks

    def get_execution_strategy(self) -> str:
        """
        Determine optimal execution strategy based on task dependencies and agent count

        Returns:
            "sequential", "parallel", or "hybrid"
        """
        total_agents = len(self.agents)
        dynamic_count = sum(1 for role in self.agents.keys()
                           if role not in ["Planner", "Coder", "Tester", "Reviewer", "Documenter"])

        # Check if tasks have dependencies
        has_dependencies = any(
            self.create_task_from_todo(todo).dependencies
            for todo in self.todos if todo
        )

        if has_dependencies:
            return "sequential"  # Must respect dependencies
        elif dynamic_count == 0:
            return "parallel"  # Base agents can run in parallel
        elif dynamic_count <= 3:
            return "hybrid"  # Mix of parallel and sequential
        else:
            return "sequential"  # Too many agents, safer to run sequential

    def get_task_groups(self) -> Dict[str, List[Task]]:
        """
        Group tasks by execution phase for parallel execution

        Returns:
            Dictionary mapping phase to tasks
        """
        groups = {
            "planning": [],
            "coding": [],
            "quality": [],  # Testing + Review (parallel)
            "documentation": [],
        }

        for task in self.assigned_tasks:
            agent_role = task.agent.role

            if agent_role == "Planner":
                groups["planning"].append(task)
            elif agent_role in ["Coder", "SecurityAgent", "DevOpsAgent", "DatabaseAgent",
                               "FrontendAgent", "APIDesignAgent", "PerformanceAgent"]:
                groups["coding"].append(task)
            elif agent_role in ["Tester", "Reviewer"]:
                groups["quality"].append(task)
            elif agent_role == "Documenter":
                groups["documentation"].append(task)

        return groups

    def print_assignment_summary(self):
        """Print summary of task assignments"""
        print("\n" + "=" * 60)
        print("📋 TASK ASSIGNMENT SUMMARY")
        print("=" * 60)

        # Count tasks per agent
        agent_task_count = {}
        for task in self.assigned_tasks:
            role = task.agent.role
            agent_task_count[role] = agent_task_count.get(role, 0) + 1

        print(f"\nTotal Tasks: {len(self.assigned_tasks)}")
        print(f"\nTasks per Agent:")
        for role, count in sorted(agent_task_count.items(), key=lambda x: -x[1]):
            print(f"  {role:<20} → {count} tasks")

        strategy = self.get_execution_strategy()
        print(f"\nRecommended Strategy: {strategy.upper()}")

        groups = self.get_task_groups()
        print(f"\nExecution Phases:")
        for phase, tasks in groups.items():
            if tasks:
                print(f"  {phase.capitalize():<15} → {len(tasks)} tasks")

        print("=" * 60 + "\n")


def get_task_assignment_engine(
    agents: Dict[str, Agent],
    todos: List[Dict[str, Any]] = None
) -> TaskAssignmentEngine:
    """
    Factory function to create TaskAssignmentEngine

    Args:
        agents: Available agents
        todos: TODO list

    Returns:
        Configured TaskAssignmentEngine
    """
    return TaskAssignmentEngine(agents=agents, todos=todos)


# Standalone usage example
if __name__ == "__main__":
    # Mock example
    from unittest.mock import Mock

    # Mock agents
    mock_agents = {
        "Planner": Mock(role="Planner"),
        "Coder": Mock(role="Coder"),
        "SecurityAgent": Mock(role="SecurityAgent"),
        "DevOpsAgent": Mock(role="DevOpsAgent"),
        "Tester": Mock(role="Tester"),
    }

    # Example TODO list
    todos = [
        {"task": "Design system architecture", "priority": "HIGH"},
        {"task": "Implement authentication with JWT", "priority": "HIGH"},
        {"task": "Setup Docker configuration", "priority": "MEDIUM"},
        {"task": "Create database schema", "priority": "HIGH"},
        {"task": "Write unit tests", "priority": "MEDIUM"},
        {"task": "Security audit", "priority": "HIGH"},
    ]

    # Create engine
    engine = TaskAssignmentEngine(agents=mock_agents, todos=todos)

    # Assign tasks
    tasks = engine.assign_all_tasks()

    # Print summary
    engine.print_assignment_summary()

    print("\n✅ Task assignment example complete")
