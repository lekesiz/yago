# YAGO v7.0 - Etap Etap İmplementasyon Promptları

## 📋 Kullanım Talimatı
Her promptu **sırayla** AI'ya veya geliştirici ekibine iletz. Bir etap tamamlanınca bir sonrakine geç.

---

# ⚡ ETAP 1: CLARIFICATION MODULE (1-2 hafta)

## Prompt 1.1: ClarificationAgent Tasarımı

```
Sen YAGO (Yerel AI Geliştirme Orkestratörü) projesi geliştiriyor. 
YAGO v7.0'da yeni bir Clarification Module eklemeyi hedefliyoruz.

GÖREV: Yeni bir ClarificationAgent class'ı tasarla ve kodla.

GEREKSİNİMLER:
1. Agent Yapısı:
   - CrewAI Agent sınıfından extends et
   - role="Requirements Specialist"
   - goal="Gather detailed project requirements from user"
   - backstory="Expert at understanding user intent and eliminating ambiguity"

2. Sorular Sistemi:
   Hazır soru setleri oluştur (proje tiplerine göre):
   
   a) WEB_PROJECT sorular:
      - Frontend framework? (Next.js, React, Vue)
      - Backend framework? (FastAPI, Django, Node.js)
      - Database? (PostgreSQL, MongoDB, SQLite)
      - Authentication? (JWT, OAuth2, Sessions)
      - Deployment? (Docker, AWS, Vercel)
      - Payment needed? (Stripe, PayPal, None)
      - Admin panel? (Yes/No)
   
   b) CLI_PROJECT sorular:
      - Primary language? (Python, Go, Rust)
      - Main purpose? (Tool, Automation, Data processing)
      - Database needed? (Yes/No, if yes: type)
      - Config file format? (YAML, JSON, TOML)
   
   c) DATA_PROJECT sorular:
      - Data source? (CSV, API, Database, Files)
      - Analysis type? (Visualization, Statistics, ML)
      - Output format? (Dashboard, Report, API)
      - Scale? (< 1GB, 1-100GB, > 100GB)

3. JSON Çıktı Format (Örnek):
   {
     "project_id": "ecommerce_001",
     "project_type": "WEB_PROJECT",
     "timestamp": "2025-10-27T14:30:00Z",
     "clarifications": {
       "framework": {
         "frontend": "Next.js",
         "backend": "FastAPI",
         "database": "PostgreSQL"
       },
       "features": {
         "payment": "Stripe",
         "authentication": "JWT",
         "admin_panel": true
       },
       "deployment": "Docker",
       "constraints": {
         "budget": "unlimited",
         "timeline": "flexible",
         "team_size": 1
       }
     },
     "raw_responses": [
       { "question": "Frontend framework?", "answer": "Next.js" },
       ...
     ],
     "confidence_score": 0.95
   }

4. Tools:
   - ask_user() → Interactive sorular sor
   - validate_answer() → Cevabı valide et
   - suggest_defaults() → Eğer cevap yoksa default öner

5. Çıktılar:
   - File: workspace/.clarifications/{project_id}.json
   - Brief: workplace/docs/CLARIFICATION_{project_id}.md

KOD ÖRNEĞİ BAŞLANGIÇ:
```python
from crewai import Agent, Task
from typing import Dict, List
import json
from datetime import datetime

class ClarificationAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Requirements Specialist",
            goal="Gather detailed project requirements",
            backstory="Expert at understanding user intent",
            model="claude-3-5-sonnet",
            allow_delegation=False,
        )
        
        self.question_sets = {
            "WEB_PROJECT": [...],  # Sorular
            "CLI_PROJECT": [...],
            "DATA_PROJECT": [...],
        }
    
    def ask_project_type(self):
        """Önce proje tipini sordur"""
        # Interactive sorular
        pass
    
    def ask_questions_for_type(self, project_type: str) -> Dict:
        """Proje tipine göre soruları sor"""
        pass
    
    def generate_brief(self, responses: Dict) -> str:
        """Cevaplardan markdown brief oluştur"""
        pass
    
    def save_clarifications(self, project_id: str, data: Dict):
        """JSON'a kaydet"""
        pass
```

BEKLENEN ÇIKILAR:
1. agents/clarification_agent.py (tam kod)
2. docs/CLARIFICATION_QUESTIONS.json (soru template'leri)
3. Example output: workspace/.clarifications/sample_001.json
4. Brief example: workspace/docs/CLARIFICATION_sample_001.md

BAŞARILI KABUL KRİTERLERİ:
✅ Agent interaktif soru soruyor
✅ Cevaplar JSON'a kaydediliyor
✅ Markdown brief oluşturuluyor
✅ project_type otomatik detect ediliyor
✅ Confidence score hesaplanıyor
```

## Prompt 1.2: Interactive Mode Entegrasyonu

```
GÖREV: ClarificationAgent'i mevcut interactive mode (-i parametresi) ile entegre et.

BAĞLAM: YAGO'da zaten --interactive / -i parametresi var.
Bu etapta clarification'ı bu moda entegre et.

İMPLEMENTASYON:

1. main.py'de yeni flow ekle:
```python
# main.py
import argparse
from agents.clarification_agent import ClarificationAgent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", help="Project idea")
    parser.add_argument("-i", "--interactive", action="store_true")
    parser.add_argument("--skip-clarification", action="store_true")
    parser.add_argument(
        "--clarification-depth", 
        choices=["full", "minimal", "none"],
        default="full"
    )
    
    args = parser.parse_args()
    
    # YENI: Clarification Phase
    if not args.skip_clarification:
        clarification_agent = ClarificationAgent()
        
        if args.clarification_depth == "full":
            clarifications = clarification_agent.run_interactive()
        elif args.clarification_depth == "minimal":
            clarifications = clarification_agent.run_quick()
        else:
            clarifications = {}
        
        # Clarifications'ı context'e ekle
        brief = clarifications.get("brief", "")
        
    # MEVCUT: Planner Phase
    # ... rest of code
```

2. utils/interactive_tools.py genişlet:
```python
def clarification_interactive_loop(project_idea: str):
    """
    Clarification interactive loop
    Returns: Dict with clarifications
    """
    pass

def display_clarification_summary(clarifications: Dict):
    """Display formatted summary to user"""
    pass

def ask_confirm_clarifications(clarifications: Dict) -> bool:
    """Kullanıcıya: These clarifications correct? Y/N"""
    pass
```

3. Test: 
```bash
# Full clarification
python main.py --idea "E-commerce site" --interactive

# Skip clarification
python main.py --idea "E-commerce site" --skip-clarification

# Minimal clarification
python main.py --idea "E-commerce site" --clarification-depth minimal
```

BAŞARILI KABUL KRİTERLERİ:
✅ --interactive flag ile clarification çalışıyor
✅ --skip-clarification ile bypass ediliyor
✅ --clarification-depth working
✅ Clarifications otomatik Planner'a iletiliyor
```

## Prompt 1.3: Brief Generation & TODO List

```
GÖREV: Clarifications'dan otomatik olarak:
1. Markdown Brief oluştur
2. TODO list generate et
3. Task Queue'ye ekle

DETAYLAR:

1. Brief Template (Markdown):
```markdown
# Project Brief: {project_name}

## Overview
{brief_description}

## Tech Stack
- Frontend: {frontend}
- Backend: {backend}
- Database: {database}
- Deployment: {deployment}

## Features
{feature_list}

## Requirements
- Budget: {budget}
- Timeline: {timeline}
- Team Size: {team_size}

## TODO List
{auto_generated_todos}

