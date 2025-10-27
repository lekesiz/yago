"""
YAGO v7.0 - Clarification Agent
Gathers detailed project requirements through intelligent questioning
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from crewai import Agent, Task
from pydantic import BaseModel, Field


class ProjectAnalysis(BaseModel):
    """Analysis of user input"""
    project_type: str = Field(description="Detected project type (e-commerce, dashboard, api, etc.)")
    implied_features: List[str] = Field(description="Features inferred from input")
    complexity_estimate: str = Field(description="Complexity level (simple/medium/complex)")
    keywords: List[str] = Field(description="Extracted keywords")


class ClarificationBrief(BaseModel):
    """Complete project brief after clarification"""
    project_id: str
    timestamp: str
    user_input: str
    clarifications: Dict[str, Any]
    auto_generated: Dict[str, Any]


class ClarificationAgent(Agent):
    """
    Specialized agent for gathering comprehensive project requirements
    through intelligent, adaptive questioning.
    """

    # Question templates by category
    BASIC_QUESTIONS = [
        {
            "key": "language",
            "question": "What programming language do you prefer?",
            "options": ["Python", "JavaScript", "TypeScript", "Go", "Other"],
            "default": "Python"
        },
        {
            "key": "frontend",
            "question": "Frontend framework?",
            "options": ["React", "Vue", "Next.js", "Angular", "None"],
            "default": "None"
        },
        {
            "key": "backend",
            "question": "Backend framework?",
            "options": ["FastAPI", "Django", "Express", "Flask", "None"],
            "default": "FastAPI"
        },
        {
            "key": "database",
            "question": "Database?",
            "options": ["PostgreSQL", "MongoDB", "MySQL", "SQLite", "None"],
            "default": "PostgreSQL"
        },
    ]

    ECOMMERCE_QUESTIONS = [
        {
            "key": "payment",
            "question": "Payment gateway?",
            "options": ["Stripe", "PayPal", "Square", "None"],
            "default": "Stripe"
        },
        {
            "key": "inventory",
            "question": "Inventory management needed?",
            "options": ["Yes", "No"],
            "default": "Yes"
        },
        {
            "key": "reviews",
            "question": "Product reviews/ratings?",
            "options": ["Yes", "No"],
            "default": "Yes"
        },
    ]

    DASHBOARD_QUESTIONS = [
        {
            "key": "charts",
            "question": "Chart library?",
            "options": ["Chart.js", "D3.js", "Recharts", "None"],
            "default": "Chart.js"
        },
        {
            "key": "realtime",
            "question": "Real-time updates needed?",
            "options": ["Yes", "No"],
            "default": "No"
        },
    ]

    API_QUESTIONS = [
        {
            "key": "api_style",
            "question": "API style?",
            "options": ["REST", "GraphQL"],
            "default": "REST"
        },
        {
            "key": "auth",
            "question": "Authentication method?",
            "options": ["JWT", "OAuth2", "API Key", "None"],
            "default": "JWT"
        },
        {
            "key": "docs",
            "question": "API documentation?",
            "options": ["Swagger", "Postman", "None"],
            "default": "Swagger"
        },
    ]

    INFRASTRUCTURE_QUESTIONS = [
        {
            "key": "deployment",
            "question": "Deployment target?",
            "options": ["Docker", "AWS", "Vercel", "Heroku", "Local"],
            "default": "Docker"
        },
        {
            "key": "ci_cd",
            "question": "CI/CD pipeline needed?",
            "options": ["Yes", "No"],
            "default": "Yes"
        },
    ]

    QUALITY_QUESTIONS = [
        {
            "key": "test_coverage",
            "question": "Test coverage target?",
            "options": ["60%", "80%", "90%"],
            "default": "80%"
        },
        {
            "key": "documentation",
            "question": "Documentation level?",
            "options": ["Basic", "Standard", "Comprehensive"],
            "default": "Standard"
        },
    ]

    def __init__(self, interactive_mode: bool = True, clarification_depth: str = "full"):
        """
        Initialize ClarificationAgent

        Args:
            interactive_mode: If True, ask questions interactively
            clarification_depth: "full", "minimal", or "auto"
        """
        super().__init__(
            role="Requirements Specialist",
            goal="Gather comprehensive and accurate project specifications through intelligent questioning",
            backstory="""You are an expert requirements analyst with 15+ years of experience.
                        You excel at understanding vague user intentions and translating them
                        into detailed, actionable project specifications. You ask the right
                        questions at the right time, never overwhelming the user while ensuring
                        all critical details are captured.""",
            model="claude-3-5-sonnet",  # Best for reasoning and conversation
            temperature=0.4,  # Focused but adaptive
            verbose=True,
            allow_delegation=False,
        )

        self.interactive_mode = interactive_mode
        self.clarification_depth = clarification_depth
        self.storage_path = Path("workspace/.clarifications")
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def analyze_input(self, user_input: str) -> ProjectAnalysis:
        """
        Analyze user input to detect project type and complexity

        Args:
            user_input: Raw user input

        Returns:
            ProjectAnalysis with detected attributes
        """
        user_lower = user_input.lower()

        # Detect project type
        project_type = "general"
        if any(kw in user_lower for kw in ["ecommerce", "e-commerce", "shop", "store", "cart"]):
            project_type = "e-commerce"
        elif any(kw in user_lower for kw in ["dashboard", "analytics", "chart", "graph", "stats"]):
            project_type = "dashboard"
        elif any(kw in user_lower for kw in ["api", "rest", "endpoint", "backend"]):
            project_type = "api"
        elif any(kw in user_lower for kw in ["web", "website", "site"]):
            project_type = "web"
        elif any(kw in user_lower for kw in ["cli", "command", "tool", "script"]):
            project_type = "cli"

        # Infer features
        implied_features = []
        feature_keywords = {
            "authentication": ["auth", "login", "user", "signup"],
            "payment": ["payment", "stripe", "paypal", "checkout"],
            "database": ["database", "db", "postgres", "mongo"],
            "api": ["api", "rest", "graphql", "endpoint"],
            "admin": ["admin", "dashboard", "panel"],
        }

        for feature, keywords in feature_keywords.items():
            if any(kw in user_lower for kw in keywords):
                implied_features.append(feature)

        # Estimate complexity
        complexity_indicators = len(user_input.split()) + len(implied_features) * 2
        if complexity_indicators < 10:
            complexity = "simple"
        elif complexity_indicators < 25:
            complexity = "medium"
        else:
            complexity = "complex"

        # Extract keywords
        keywords = re.findall(r'\b\w{4,}\b', user_lower)
        keywords = list(set(keywords))[:10]  # Top 10 unique keywords

        return ProjectAnalysis(
            project_type=project_type,
            implied_features=implied_features,
            complexity_estimate=complexity,
            keywords=keywords
        )

    def generate_questions(self, analysis: ProjectAnalysis, mode: str = "full") -> List[Dict]:
        """
        Generate relevant questions based on analysis and mode
        NO LIMITS - generates as many questions as needed for complete technical documentation

        Args:
            analysis: Project analysis
            mode: "full", "minimal", or "auto"

        Returns:
            List of question dictionaries
        """
        questions = []

        # Always include basics
        if mode in ["full", "minimal"]:
            questions.extend(self.BASIC_QUESTIONS)

        # Add project-specific questions (full mode only)
        if mode == "full":
            # ALL relevant questions for project type
            if analysis.project_type == "e-commerce":
                questions.extend(self.ECOMMERCE_QUESTIONS)
            elif analysis.project_type == "dashboard":
                questions.extend(self.DASHBOARD_QUESTIONS)
            elif analysis.project_type == "api":
                questions.extend(self.API_QUESTIONS)

            # ALWAYS add infrastructure for any non-trivial project
            if analysis.complexity_estimate in ["medium", "complex"]:
                questions.extend(self.INFRASTRUCTURE_QUESTIONS)

            # ALWAYS add quality questions
            questions.extend(self.QUALITY_QUESTIONS)

            # For complex projects, add MORE detailed questions
            if analysis.complexity_estimate == "complex":
                questions.extend([
                    {
                        "key": "scalability_target",
                        "question": "Expected scale (users/requests)?",
                        "options": ["<1K", "1K-10K", "10K-100K", "100K-1M", ">1M"],
                        "default": "1K-10K"
                    },
                    {
                        "key": "performance_requirements",
                        "question": "Performance requirements (response time)?",
                        "options": ["<50ms", "<100ms", "<200ms", "<500ms", "No specific"],
                        "default": "<200ms"
                    },
                    {
                        "key": "availability_target",
                        "question": "Availability requirement?",
                        "options": ["99%", "99.9%", "99.99%", "99.999%"],
                        "default": "99.9%"
                    },
                    {
                        "key": "team_size",
                        "question": "Development team size?",
                        "options": ["Solo", "2-3", "4-10", "10+"],
                        "default": "Solo"
                    },
                ])

        elif mode == "minimal":
            # Only essential questions
            questions.extend([
                {
                    "key": "deployment",
                    "question": "Deployment target?",
                    "options": ["Docker", "Local"],
                    "default": "Docker"
                }
            ])

        # NO LIMIT - return ALL generated questions
        return questions

    def ask_question(self, question: Dict) -> str:
        """
        Ask a single question to the user

        Args:
            question: Question dictionary with key, question, options, default

        Returns:
            User's answer
        """
        if not self.interactive_mode:
            # Return default in non-interactive mode
            return question.get("default", "")

        print(f"\n🤖 YAGO: {question['question']}")
        options = question.get("options", [])

        if options:
            for idx, option in enumerate(options, 1):
                print(f"   {idx}. {option}")
            print(f"   {len(options) + 1}. Other (specify)")

        answer = input(">>> Your answer: ").strip()

        # Handle numeric choice
        if answer.isdigit() and options:
            choice = int(answer)
            if 1 <= choice <= len(options):
                return options[choice - 1]
            # "Other" selected, ask for specification
            if choice == len(options) + 1:
                answer = input(">>> Please specify: ").strip()

        # Return answer or default
        return answer if answer else question.get("default", "")

    def conduct_interview(self, questions: List[Dict]) -> Dict[str, str]:
        """
        Conduct full interview with user

        Args:
            questions: List of questions to ask

        Returns:
            Dictionary of answers keyed by question key
        """
        answers = {}

        print("\n" + "=" * 60)
        print("🎯 YAGO v7.0 - Project Clarification")
        print("=" * 60)
        print("Let's clarify your project requirements.")
        print(f"I'll ask you {len(questions)} questions. Press Enter for defaults.")
        print("-" * 60)

        for idx, question in enumerate(questions, 1):
            print(f"\n[{idx}/{len(questions)}]")
            answer = self.ask_question(question)
            answers[question["key"]] = answer

        print("\n" + "=" * 60)
        print("✅ Clarification complete! Generating brief...")
        print("=" * 60 + "\n")

        return answers

    def generate_brief(
        self,
        user_input: str,
        analysis: ProjectAnalysis,
        answers: Dict[str, str]
    ) -> ClarificationBrief:
        """
        Generate comprehensive project brief from answers

        Args:
            user_input: Original user input
            analysis: Project analysis
            answers: User answers

        Returns:
            Complete ClarificationBrief
        """
        project_id = f"{analysis.project_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Structure clarifications
        clarifications = {
            "tech_stack": {
                "language": answers.get("language", "Python"),
                "frontend": answers.get("frontend", "None"),
                "backend": answers.get("backend", "FastAPI"),
                "database": answers.get("database", "PostgreSQL"),
            },
            "features": analysis.implied_features,
            "infrastructure": {
                "deployment": answers.get("deployment", "Docker"),
                "ci_cd": answers.get("ci_cd", "Yes") == "Yes",
            },
            "quality": {
                "test_coverage": answers.get("test_coverage", "80%"),
                "documentation": answers.get("documentation", "Standard"),
            }
        }

        # Add project-specific details
        if analysis.project_type == "e-commerce":
            clarifications["payment"] = answers.get("payment", "None")
            clarifications["inventory"] = answers.get("inventory", "No") == "Yes"

        # Determine required agents
        required_agents = ["Planner", "Coder", "Tester", "Reviewer", "Documenter"]

        if answers.get("payment") and answers["payment"] != "None":
            required_agents.append("SecurityAgent")

        if answers.get("deployment") in ["Docker", "AWS"]:
            required_agents.append("DevOpsAgent")

        if answers.get("frontend") != "None":
            required_agents.append("FrontendAgent")

        # Generate TODO list
        todo_list = self.generate_todo_list(clarifications, required_agents)

        # Estimate costs and duration
        estimated_cost = len(todo_list) * 0.25  # $0.25 per task (rough estimate)
        estimated_duration = len(todo_list) * 5  # 5 minutes per task

        brief = ClarificationBrief(
            project_id=project_id,
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            clarifications=clarifications,
            auto_generated={
                "required_agents": required_agents,
                "todo_list": todo_list,
                "estimated_total_cost": f"${estimated_cost:.2f}",
                "estimated_duration": f"{estimated_duration} minutes"
            }
        )

        return brief

    def generate_todo_list(self, clarifications: Dict, agents: List[str]) -> List[Dict]:
        """
        Generate TODO list from clarifications

        Args:
            clarifications: Project clarifications
            agents: Required agents

        Returns:
            List of TODO items
        """
        todos = [
            {"task": "Setup project structure", "agent": "Planner", "priority": "HIGH"},
            {"task": "Create database schema", "agent": "Coder", "priority": "HIGH"},
        ]

        # Add conditional tasks
        if clarifications.get("payment"):
            todos.append({
                "task": f"Integrate {clarifications['payment']} payment",
                "agent": "SecurityAgent",
                "priority": "HIGH"
            })

        if clarifications["tech_stack"].get("frontend") != "None":
            todos.append({
                "task": f"Create {clarifications['tech_stack']['frontend']} frontend",
                "agent": "Coder",
                "priority": "MEDIUM"
            })

        if clarifications["infrastructure"].get("deployment") == "Docker":
            todos.append({
                "task": "Create Docker configuration",
                "agent": "DevOpsAgent",
                "priority": "MEDIUM"
            })

        # Always add testing and docs
        todos.extend([
            {"task": "Write comprehensive tests", "agent": "Tester", "priority": "HIGH"},
            {"task": "Create documentation", "agent": "Documenter", "priority": "MEDIUM"},
        ])

        return todos

    def save_brief(self, brief: ClarificationBrief) -> Path:
        """
        Save brief to JSON file

        Args:
            brief: ClarificationBrief to save

        Returns:
            Path to saved file
        """
        file_path = self.storage_path / f"{brief.project_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(brief.dict(), f, indent=2, ensure_ascii=False)

        print(f"💾 Brief saved: {file_path}")
        return file_path

    def load_brief(self, project_id: str) -> Optional[ClarificationBrief]:
        """
        Load existing brief from storage

        Args:
            project_id: Project ID

        Returns:
            ClarificationBrief if found, None otherwise
        """
        file_path = self.storage_path / f"{project_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return ClarificationBrief(**data)

    def clarify_requirements(
        self,
        user_input: str,
        mode: str = None
    ) -> ClarificationBrief:
        """
        Main entry point: Clarify requirements from user input

        Args:
            user_input: User's project idea
            mode: Override clarification depth ("full", "minimal", "auto")

        Returns:
            Complete ClarificationBrief
        """
        mode = mode or self.clarification_depth

        print(f"\n🔍 Analyzing input: '{user_input}'")

        # Step 1: Analyze input
        analysis = self.analyze_input(user_input)
        print(f"📊 Detected: {analysis.project_type} project ({analysis.complexity_estimate} complexity)")

        # Step 2: Generate questions
        questions = self.generate_questions(analysis, mode)

        # Step 3: Conduct interview (or use defaults)
        if mode == "auto":
            # Auto mode: use all defaults
            answers = {q["key"]: q.get("default", "") for q in questions}
            print("🤖 Auto mode: Using inferred defaults")
        else:
            answers = self.conduct_interview(questions)

        # Step 4: Generate brief
        brief = self.generate_brief(user_input, analysis, answers)

        # Step 5: Save brief
        self.save_brief(brief)

        return brief

    def print_brief_summary(self, brief: ClarificationBrief):
        """
        Print human-readable brief summary

        Args:
            brief: ClarificationBrief to print
        """
        print("\n" + "=" * 60)
        print("📋 PROJECT BRIEF SUMMARY")
        print("=" * 60)
        print(f"Project ID: {brief.project_id}")
        print(f"Original Input: {brief.user_input}")
        print()
        print("Tech Stack:")
        for key, value in brief.clarifications["tech_stack"].items():
            print(f"  - {key.capitalize()}: {value}")
        print()
        print(f"Required Agents: {', '.join(brief.auto_generated['required_agents'])}")
        print(f"TODO Items: {len(brief.auto_generated['todo_list'])}")
        print(f"Estimated Cost: {brief.auto_generated['estimated_total_cost']}")
        print(f"Estimated Duration: {brief.auto_generated['estimated_duration']}")
        print("=" * 60 + "\n")


def get_clarification_agent(
    interactive: bool = True,
    depth: str = "full"
) -> ClarificationAgent:
    """
    Factory function to create ClarificationAgent

    Args:
        interactive: Enable interactive mode
        depth: Clarification depth ("full", "minimal", "auto")

    Returns:
        Configured ClarificationAgent
    """
    return ClarificationAgent(interactive_mode=interactive, clarification_depth=depth)


# Standalone usage example
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python clarification_agent.py 'Your project idea'")
        sys.exit(1)

    user_idea = " ".join(sys.argv[1:])

    agent = get_clarification_agent(interactive=True, depth="full")
    brief = agent.clarify_requirements(user_idea)
    agent.print_brief_summary(brief)
