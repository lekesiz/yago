"""
YAGO v8.0 - AI-Powered Clarification Service
Generates dynamic questions and analyzes answers using AI
Multi-provider support: OpenAI, Anthropic, Google Gemini, Cursor
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
import json
import anthropic
import google.generativeai as genai
import requests

class AIClarificationService:
    """AI service for dynamic question generation and answer analysis"""

    def __init__(self):
        # Initialize all AI providers
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Configure Google Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Cursor API configuration
        self.cursor_api_key = os.getenv("CURSOR_API_KEY")
        self.cursor_api_url = "https://api.cursor.sh/v1/chat/completions"

        # Model configurations
        self.models = {
            "openai": {
                "quick": "gpt-3.5-turbo",
                "detailed": "gpt-4-turbo-preview"
            },
            "anthropic": {
                "quick": "claude-3-haiku-20240307",
                "detailed": "claude-3-opus-20240229"
            },
            "gemini": {
                "quick": "gemini-pro",
                "detailed": "gemini-pro"
            },
            "cursor": {
                "quick": "cursor-small",
                "detailed": "cursor-large"
            }
        }

        # Default provider for different tasks
        self.question_provider = "openai"  # Fast questions with GPT-3.5
        self.brief_provider = "anthropic"   # Detailed brief with Claude Opus
        self.analysis_provider = "gemini"   # Quick analysis with Gemini

    def _call_ai_provider(
        self,
        provider: str,
        prompt: str,
        system_message: str,
        task_type: str = "quick"
    ) -> str:
        """Universal AI provider caller with fallback support"""
        try:
            if provider == "openai":
                response = self.openai_client.chat.completions.create(
                    model=self.models["openai"][task_type],
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=3000 if task_type == "quick" else 4000
                )
                return response.choices[0].message.content.strip()

            elif provider == "anthropic":
                response = self.anthropic_client.messages.create(
                    model=self.models["anthropic"][task_type],
                    max_tokens=3000 if task_type == "quick" else 4000,
                    system=system_message,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif provider == "gemini":
                model = genai.GenerativeModel(self.models["gemini"][task_type])
                response = model.generate_content(f"{system_message}\n\n{prompt}")
                return response.text

            elif provider == "cursor":
                response = requests.post(
                    self.cursor_api_url,
                    headers={
                        "Authorization": f"Bearer {self.cursor_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.models["cursor"][task_type],
                        "messages": [
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 3000 if task_type == "quick" else 4000
                    },
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"Cursor API error: {response.status_code}")

        except Exception as e:
            print(f"❌ {provider} failed: {e}")
            # Try fallback provider
            if provider != "openai":
                print(f"🔄 Falling back to OpenAI...")
                return self._call_ai_provider("openai", prompt, system_message, task_type)
            raise

    def generate_questions(
        self,
        project_idea: str,
        depth: str = "standard",
        previous_answers: Optional[Dict] = None,
        provider: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate dynamic questions using multi-provider AI

        Args:
            project_idea: The user's project description
            depth: minimal (10), standard (20), or full (40)
            previous_answers: Previous answers for context-aware follow-ups
            provider: Specific provider to use (openai, anthropic, gemini, cursor)

        Returns:
            List of question objects with id, text, type, required, category
        """
        # Use specified provider or default
        provider = provider or self.question_provider

        # Determine question count based on depth
        question_counts = {
            "minimal": 10,
            "standard": 20,
            "full": 40
        }
        target_count = question_counts.get(depth, 20)

        print(f"🤖 Using {provider.upper()} for question generation")

        # Build context from previous answers
        context = ""
        if previous_answers:
            context = "\n\nPrevious answers for context:\n"
            for qid, answer in previous_answers.items():
                context += f"- {qid}: {answer}\n"

        # Create the prompt
        prompt = f"""You are an expert software architect conducting a project requirements gathering session.

Project Idea: {project_idea}{context}

Generate EXACTLY {target_count} questions to fully understand this project. Questions should cover:

1. **Basic Requirements** (20%): Core purpose, target audience, main features
2. **Technical Specifications** (30%): Tech stack, architecture, integrations, scalability
3. **User Experience** (15%): UI/UX requirements, user flows, accessibility
4. **Quality Attributes** (15%): Performance, security, reliability requirements
5. **Business Context** (10%): Timeline, budget, success metrics
6. **Advanced Features** (10%): Optional features, future enhancements

Question types:
- "text": Open-ended text input
- "select": Multiple choice (provide options array)
- "multiselect": Multiple selection (provide options array)
- "number": Numeric input
- "boolean": Yes/No

Required format (JSON array):
[
  {{
    "id": "q1",
    "text": "What is the primary goal of this project?",
    "type": "text",
    "required": true,
    "category": "basic",
    "placeholder": "e.g., Increase user engagement by 50%"
  }},
  {{
    "id": "q2",
    "text": "What is your preferred tech stack?",
    "type": "select",
    "required": false,
    "category": "technical",
    "options": ["React + Node.js", "Vue + Python", "Angular + Java", "Other"]
  }}
]

IMPORTANT:
- Generate EXACTLY {target_count} questions
- Mix required (40%) and optional (60%) questions
- Include specific, actionable questions
- Add helpful placeholders for text fields
- Provide relevant options for select fields
- Questions should build upon each other logically

Return ONLY the JSON array, no other text."""

        try:
            # Call AI provider
            content = self._call_ai_provider(
                provider=provider,
                prompt=prompt,
                system_message="You are an expert software architect. Return only valid JSON.",
                task_type="quick"
            )

            # Parse JSON response
            questions = json.loads(content)

            # Validate and ensure correct count
            if len(questions) < target_count:
                print(f"⚠️ Warning: Generated {len(questions)} questions, expected {target_count}")

            return questions[:target_count]  # Ensure we don't exceed target

        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Response: {content[:500]}")
            # Return fallback questions
            return self._get_fallback_questions(target_count)
        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            return self._get_fallback_questions(target_count)

    def analyze_answer(
        self,
        question: Dict,
        answer: str,
        project_context: Dict
    ) -> Dict:
        """
        Analyze a single answer and determine if follow-up is needed

        Returns:
            {
                "needs_followup": bool,
                "followup_question": Optional[Dict],
                "insights": str
            }
        """
        if not answer or len(str(answer).strip()) < 3:
            return {"needs_followup": False, "insights": ""}

        prompt = f"""Analyze this answer in the context of a software project:

Question: {question['text']}
Answer: {answer}
Project: {project_context.get('project_idea', 'Unknown')}

Determine:
1. Is the answer clear and sufficient?
2. Should we ask a follow-up question for clarification?
3. What insights can we extract?

Return JSON:
{{
  "needs_followup": true/false,
  "followup_question": {{"id": "f1", "text": "...", "type": "text", "required": false, "category": "{question.get('category', 'basic')}"}},
  "insights": "Key takeaway from this answer"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.gpt35_model,
                messages=[
                    {"role": "system", "content": "You are an expert analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )

            return json.loads(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"❌ Error analyzing answer: {e}")
            return {"needs_followup": False, "insights": ""}

    def generate_comprehensive_brief(
        self,
        project_idea: str,
        all_answers: Dict,
        questions: List[Dict],
        provider: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive project brief using multi-provider AI

        Returns detailed brief with all specifications
        """
        # Use specified provider or default
        provider = provider or self.brief_provider
        print(f"📝 Using {provider.upper()} for brief generation")
        # Build Q&A pairs
        qa_text = ""
        for q in questions:
            qid = q['id']
            if qid in all_answers:
                qa_text += f"\nQ: {q['text']}\nA: {all_answers[qid]}\n"

        prompt = f"""You are an expert software architect creating a comprehensive project brief.

Original Idea: {project_idea}

Clarification Q&A:
{qa_text}

Create a detailed project brief that includes:

1. **Executive Summary**: 2-3 sentences capturing the essence
2. **Project Scope**: Detailed description of what will be built
3. **Target Audience**: Who will use this and their needs
4. **Core Features**: List of must-have features (prioritized)
5. **Technical Requirements**:
   - Recommended tech stack
   - Architecture approach
   - Key integrations
   - Performance requirements
6. **Quality Attributes**:
   - Security considerations
   - Scalability needs
   - Reliability requirements
7. **User Experience**:
   - Key user flows
   - UI/UX priorities
8. **Success Metrics**: How to measure success
9. **Timeline Estimate**: Realistic development timeline
10. **Budget Estimate**: Rough cost estimate
11. **Risks & Challenges**: Potential issues to consider
12. **Recommendations**: Expert suggestions for success

Return JSON format:
{{
  "executive_summary": "...",
  "project_scope": "...",
  "target_audience": "...",
  "core_features": ["feature 1", "feature 2", ...],
  "technical_requirements": {{
    "tech_stack": ["React", "Node.js", ...],
    "architecture": "...",
    "integrations": [...],
    "performance": "..."
  }},
  "quality_attributes": {{...}},
  "user_experience": {{...}},
  "success_metrics": [...],
  "timeline": "...",
  "budget_range": "...",
  "risks": [...],
  "recommendations": [...]
}}"""

        try:
            # Call AI provider
            content = self._call_ai_provider(
                provider=provider,
                prompt=prompt,
                system_message="You are an expert software architect with 20 years of experience. Create detailed, actionable project briefs. Return only valid JSON.",
                task_type="detailed"
            )

            brief = json.loads(content)

            # Add metadata
            brief["project_idea"] = project_idea
            brief["total_questions"] = len(questions)
            brief["answered_questions"] = len(all_answers)
            brief["completion_rate"] = (len(all_answers) / len(questions) * 100) if questions else 0

            return brief

        except Exception as e:
            print(f"❌ Error generating brief: {e}")
            return self._get_fallback_brief(project_idea, all_answers)

    def _get_fallback_questions(self, count: int) -> List[Dict]:
        """Return basic fallback questions if AI fails"""
        base_questions = [
            {"id": "q1", "text": "What is the primary purpose of your project?", "type": "text", "required": True, "category": "basic"},
            {"id": "q2", "text": "Who is your target audience?", "type": "text", "required": True, "category": "basic"},
            {"id": "q3", "text": "What are the main features you need?", "type": "text", "required": True, "category": "basic"},
            {"id": "q4", "text": "What is your preferred tech stack?", "type": "select", "required": False, "category": "technical",
             "options": ["React + Node.js", "Vue + Python", "Angular + Java", "No preference"]},
            {"id": "q5", "text": "What is your expected timeline?", "type": "select", "required": False, "category": "business",
             "options": ["1-2 weeks", "1 month", "2-3 months", "3+ months"]},
            {"id": "q6", "text": "What is your budget range?", "type": "select", "required": False, "category": "business",
             "options": ["<$1000", "$1000-$5000", "$5000-$10000", "$10000+"]},
            {"id": "q7", "text": "Do you need user authentication?", "type": "boolean", "required": False, "category": "technical"},
            {"id": "q8", "text": "Do you need a database?", "type": "boolean", "required": False, "category": "technical"},
            {"id": "q9", "text": "Any specific design requirements?", "type": "text", "required": False, "category": "ux"},
            {"id": "q10", "text": "Any additional requirements?", "type": "text", "required": False, "category": "quality"}
        ]

        # Repeat and extend if needed
        while len(base_questions) < count:
            base_questions.append({
                "id": f"q{len(base_questions) + 1}",
                "text": f"Additional requirement #{len(base_questions) - 9}?",
                "type": "text",
                "required": False,
                "category": "quality"
            })

        return base_questions[:count]

    def _get_fallback_brief(self, project_idea: str, answers: Dict) -> Dict:
        """Return basic fallback brief if AI fails"""
        return {
            "executive_summary": f"Project: {project_idea}",
            "project_scope": "A software project to be defined",
            "target_audience": "General users",
            "core_features": ["Core functionality"],
            "technical_requirements": {
                "tech_stack": ["To be determined"],
                "architecture": "Standard web architecture",
                "integrations": [],
                "performance": "Standard"
            },
            "quality_attributes": {},
            "user_experience": {},
            "success_metrics": [],
            "timeline": "To be determined",
            "budget_range": "To be estimated",
            "risks": [],
            "recommendations": [],
            "project_idea": project_idea,
            "total_questions": 0,
            "answered_questions": len(answers),
            "completion_rate": 0
        }

# Singleton instance
_ai_service = None

def get_ai_clarification_service() -> AIClarificationService:
    """Get or create the AI clarification service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIClarificationService()
    return _ai_service