## Success Criteria
{auto_generated_criteria}
```

2. TODO List Auto-Generation:
Clarifications'dan bak:
- Eğer payment gerekli → "Implement payment integration" task'ı ekle
- Eğer authentication → "Setup authentication system" task'ı ekle
- Eğer deployment Docker → "Create Dockerfile and CI/CD" task'ı ekle
- vb...

3. Implementation:
```python
# utils/brief_generator.py
class BriefGenerator:
    def __init__(self, clarifications: Dict):
        self.clarifications = clarifications
    
    def generate_brief(self) -> str:
        """Markdown brief oluştur"""
        pass
    
    def generate_todo_list(self) -> List[Dict]:
        """
        Returns:
        [
          {"title": "Setup project structure", "priority": "HIGH"},
          {"title": "Create database schema", "priority": "HIGH"},
          ...
        ]
        """
        pass
    
    def save_files(self, project_id: str):
        """Brief ve TODO'yu file'lara kaydet"""
        pass

# tasks/task_queue.py
class DynamicTaskQueue:
    def __init__(self):
        self.tasks = []
    
    def add_from_todo_list(self, todo_list: List[Dict]):
        """TODO list'ten task'lar ekle"""
        pass
```

BAŞARILI KABUL KRİTERLERİ:
✅ Markdown brief oluşturuluyor
✅ TODO list auto-generated
✅ Task Queue'ye entegre ediliyor
✅ workspace/docs/{project_id}_brief.md dosyası oluşturuluyor
```

## Prompt 1.4: Etap 1 Test & Validation

```
GÖREV: Etap 1'in (Clarification Module) tam test coverage'ını yaz.

TEST CASES:

1. test_clarification_agent.py:
```python
import pytest
from agents.clarification_agent import ClarificationAgent

class TestClarificationAgent:
    
    def test_web_project_questions(self):
        """Web project için doğru soruların sorulduğunu test et"""
        agent = ClarificationAgent()
        questions = agent.get_questions_for_type("WEB_PROJECT")
        
        assert "Frontend framework?" in questions
        assert "Backend framework?" in questions
        assert "Database?" in questions
    
    def test_cli_project_questions(self):
        """CLI project için doğru soruların sorulduğunu test et"""
        agent = ClarificationAgent()
        questions = agent.get_questions_for_type("CLI_PROJECT")
        
        assert len(questions) > 0
        assert "Primary language?" in questions
    
    def test_json_output_format(self):
        """JSON çıktı formatının doğru olduğunu test et"""
        agent = ClarificationAgent()
        
        sample_responses = {
            "project_type": "WEB_PROJECT",
            "frontend": "Next.js",
            "backend": "FastAPI",
        }
        
        output = agent.generate_json(sample_responses)
        
        assert "project_id" in output
        assert "timestamp" in output
        assert "clarifications" in output
        assert "confidence_score" in output
    
    def test_brief_generation(self):
        """Brief'in Markdown formatında oluşturulduğunu test et"""
        agent = ClarificationAgent()
        
        clarifications = {
            "framework": {"frontend": "React"},
            "features": {"payment": "Stripe"},
        }
        
        brief = agent.generate_brief(clarifications)
        
        assert "# Project Brief" in brief
        assert "Tech Stack" in brief
        assert "React" in brief
        assert "Stripe" in brief

2. test_todo_generation.py:
```python
from utils.brief_generator import BriefGenerator

class TestTODOGeneration:
    
    def test_payment_triggers_todo(self):
        """Payment feature TODO oluşturması test et"""
        clarifications = {
            "features": {"payment": "Stripe"},
        }
        
        generator = BriefGenerator(clarifications)
        todos = generator.generate_todo_list()
        
        payment_todos = [t for t in todos if "payment" in t["title"].lower()]
        assert len(payment_todos) > 0
    
    def test_docker_triggers_devops_todo(self):
        """Docker deployment DevOps TODO'ları test et"""
        clarifications = {
            "deployment": "Docker",
        }
        
        generator = BriefGenerator(clarifications)
        todos = generator.generate_todo_list()
        
        devops_todos = [t for t in todos if "docker" in t["title"].lower()]
        assert len(devops_todos) > 0
    
    def test_todo_priority_assignment(self):
        """TODO'ların priority'si doğru atanıyor mu?"""
        clarifications = {
            "features": {"payment": "Stripe", "auth": "JWT"},
        }
        
        generator = BriefGenerator(clarifications)
        todos = generator.generate_todo_list()
        
        # Foundation tasks HIGH priority olmalı
        foundation = [t for t in todos if t["priority"] == "HIGH"]
        assert len(foundation) > 0

3. test_integration.py:
```python
class TestClarificationIntegration:
    
    def test_full_flow_web_project(self):
        """
        Tam flow test:
        1. Kullanıcı --idea versin
        2. ClarificationAgent sorular soruyor
        3. JSON kaydediliyor
        4. Brief oluşturuluyor
        5. TODO list oluşturuluyor
        """
        
        test_responses = {
            "project_name": "My E-Commerce",
            "project_type": "WEB_PROJECT",
            "frontend": "Next.js",
            "backend": "FastAPI",
            "database": "PostgreSQL",
            "payment": "Stripe",
        }
        
        # 1. JSON
        json_output = generate_clarification_json(test_responses)
        assert json_output["project_type"] == "WEB_PROJECT"
        
        # 2. Brief
        brief = generate_brief(json_output)
        assert "Next.js" in brief
        assert "FastAPI" in brief
        
        # 3. TODO
        todos = generate_todos(json_output)
        assert len(todos) > 5
        assert any("Stripe" in t["title"] for t in todos)

EXPECTED TEST RESULTS:
✅ 15+ tests passing
✅ 100% code coverage for clarification_agent.py
✅ Integration tests passing
```

---

# ⚡ ETAP 2: DYNAMIC ROLES SYSTEM (3-4 hafta)

## Prompt 2.1: DynamicRoleManager Tasarımı

```
GÖREV: YAGO'ya Dynamic Role Management sistemi ekle.

BAĞLAM:
- Etap 1'de clarifications JSON'da
- Etap 2'de buna göre dinamik roller oluşturacağız
- Mevcut 5 agent var (Planner, Coder, Tester, Reviewer, Documenter)
- Bunlara ihtiyaca göre extra agentz ekleyeceğiz

DETAYLAR:

1. Rol Türleri ve Koşulları:

```python
# agents/dynamic_roles.py

ROLE_RULES = {
    "SecurityAgent": {
        "triggers": ["payment", "authentication", "oauth"],
        "skills": ["security", "encryption", "compliance"],
        "model": "claude-3-5-sonnet",
        "priority": "HIGH",
        "description": "Security audit and encryption implementation",
    },
    
    "DevOpsAgent": {
        "triggers": ["docker", "kubernetes", "aws", "deployment", "ci/cd"],
        "skills": ["devops", "infrastructure", "deployment"],
        "model": "gpt-4o",
        "priority": "MEDIUM",
        "description": "Infrastructure and deployment configuration",
    },
    
    "UIUXAgent": {
        "triggers": ["frontend", "ui/ux", "design", "dashboard"],
        "skills": ["ui", "ux", "design", "frontend"],
        "model": "claude-3-5-sonnet",
        "priority": "MEDIUM",
        "description": "UI/UX design and component creation",
    },
    
    "DatabaseArchitectAgent": {
        "triggers": ["database", "schema", "migration", "orm"],
        "skills": ["database", "sql", "orm", "architecture"],
        "model": "gpt-4o",
        "priority": "HIGH",
        "description": "Database design and optimization",
    },
    
    "PerformanceAgent": {
        "triggers": ["optimization", "performance", "caching", "scaling"],
        "skills": ["performance", "caching", "optimization"],
        "model": "gpt-4o",
        "priority": "LOW",
        "description": "Performance optimization and monitoring",
    },
}
```

2. DynamicRoleManager Class:

```python
# agents/dynamic_role_manager.py

from typing import Dict, List
from crewai import Agent
import json

class DynamicRoleManager:
    def __init__(self, clarifications: Dict):
        self.clarifications = clarifications
        self.base_agents = self._initialize_base_agents()
        self.dynamic_agents = []
    
    def _initialize_base_agents(self) -> List[Agent]:
        """
        Mevcut 5 ajanı initialize et
        Returns: [PlannerAgent, CoderAgent, TesterAgent, ReviewerAgent, DocumenterAgent]
        """
        pass
    
    def analyze_requirements(self) -> List[str]:
        """
        Clarifications'dan gerekli rol türlerini belirle
        
        Args: clarifications Dict
        Returns: ["SecurityAgent", "DevOpsAgent", ...]
        """
        required_roles = []
        
        # Trigger-based role detection
        for role_name, role_config in ROLE_RULES.items():
            triggers = role_config["triggers"]
            
            # Clarifications'da trigger var mı?
            if self._matches_triggers(triggers):
                required_roles.append(role_name)
        
        return required_roles
    
    def _matches_triggers(self, triggers: List[str]) -> bool:
        """
        Clarifications'da trigger kelimeleri var mı kontrol et
        """
        clarification_text = json.dumps(self.clarifications).lower()
        return any(trigger.lower() in clarification_text for trigger in triggers)
    
    def create_dynamic_agents(self) -> List[Agent]:
        """
        Gerekli role göre Agent'ler oluştur
        Returns: [SecurityAgent(), DevOpsAgent(), ...]
        """
        required_roles = self.analyze_requirements()
        
        for role_name in required_roles[:5]:  # Max 5 dynamic agent (cost control)
            agent = self._create_agent_for_role(role_name)
            self.dynamic_agents.append(agent)
        
        return self.dynamic_agents
    
    def _create_agent_for_role(self, role_name: str) -> Agent:
        """Spesifik role için Agent'i oluştur"""
        
        config = ROLE_RULES[role_name]
        
        agent = Agent(
            role=role_name,
            goal=config["description"],
            backstory=f"Expert {role_name} with deep knowledge",
            model=config["model"],
            allow_delegation=False,
            verbose=True,
        )
        
        return agent
    
    def get_all_agents(self) -> Dict[str, List[Agent]]:
        """
        Base agents + dynamic agents'ı döndür
        
        Returns:
        {
            "base": [PlannerAgent, CoderAgent, ...],
            "dynamic": [SecurityAgent, DevOpsAgent, ...],
            "all": [all agents]
        }
        """
        all_agents = self.base_agents + self.dynamic_agents
        
        return {
            "base": self.base_agents,
            "dynamic": self.dynamic_agents,
            "all": all_agents,
            "count": len(all_agents),
        }
    
    def assign_models(self) -> Dict[str, str]:
        """
        Her agent'e model assign et
        
        Returns:
        {
            "Planner": "claude-3-5-sonnet",
            "Coder": "gpt-4o",
            ...
        }
        """
        assignment = {}
        
        for agent in self.get_all_agents()["all"]:
            assignment[agent.role] = agent.model
        
        return assignment
    
    def save_team_config(self, project_id: str):
        """Team configuration'ı JSON'a kaydet"""
        
        config = {
            "project_id": project_id,
            "timestamp": datetime.now().isoformat(),
            "team_composition": {
                "base_agents": len(self.base_agents),
                "dynamic_agents": len(self.dynamic_agents),
                "total": len(self.get_all_agents()["all"]),
            },
            "agents": [
                {
                    "role": agent.role,
                    "model": agent.model,
                    "priority": ROLE_RULES.get(agent.role, {}).get("priority", "MEDIUM"),
                }
                for agent in self.get_all_agents()["all"]
            ],
            "clarifications_used": self.clarifications,
        }
        
        filepath = f"workspace/.team/{project_id}_team.json"
        with open(filepath, "w") as f:
            json.dump(config, f, indent=2)

EXAMPLE OUTPUT:
{
  "project_id": "ecommerce_001",
  "timestamp": "2025-10-27T14:30:00Z",
  "team_composition": {
    "base_agents": 5,
    "dynamic_agents": 2,
    "total": 7
  },
  "agents": [
    {"role": "Planner", "model": "claude-3-5-sonnet", "priority": "HIGH"},
    {"role": "Coder", "model": "gpt-4o", "priority": "HIGH"},
    {"role": "SecurityAgent", "model": "claude-3-5-sonnet", "priority": "HIGH"},
    {"role": "DevOpsAgent", "model": "gpt-4o", "priority": "MEDIUM"},
    ...
  ]
}
```

3. Integration: main.py'e ekle:

```python
# main.py

from agents.dynamic_role_manager import DynamicRoleManager
from utils.brief_generator import BriefGenerator

def main():
    # ... (Clarification Phase - Etap 1)
    clarifications = clarification_agent.run_interactive()
    
    # NEW: Dynamic Role Management Phase (Etap 2)
    role_manager = DynamicRoleManager(clarifications)
    role_manager.create_dynamic_agents()
    
    team_agents = role_manager.get_all_agents()
    print(f"Team assembled: {team_agents['count']} agents")
    
    role_manager.save_team_config(project_id)
    
    # NEW: Orchestrator'ı dynamic team ile initialize et
    orchestrator.initialize_with_agents(team_agents["all"])
    
    # ... (rest of execution)
```

BAŞARILI KABUL KRİTERLERİ:
✅ DynamicRoleManager clarifications'dan rolle belirliyor
✅ Max 5 dynamic agent (cost control)
✅ Agents JSON'a kaydediliyor
✅ workspace/.team/{project_id}_team.json oluşturuluyor
✅ Model assignment logic working
```

## Prompt 2.2: Task Assignment & Execution Strategy

```
GÖREV: Dynamic roller için task assignment sistemi ekle.

DETAYLAR:

1. Task Assignment Logic:

```python
# tasks/assignment_engine.py

class TaskAssignmentEngine:
    def __init__(self, todo_list: List[Dict], agents: Dict[str, Agent]):
        self.todos = todo_list
        self.agents = agents
    
    def assign_tasks(self) -> List[Task]:
        """
        TODO list'i agent'lere assign et
        
        Mantık:
        - "Database schema" → DatabaseArchitectAgent (varsa), yoksa Coder
        - "Security audit" → SecurityAgent, yoksa Reviewer
        - "Deployment" → DevOpsAgent, yoksa Coder
        """
        
        tasks = []
        
        for todo in self.todos:
            best_agent = self._find_best_agent(todo)
            
            task = Task(
                description=todo["title"],
                expected_output=todo.get("expected_output", ""),
                agent=best_agent,
                priority=todo.get("priority", "MEDIUM"),
            )
            
            tasks.append(task)
        
        return tasks
    
    def _find_best_agent(self, todo: Dict) -> Agent:
        """
        TODO için en uygun agent'i bul
        
        Matching algorithm:
        1. Exact match (role name + todo keywords)
        2. Skill match (role skills + todo requirements)
        3. Default fallback (Coder)
        """
        
        todo_keywords = set(todo["title"].lower().split())
        
        best_match = None
        best_score = 0
        
        for agent in self.agents.get("all", []):
            role_config = ROLE_RULES.get(agent.role, {})
            triggers = role_config.get("triggers", [])
            
            # Keyword matching
            score = len(set(triggers) & todo_keywords)
            
            if score > best_score:
                best_score = score
                best_match = agent
        
        return best_match or self.agents["base"][1]  # Fallback to Coder
    
    def get_execution_strategy(self) -> str:
        """
        Task execution stratejisi belirle:
        - sequential: Sırayla (default)
        - parallel: Base agents parallel, dynamic sequential
        - race: İlk başarılı sonuç kazanır (cost control)
        """
        
        dynamic_count = len(self.agents.get("dynamic", []))
        
        if dynamic_count > 3:
            return "sequential"  # Çok agent varsa sequential
        elif dynamic_count > 0:
            return "parallel"  # Hybrid
        else:
            return "parallel"  # Base agents parallelizable
```

2. Execution Orchestration:

```python
# core/execution_engine.py

class ExecutionEngine:
    def __init__(self, tasks: List[Task], strategy: str):
        self.tasks = tasks
        self.strategy = strategy
    
    async def execute(self) -> Dict:
        """
        Tasks'ı execute et seçilen stratejiye göre
        """
        
        if self.strategy == "sequential":
            return await self._execute_sequential()
        elif self.strategy == "parallel":
            return await self._execute_parallel()
        elif self.strategy == "race":
            return await self._execute_race()
    
    async def _execute_sequential(self) -> Dict:
        """
        Tasks'ı sırayla çalıştır
        Prev task'ın output'u next task'ın input'u
        """
        results = []
        
        for i, task in enumerate(self.tasks):
            context = results[i-1] if i > 0 else None
            
            result = await self._execute_task(task, context)
            results.append(result)
            
            # Task arası barrier
            print(f"✅ Task {i+1}/{len(self.tasks)} completed: {task.description}")
        
        return {"status": "SUCCESS", "results": results}
    
    async def _execute_parallel(self) -> Dict:
        """
        Parallelizable tasks'ı async çalıştır
        
        Dependency graph:
        Planner → Coder (depends on Plan)
        Coder → [Tester, Reviewer, UIUXAgent] (parallel)
        [Tester, Reviewer] → Documenter (final)
        """
        
        import asyncio
        
        # Phase 1: Planner
        plan_result = await self._execute_task(self.tasks[0])
        
        # Phase 2: Coder
        code_result = await self._execute_task(self.tasks[1], plan_result)
        
        # Phase 3: Parallel (Tester + Reviewer + Others)
        parallel_tasks = self.tasks[2:-1]  # Skip Documenter
        parallel_results = await asyncio.gather(
            *[self._execute_task(t, code_result) for t in parallel_tasks]
        )
        
        # Phase 4: Documenter
        doc_result = await self._execute_task(
            self.tasks[-1], 
            parallel_results
        )
        
        return {
            "status": "SUCCESS",
            "phases": {
                "plan": plan_result,
                "code": code_result,
                "parallel": parallel_results,
                "documentation": doc_result,
            }
        }
    
    async def _execute_task(self, task: Task, context: Dict = None) -> Dict:
        """Tek bir task'ı execute et"""
        
        result = await task.agent.run(
            task=task.description,
            context=context or {}
        )
        
        return {
            "task": task.description,
            "agent": task.agent.role,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
```

3. Integration:

```python
# main.py

from tasks.assignment_engine import TaskAssignmentEngine
from core.execution_engine import ExecutionEngine

def main():
    # ... (Etap 1 & 2: Clarifications + Team Assembly)
    
    # NEW: Task Assignment
    assignment_engine = TaskAssignmentEngine(
        todo_list=todos,
        agents=team_agents
    )
    
    tasks = assignment_engine.assign_tasks()
    strategy = assignment_engine.get_execution_strategy()
    
    print(f"Task assignment complete: {len(tasks)} tasks")
    print(f"Execution strategy: {strategy}")
    
    # NEW: Execution
    executor = ExecutionEngine(tasks, strategy)
    results = await executor.execute()
    
    # ... (rest)
```

BAŞARILI KABUL KRİTERLERİ:
✅ Task'lar doğru agent'lere assign ediliyor
✅ Execution stratejisi otomatik seçiliyor
✅ Parallel execution çalışıyor (speedup)
✅ Sequential mode cost-effective
✅ Results structured output döndürüyor
```

## Prompt 2.3: Etap 2 Test & Validation

```
GÖREV: Etap 2 (Dynamic Roles) için comprehensive test suite yaz.

TEST CASES:

1. test_dynamic_role_manager.py:

```python
import pytest
from agents.dynamic_role_manager import DynamicRoleManager, ROLE_RULES

class TestDynamicRoleManager:
    
    def test_security_agent_triggered(self):
        """Payment feature olunca SecurityAgent trigger olması test et"""
        
        clarifications = {
            "features": {"payment": "Stripe"},
        }
        
        manager = DynamicRoleManager(clarifications)
        required_roles = manager.analyze_requirements()
        
        assert "SecurityAgent" in required_roles
    
    def test_devops_agent_triggered(self):
        """Docker deployment olunca DevOpsAgent trigger olması"""
        
        clarifications = {
            "deployment": "Docker",
        }
        
        manager = DynamicRoleManager(clarifications)
        required_roles = manager.analyze_requirements()
        
        assert "DevOpsAgent" in required_roles
    
    def test_multiple_roles_triggered(self):
        """Kompleks proje: multiple role trigger"""
        
        clarifications = {
            "features": {"payment": "Stripe", "auth": "OAuth"},
            "deployment": "Kubernetes",
            "frontend": "React",
        }
        
        manager = DynamicRoleManager(clarifications)
        required_roles = manager.analyze_requirements()
        
        # Multiple roles expected
        assert len(required_roles) >= 2
        assert "SecurityAgent" in required_roles
    
    def test_max_five_dynamic_agents(self):
        """Max 5 dynamic agent limit"""
        
        clarifications = {
            "features": {
                "payment": "Stripe",
                "auth": "OAuth",
                "optimization": True,
                "ui": "complex",
                "database": "advanced",
            }
        }
        
        manager = DynamicRoleManager(clarifications)
        manager.create_dynamic_agents()
        
        assert len(manager.dynamic_agents) <= 5
    
    def test_base_agents_always_present(self):
        """5 base agent hep olmalı"""
        
        manager = DynamicRoleManager({})
        agents = manager.get_all_agents()
        
        assert len(agents["base"]) == 5
        base_roles = [a.role for a in agents["base"]]
        
        assert "Planner" in base_roles
        assert "Coder" in base_roles
        assert "Tester" in base_roles
    
    def test_model_assignment_correct(self):
        """Model assignment logic"""
        
        manager = DynamicRoleManager({"features": {"payment": "Stripe"}})
        manager.create_dynamic_agents()
        
        model_map = manager.assign_models()
        
        assert model_map["Planner"] == "claude-3-5-sonnet"
        assert model_map["Coder"] == "gpt-4o"
        assert model_map.get("SecurityAgent") == "claude-3-5-sonnet"
    
    def test_team_config_saved(self, tmp_path):
        """Team config JSON kaydediliyor mu?"""
        
        manager = DynamicRoleManager({"deployment": "Docker"})
        manager.create_dynamic_agents()
        manager.save_team_config("test_project")
        
        # File exists check
        assert os.path.exists("workspace/.team/test_project_team.json")

2. test_task_assignment.py:

```python
from tasks.assignment_engine import TaskAssignmentEngine

class TestTaskAssignment:
    
    def test_database_schema_to_architect(self):
        """Database schema task → DatabaseArchitectAgent"""
        
        todos = [
            {"title": "Create database schema", "priority": "HIGH"}
        ]
        
        agents = {...}  # Mock agents
        
        engine = TaskAssignmentEngine(todos, agents)
        tasks = engine.assign_tasks()
        
        assert tasks[0].agent.role == "DatabaseArchitectAgent"
    
    def test_security_audit_to_security_agent(self):
        """Security audit → SecurityAgent"""
        
        todos = [
            {"title": "Security audit and encryption", "priority": "HIGH"}
        ]
        
        engine = TaskAssignmentEngine(todos, agents)
        tasks = engine.assign_tasks()
        
        assert tasks[0].agent.role == "SecurityAgent"
    
    def test_fallback_to_coder(self):
        """Eğer matching agent yoksa Coder'a fall back et"""
        
        todos = [
            {"title": "Random generic task", "priority": "LOW"}
        ]
        
        engine = TaskAssignmentEngine(todos, agents)
        best_agent = engine._find_best_agent(todos[0])
        
        assert best_agent.role == "Coder"
    
    def test_execution_strategy_selection(self):
        """
        Execution strategy seçimi:
        - 0 dynamic → parallel
        - 1-3 dynamic → parallel
        - >3 dynamic → sequential
        """
        
        # Many agents case
        agents_many = {"base": [...], "dynamic": [1,2,3,4,5]}
        engine = TaskAssignmentEngine(todos, agents_many)
        
        strategy = engine.get_execution_strategy()
        assert strategy == "sequential"

3. test_execution.py:

```python
from core.execution_engine import ExecutionEngine

class TestExecutionEngine:
    
    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Sequential execution order"""
        
        tasks = [
            Task(description="Task 1", agent=mock_agent1),
            Task(description="Task 2", agent=mock_agent2),
            Task(description="Task 3", agent=mock_agent3),
        ]
        
        executor = ExecutionEngine(tasks, "sequential")
        results = await executor.execute()
        
        assert len(results["results"]) == 3
        assert results["status"] == "SUCCESS"
    
    @pytest.mark.asyncio
    async def test_parallel_execution_speedup(self):
        """Parallel execution 2-3x hızlanmalı"""
        
        import time
        
        tasks = [...]
        
        # Sequential time
        executor_seq = ExecutionEngine(tasks, "sequential")
        start_seq = time.time()
        await executor_seq.execute()
        time_seq = time.time() - start_seq
        
        # Parallel time
        executor_par = ExecutionEngine(tasks, "parallel")
        start_par = time.time()
        await executor_par.execute()
        time_par = time.time() - start_par
        
        # Parallel should be faster (roughly 1.5-2x)
        assert time_par < time_seq * 0.7  # 30% hızlı olmali minimum

EXPECTED TEST RESULTS:
✅ 20+ tests passing
✅ 95% code coverage
✅ All agent routing tests passing
✅ Execution strategy tests passing
```

---

# ⚡ ETAP 3: SUPER ADMIN COORDINATOR (4-5 hafta)

## Prompt 3.1: Integrity Checker

```
GÖREV: Integrity Checker sistemi tasarla ve kodla.
Bu sistem çalışan agents'in output'unu kontrol eder ve uyumsuzlukları tespit eder.

DETAYLAR:

1. Integrity Check Types:

```python
# core/integrity_checker.py

class IntegrityChecker:
    def __init__(self):
        self.checks = {}
        self.violations = []
    
    # CHECK 1: API Consistency
    def check_api_consistency(self, coder_output: Dict, reviewer_output: Dict) -> bool:
        """
        Coder'ın yazdığı API ile Reviewer'ın gördüğü API tutarlı mı?
        
        Örnek:
        Frontend: expects User.name
        Backend: provides User.fullName
        ❌ Inconsistent → Violation
        """
        
        frontend_models = self._extract_models(coder_output.get("frontend_code", ""))
        backend_models = self._extract_models(coder_output.get("backend_code", ""))
        
        mismatches = self._find_mismatches(frontend_models, backend_models)
        
        if mismatches:
            self.violations.append({
                "type": "API_MISMATCH",
                "severity": "HIGH",
                "details": mismatches,
                "agents": ["Coder", "Reviewer"],
            })
            return False
        
        return True
    
    # CHECK 2: Test Coverage
    def check_test_coverage(self, coder_tasks: List, tester_tasks: List) -> bool:
        """
        Test coverage >= 80%?
        
        Örnek:
        Coder: Wrote 5 new functions
        Tester: Only tested 3
        ❌ Coverage < 80% → Violation
        """
        
        functions_written = len(coder_tasks)
        functions_tested = len(tester_tasks)
        
        coverage = functions_tested / functions_written if functions_written > 0 else 1.0
        
        if coverage < 0.80:
            self.violations.append({
                "type": "LOW_TEST_COVERAGE",
                "severity": "MEDIUM",
                "details": {
                    "coverage": coverage * 100,
                    "threshold": 80,
                    "untested_count": functions_written - functions_tested,
                },
                "agents": ["Tester"],
            })
            return False
        
        return True
    
    # CHECK 3: Documentation Completeness
    def check_documentation(self, code_count: int, doc_count: int) -> bool:
        """
        Dokümantasyon >= 90% complete?
        
        Örnek:
        Coder: 10 new endpoints
        Documenter: Only 6 documented
        ❌ Doc coverage < 90% → Violation
        """
        
        doc_coverage = doc_count / code_count if code_count > 0 else 1.0
        
        if doc_coverage < 0.90:
            self.violations.append({
                "type": "INCOMPLETE_DOCUMENTATION",
                "severity": "LOW",
                "details": {
                    "coverage": doc_coverage * 100,
                    "threshold": 90,
                    "undocumented_count": code_count - doc_count,
                },
                "agents": ["Documenter"],
            })
            return False
        
        return True
    
    # CHECK 4: Database Migrations
    def check_database_migrations(self, code_output: Dict) -> bool:
        """
        Model değişiklikleri var ama migration file yok mu?
        
        Örnek:
        Coder: Added new field to User model
        Missing: Database migration file
        ❌ Deployment will fail → Violation
        """
        
        has_model_changes = self._detect_model_changes(code_output)
        has_migrations = self._detect_migration_files(code_output)
        
        if has_model_changes and not has_migrations:
            self.violations.append({
                "type": "MISSING_DATABASE_MIGRATION",
                "severity": "HIGH",
                "details": {
                    "model_changes_detected": True,
                    "migration_files": 0,
                },
                "agents": ["Coder"],
            })
            return False
        
        return True
    
    # CHECK 5: Security Compliance
    def check_security_compliance(self, code_output: Dict) -> bool:
        """
        Temel security best practices var mı?
        - No hardcoded secrets
        - Password hashing used
        - SQL injection prevention
        """
        
        violations_found = []
        
        # Check for hardcoded secrets
        if self._has_hardcoded_secrets(code_output):
            violations_found.append("hardcoded_secrets")
        
        # Check for password hashing
        if self._needs_password_hashing(code_output) and not self._uses_password_hash(code_output):
            violations_found.append("missing_password_hashing")
        
        # Check for SQL injection prevention
        if self._has_raw_sql_queries(code_output):
            violations_found.append("potential_sql_injection")
        
        if violations_found:
            self.violations.append({
                "type": "SECURITY_VIOLATION",
                "severity": "CRITICAL",
                "details": violations_found,
                "agents": ["SecurityAgent" if hasattr(self, "security_agent") else "Coder"],
            })
            return False
        
        return True
    
    # CHECK 6: Dependency Conflicts
    def check_dependency_conflicts(self, requirements: List[str]) -> bool:
        """
        Çakışan package versions var mı?
        
        Örnek:
        - package_a requires django>=2.0,<3.0
        - package_b requires django>=3.0
        ❌ Conflict → Violation
        """
        
        conflicts = self._find_version_conflicts(requirements)
        
        if conflicts:
            self.violations.append({
                "type": "DEPENDENCY_CONFLICT",
                "severity": "HIGH",
                "details": conflicts,
                "agents": ["Coder"],
            })
            return False
        
        return True
    
    def run_all_checks(self, project_output: Dict) -> Dict:
        """
        Tüm checks'i çalıştır
        
        Returns:
        {
            "all_pass": True/False,
            "violations": [...],
            "scores": {
                "api_consistency": 1.0 (0-1 scale),
                "test_coverage": 0.92,
                ...
            }
        }
        """
        
        checks_passed = []
        
        # Run all checks
        checks_passed.append(("API Consistency", self.check_api_consistency(...)))
        checks_passed.append(("Test Coverage", self.check_test_coverage(...)))
        checks_passed.append(("Documentation", self.check_documentation(...)))
        checks_passed.append(("DB Migrations", self.check_database_migrations(...)))
        checks_passed.append(("Security", self.check_security_compliance(...)))
        checks_passed.append(("Dependencies", self.check_dependency_conflicts(...)))
        
        all_pass = all(result for _, result in checks_passed)
        
        return {
            "all_pass": all_pass,
            "violations": self.violations,
            "scores": {name: (1.0 if result else 0.0) for name, result in checks_passed},
            "violations_count": len(self.violations),
        }
    
    def _extract_models(self, code: str) -> Dict:
        """Extract model definitions from code"""
        pass
    
    def _find_mismatches(self, models_a: Dict, models_b: Dict) -> List:
        """Find API inconsistencies"""
        pass
    
    # ... (other helper methods)
```

BAŞARILI KABUL KRİTERLERİ:
✅ 6 integrity check types working
✅ Violations properly detected
✅ Scores calculated (0-1)
✅ JSON report generation
```

## Prompt 3.2: Conflict Resolver

```
GÖREV: Conflict Resolver tasarla - iki agent'in çelişkili output'unu çöz.

DETAYLAR:

```python
# core/conflict_resolver.py

class ConflictResolver:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    async def resolve_conflict(self, conflict: Dict) -> Dict:
        """
        Çelişkiyi otomatik veya user yardımıyla çöz
        
        conflict = {
            "type": "API_MISMATCH",
            "agent_1": "Coder",
            "agent_2": "Reviewer",
            "details": {...},
        }
        """
        
        conflict_type = conflict["type"]
        
        if conflict_type == "API_MISMATCH":
            return await self._resolve_api_mismatch(conflict)
        elif conflict_type == "CODE_STYLE_CONFLICT":
            return await self._resolve_style_conflict(conflict)
        elif conflict_type == "IMPLEMENTATION_CONFLICT":
            return await self._resolve_implementation_conflict(conflict)
    
    async def _resolve_api_mismatch(self, conflict: Dict) -> Dict:
        """
        Frontend ↔ Backend API mismatch çöz
        
        Strateji:
        1. Backend'i source of truth kabul et
        2. Frontend'de matching model update
        3. Tests güncelle
        """
        
        details = conflict["details"]
        
        # Backend spec'i al
        backend_spec = details["backend_models"]
        
        # Frontend'i backend'e align et
        fix = {
            "action": "UPDATE_FRONTEND_MODELS",
            "changes": {
                "before": details["frontend_models"],
                "after": backend_spec,
            },
            "agents_to_notify": ["Coder"],
        }
        
        # Coder'ı güncelleme için invoke et
        await self.orchestrator.notify_agent(
            agent_name="Coder",
            message=f"Update frontend models to match backend: {fix['changes']}"
        )
        
        return {
            "resolution": "COMPLETED",
            "type": "AUTO",
            "fix": fix,
        }
    
    async def _resolve_style_conflict(self, conflict: Dict) -> Dict:
        """
        Code style conflict çöz
        
        Strateji:
        1. Project styleguide'ı apply et
        2. Auto-formatter çalıştır
        """
        
        fix = {
            "action": "APPLY_STYLE_GUIDE",
            "formatter": "black",  # Python için
            "agents_to_notify": ["Reviewer"],
        }
        
        # Formatter'ı çalıştır
        await self.orchestrator.run_formatter()
        
        return {
            "resolution": "COMPLETED",
            "type": "AUTO",
            "fix": fix,
        }
    
    async def _resolve_implementation_conflict(self, conflict: Dict) -> Dict:
        """
        İki agent'in farklı implementation'ı çöz
        
        Strateji:
        1. Her iki approach'ın pros/cons'unu listele
        2. Best approach'ı seç (heuristic)
        3. Tercih ettiğin approach'ı kullan
        4. Diğer code silinir
        
        Örnek:
        Coder: "Use bcrypt for passwords"
        SecurityAgent: "Use argon2"
        → Argon2 daha iyi, SecurityAgent wins
        """
        
        details = conflict["details"]
        
        implementation_a = {
            "agent": details["agent_1"],
            "approach": details["approach_1"],
            "score": self._score_implementation(details["approach_1"]),
        }
        
        implementation_b = {
            "agent": details["agent_2"],
            "approach": details["approach_2"],
            "score": self._score_implementation(details["approach_2"]),
        }
        
        # Better one wins
        winner = implementation_a if implementation_a["score"] > implementation_b["score"] else implementation_b
        loser = implementation_b if winner == implementation_a else implementation_a
        
        fix = {
            "action": "USE_IMPLEMENTATION",
            "winner_agent": winner["agent"],
            "winner_approach": winner["approach"],
            "loser_agent": loser["agent"],
            "loser_code_status": "REMOVE",
        }
        
        # Loser'ı notify et
        await self.orchestrator.notify_agent(
            agent_name=loser["agent"],
            message=f"Your implementation replaced with: {winner['approach']}"
        )
        
        return {
            "resolution": "COMPLETED",
            "type": "AUTO",
            "fix": fix,
        }
    
    def _score_implementation(self, approach: str) -> float:
        """
        Implementation'ı 0-1 arası score'la
        
        Kriterleri:
        - Security
        - Performance
        - Maintainability
        - Community adoption
        """
        
        score = 0.0
        
        # Scoring logic
        if "argon2" in approach.lower():
            score += 0.3  # Better security
        elif "bcrypt" in approach.lower():
            score += 0.2
        
        if "async" in approach.lower():
            score += 0.2  # Performance
        
        if "well-documented" in approach.lower() or "standard" in approach.lower():
            score += 0.2  # Maintainability
        
        return min(score, 1.0)
```

BAŞARILI KABUL KRİTERLERİ:
✅ API mismatch otomatik çözülüyor
✅ Style conflicts auto-formatter ile çözülüyor
✅ Implementation conflicts best approach seçiyor
✅ Conflict resolution log'u tutuluyor
```

## Prompt 3.3: Super Admin Orchestrator

```
GÖREV: SuperAdminOrchestrator tasarla - tüm kontrolü yönet.

DETAYLAR:

```python
# core/super_admin.py

from core.integrity_checker import IntegrityChecker
from core.conflict_resolver import ConflictResolver

class SuperAdminOrchestrator:
    def __init__(self, base_orchestrator, approval_mode: str = "interactive"):
        self.base = base_orchestrator
        self.approval_mode = approval_mode  # automatic, interactive, manual
        self.integrity_checker = IntegrityChecker()
        self.conflict_resolver = ConflictResolver(self)
        
        self.event_queue = asyncio.Queue()
        self.interventions = []
    
    async def supervise(self):
        """
        Continuous supervision loop
        Event-driven: her task tamamlandığında trigger
        """
        
        while True:
            try:
                # Event'i bekle (non-blocking)
                event = await asyncio.wait_for(
                    self.event_queue.get(), 
                    timeout=None
                )
                
                # Event'i handle et
                await self.handle_event(event)
                
            except asyncio.TimeoutError:
                # Periodic check (her 5 dakika)
                await self.periodic_health_check()
                continue
    
    async def handle_event(self, event: Dict):
        """
        Event'i handle et (task completion, errors, vb)
        """
        
        event_type = event["type"]
        
        if event_type == "TASK_COMPLETED":
            await self.on_task_completed(event)
        elif event_type == "TASK_FAILED":
            await self.on_task_failed(event)
        elif event_type == "CONFLICT_DETECTED":
            await self.on_conflict_detected(event)
        elif event_type == "QUALITY_ISSUE":
            await self.on_quality_issue(event)
    
    async def on_task_completed(self, event: Dict):
        """Task tamamlandı → Integrity check"""
        
        task_output = event["output"]
        task_agent = event["agent"]
        
        print(f"🔍 Super Admin: Verifying {task_agent} output...")
        
        # Integrity checks
        check_results = self.integrity_checker.run_all_checks(task_output)
        
        if not check_results["all_pass"]:
            print(f"⚠️  Integrity violations found: {check_results['violations_count']}")
            
            await self.handle_integrity_violations(
                violations=check_results["violations"],
                task_agent=task_agent,
            )
        else:
            print(f"✅ {task_agent} output verified successfully")
    
    async def handle_integrity_violations(self, violations: List, task_agent: str):
        """
        Integrity violations handle et
        """
        
        for violation in violations:
            severity = violation["severity"]
            violation_type = violation["type"]
            
            if severity == "CRITICAL":
                # CRITICAL → Always intervene
                await self.intervene(violation, auto_fix=True)
            
            elif severity == "HIGH":
                # HIGH → Auto-fix in professional mode
                if self.approval_mode == "professional":
                    await self.intervene(violation, auto_fix=True)
                else:
                    await self.ask_user_intervention(violation)
            
            elif severity == "MEDIUM":
                # MEDIUM → Notify, log
                await self.notify_violation(violation)
            
            elif severity == "LOW":
                # LOW → Just log
                self.log_violation(violation)
    
    async def intervene(self, violation: Dict, auto_fix: bool = True) -> Dict:
        """
        Violation'a müdahale et
        
        Seçenekler:
        1. Auto-fix (immediate)
        2. Re-assign (diğer agent'e ver)
        3. Escalate (better model kullan)
        4. Manual (kullanıcıya sor)
        """
        
        violation_type = violation["type"]
        affected_agent = violation["agents"][0]
        
        intervention = {
            "timestamp": datetime.now().isoformat(),
            "violation_type": violation_type,
            "affected_agent": affected_agent,
            "mode": "AUTO" if auto_fix else "MANUAL",
        }
        
        if violation_type == "LOW_TEST_COVERAGE":
            # Tester'a test yazması söyle
            print(f"📝 Super Admin: Requesting {affected_agent} to increase test coverage")
            
            await self.notify_agent(
                agent_name="Tester",
                message=f"Test coverage {violation['details']['coverage']:.1f}% < 80%. " \
                        f"Please write {violation['details']['untested_count']} more tests.",
                priority="HIGH",
            )
            
            intervention["action"] = "ESCALATE_TO_AGENT"
            intervention["details"] = f"Tester asked to write missing tests"
        
        elif violation_type == "INCOMPLETE_DOCUMENTATION":
            # Documenter'a doc yazması söyle
            print(f"📝 Super Admin: Requesting Documenter to complete documentation")
            
            await self.notify_agent(
                agent_name="Documenter",
                message=f"Documentation {violation['details']['coverage']:.1f}% < 90%. " \
                        f"Please document {violation['details']['undocumented_count']} missing items.",
                priority="MEDIUM",
            )
            
            intervention["action"] = "ESCALATE_TO_AGENT"
        
        elif violation_type == "MISSING_DATABASE_MIGRATION":
            # Migration file oluştur
            print(f"🗂️ Super Admin: Generating missing database migration")
            
            await self.notify_agent(
                agent_name="Coder",
                message="Model changes detected but migration file missing. Please create migration.",
                priority="HIGH",
            )
            
            intervention["action"] = "ESCALATE_TO_AGENT"
        
        elif violation_type == "SECURITY_VIOLATION":
            # Security fix immediately
            print(f"🔒 Super Admin: Fixing security violation")
            
            await self.fix_security_issue(violation)
            
            intervention["action"] = "AUTO_FIX"
            intervention["details"] = f"Fixed: {', '.join(violation['details'])}"
        
        self.interventions.append(intervention)
        
        return intervention
    
    async def on_conflict_detected(self, event: Dict):
        """
        İki agent'in çelişkili output'u tespit edildi
        """
        
        conflict = event["conflict"]
        
        print(f"⚖️ Super Admin: Conflict detected between {conflict['agent_1']} and {conflict['agent_2']}")
        
        # ConflictResolver'ı çalıştır
        resolution = await self.conflict_resolver.resolve_conflict(conflict)
        
        print(f"✅ Conflict resolved: {resolution['type']}")
    
    async def ask_user_intervention(self, violation: Dict):
        """
        User'dan müdahale kararı iste (interactive mode)
        """
        
        from utils.interactive_tools import ask_user
        
        print(f"\n⚠️  Super Admin Alert: {violation['type']}")
        print(f"Severity: {violation['severity']}")
        print(f"Details: {violation['details']}")
        
        response = await ask_user(
            f"Auto-fix this {violation['type']}?",
            options=["Yes", "No", "Review"]
        )
        
        if response == "Yes":
            await self.intervene(violation, auto_fix=True)
        elif response == "Review":
            await self.show_details(violation)
    
    async def periodic_health_check(self):
        """
        Periyodik health check (her 5 dakika)
        Safety net olarak
        """
        
        print("🏥 Super Admin: Running periodic health check...")
        
        # Check all agents are responsive
        # Check no hanging tasks
        # Check resource usage
        # Check costs
```

BAŞARILI KABUL KRİTERLERİ:
✅ Continuous supervision working
✅ Violations otomatik detect ediliyor
✅ Event-driven model working
✅ Interventions properly logged
✅ Approval modes (automatic/interactive/manual) working
```

## Prompt 3.4: Reporting & Dashboard

```
GÖREV: Super Admin reports ve real-time dashboard.

DETAYLAR:

```python
# core/reporting/admin_reports.py

class SuperAdminReporting:
    def __init__(self, super_admin):
        self.super_admin = super_admin
    
    async def generate_comprehensive_report(self) -> Dict:
        """
        Comprehensive Super Admin report
        """
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_id": self.super_admin.current_project_id,
            
            "executive_summary": {
                "status": self._calculate_overall_status(),
                "health_score": self._calculate_health_score(),  # 0-100
                "interventions_count": len(self.super_admin.interventions),
                "critical_issues": len([i for i in self.super_admin.interventions if i["severity"] == "CRITICAL"]),
            },
            
            "integrity_check_results": {
                "api_consistency": {...},
                "test_coverage": {...},
                "documentation": {...},
                "security": {...},
                "dependencies": {...},
            },
            
            "agent_performance": {
                "Planner": {...},
                "Coder": {...},
                "Tester": {...},
                "Reviewer": {...},
                "Documenter": {...},
            },
            
            "interventions": self.super_admin.interventions,
            
            "costs": {
                "tokens_used": ...,
                "api_calls": ...,
                "estimated_cost": ...,
            },
            
            "recommendations": self._generate_recommendations(),
            
            "timeline": {
                "start_time": ...,
                "end_time": ...,
                "total_duration": ...,
            },
        }
        
        return report
    
    def export_report(self, format: str = "json") -> str:
        """
        Report'u export et (json, markdown, html, pdf)
        """
        
        report = self.generate_comprehensive_report()
        
        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "markdown":
            return self._format_markdown(report)
        elif format == "html":
            return self._format_html(report)
        elif format == "pdf":
            return self._format_pdf(report)
    
    def _format_markdown(self, report: Dict) -> str:
        """Markdown formatted report"""
        
        md = f"""# YAGO Super Admin Report
**Project:** {report['project_id']}
**Generated:** {report['timestamp']}

## Executive Summary
- **Overall Status:** {report['executive_summary']['status']}
- **Health Score:** {report['executive_summary']['health_score']}/100
- **Interventions:** {report['executive_summary']['interventions_count']}
- **Critical Issues:** {report['executive_summary']['critical_issues']}

## Integrity Checks
...

## Agent Performance
...

## Interventions Log
...

## Costs
...

## Recommendations
...
"""
        return md

# web/backend/dashboard.py (FastAPI endpoint)

from fastapi import FastAPI
from fastapi.responses import JSONResponse

@app.get("/api/super-admin/report")
async def get_super_admin_report():
    """Real-time Super Admin report endpoint"""
    
    report = super_admin.reporter.generate_comprehensive_report()
    return JSONResponse(report)

@app.get("/api/super-admin/interventions")
async def get_interventions(limit: int = 50):
    """Recent interventions"""
    
    return {
        "interventions": super_admin.interventions[-limit:],
        "total": len(super_admin.interventions),
    }

@app.get("/api/super-admin/health")
async def get_health():
    """Health check endpoint"""
    
    return {
        "status": super_admin.get_status(),
        "health_score": super_admin.reporter._calculate_health_score(),
        "agents_active": len(super_admin.active_agents),
    }
```

BAŞARILI KABUL KRİTERLERİ:
✅ Comprehensive reports generating
✅ Multiple export formats (json, md, html)
✅ Dashboard endpoints working
✅ Real-time metrics updating
```

## Prompt 3.5: Integration & Final Testing

```
GÖREV: Etap 3'ü (Super Admin) main flow'a entegre et ve test et.

INTEGRATION:

```python
# main.py - Full v7.0 Flow

async def main():
    # Phase 1: Clarification (Etap 1)
    print("📋 Phase 1: Clarification")
    clarification_agent = ClarificationAgent()
    clarifications = await clarification_agent.run_interactive()
    project_id = clarifications["project_id"]
    
    # Phase 2: Dynamic Roles (Etap 2)
    print("👥 Phase 2: Team Assembly")
    role_manager = DynamicRoleManager(clarifications)
    role_manager.create_dynamic_agents()
    team_agents = role_manager.get_all_agents()
    role_manager.save_team_config(project_id)
    
    # Phase 3: Execution
    print("⚙️ Phase 3: Execution")
    assignment_engine = TaskAssignmentEngine(todos, team_agents)
    tasks = assignment_engine.assign_tasks()
    strategy = assignment_engine.get_execution_strategy()
    
    executor = ExecutionEngine(tasks, strategy)
    exec_results = await executor.execute()
    
    # Phase 4: Super Admin Supervision (NEW - Etap 3)
    print("👮 Phase 4: Super Admin Supervision")
    super_admin = SuperAdminOrchestrator(orchestrator, approval_mode="automatic")
    
    # Supervision loop başlat (background)
    supervision_task = asyncio.create_task(super_admin.supervise())
    
    # Main execution loop
    for task_result in exec_results:
        # Event'i super admin'e gönder
        await super_admin.event_queue.put({
            "type": "TASK_COMPLETED",
            "output": task_result,
            "agent": task_result["agent"],
        })
    
    # Supervision bitmesi için bekle
    await asyncio.sleep(5)  # Interventions tamamlansın
    
    # Phase 5: Reporting
    print("📊 Phase 5: Reporting")
    report = super_admin.reporter.generate_comprehensive_report()
    
    print(f"\n✅ Project '{project_id}' completed!")
    print(f"Health Score: {report['executive_summary']['health_score']}/100")
    print(f"Interventions: {report['executive_summary']['interventions_count']}")
    
    # Reports'ı export et
    with open(f"reports/{project_id}_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    with open(f"reports/{project_id}_report.md", "w") as f:
        f.write(super_admin.reporter._format_markdown(report))

# TEST CASES

class TestEtap3Integration:
    
    @pytest.mark.asyncio
    async def test_full_pipeline_with_super_admin(self):
        """Tüm 5 phase'i end-to-end test et"""
        
        result = await main()
        
        assert result["status"] == "SUCCESS"
        assert result["interventions_count"] >= 0
        assert result["health_score"] >= 0
    
    @pytest.mark.asyncio
    async def test_super_admin_detects_test_coverage_issue(self):
        """Super Admin test coverage violation tespit ediyor"""
        
        # Simulate: Coder writes code, Tester incomplete
        mock_output = {
            "coder_functions": 5,
            "tested_functions": 3,  # < 80%
        }
        
        # Super Admin should detect
        event = {
            "type": "TASK_COMPLETED",
            "output": mock_output,
            "agent": "Tester",
        }
        
        await super_admin.handle_event(event)
        
        # Should intervene
        assert len(super_admin.interventions) > 0
        assert any(i["violation_type"] == "LOW_TEST_COVERAGE" for i in super_admin.interventions)
    
    @pytest.mark.asyncio
    async def test_super_admin_resolves_conflict(self):
        """Super Admin çelişkiyi otomatik çöz"""
        
        conflict = {
            "type": "API_MISMATCH",
            "agent_1": "Coder",
            "agent_2": "Reviewer",
            "details": {...},
        }
        
        resolution = await super_admin.conflict_resolver.resolve_conflict(conflict)
        
        assert resolution["resolution"] == "COMPLETED"
        assert resolution["type"] == "AUTO"
    
    def test_report_generation(self):
        """Report'un tam generate edildiğini test et"""
        
        report = super_admin.reporter.generate_comprehensive_report()
        
        assert "executive_summary" in report
        assert "integrity_check_results" in report
        assert "agent_performance" in report
        assert "interventions" in report
        assert "recommendations" in report

BAŞARILI KABUL KRİTERLERİ:
✅ Full pipeline working (Etap 1→2→3)
✅ Super Admin actively supervising
✅ Violations detected & resolved
✅ Reports generated (json + md)
✅ End-to-end tests passing
```

---

## 📋 Özet: Sırayla Verilen Promptlar

### **Etap 1: Clarification Module** (Prompt 1.1 → 1.2 → 1.3 → 1.4)
1. ClarificationAgent tasarımı ve kodlaması
2. Interactive mode entegrasyonu  
3. Brief generation ve TODO list
4. Test & Validation

### **Etap 2: Dynamic Roles System** (Prompt 2.1 → 2.2 → 2.3)
1. DynamicRoleManager tasarımı
2. Task assignment ve execution stratejisi
3. Test & Validation

### **Etap 3: Super Admin Coordinator** (Prompt 3.1 → 3.2 → 3.3 → 3.4 → 3.5)
1. Integrity Checker
2. Conflict Resolver
3. SuperAdminOrchestrator
4. Reporting & Dashboard
5. Integration & Final Testing

---

## 🚀 Deployment Timeline

| Etap | Hafta | Deliverable |
|------|-------|------------|
| 1 | 1-2 | Clarification Module + Tests |
| 2 | 3-6 | Dynamic Roles + Tests |
| 3 | 7-11 | Super Admin + Tests |
| Integration | 12 | Full v7.0 Release |

**Total:** ~12 hafta for YAGO v7.0 🎉