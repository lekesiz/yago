"""
Interactive Tools for YAGO Agents
Allows agents to ask user questions during execution
"""

from crewai.tools import BaseTool
from typing import Type, Optional, List
from pydantic import BaseModel, Field
from utils.interactive_chat import get_interactive_chat, notify


class AskQuestionInput(BaseModel):
    """Input for AskQuestionTool"""

    question: str = Field(..., description="The question to ask the user")
    default_answer: Optional[str] = Field(
        None, description="Default answer if user skips or timeout"
    )
    context: Optional[str] = Field(
        None, description="Additional context about the question"
    )


class AskQuestionTool(BaseTool):
    name: str = "ask_user"
    description: str = (
        "Ask the user a question and wait for their response. "
        "Use this when you need user input to make decisions. "
        "For example: 'Should I use SQLite or PostgreSQL?', "
        "'What should the API endpoint be named?', "
        "'Do you want error logging enabled?'"
    )
    args_schema: Type[BaseModel] = AskQuestionInput

    def _run(
        self,
        question: str,
        default_answer: Optional[str] = None,
        context: Optional[str] = None,
    ) -> str:
        """Ask user a question"""
        chat = get_interactive_chat()

        context_dict = {"context": context} if context else None

        answer = chat.ask_question(
            question=question, default_answer=default_answer, context=context_dict, timeout=30
        )

        return answer or default_answer or "No answer provided"


class AskChoiceInput(BaseModel):
    """Input for AskChoiceTool"""

    question: str = Field(..., description="The question to ask")
    choices: List[str] = Field(..., description="List of choices")
    default_index: int = Field(0, description="Index of default choice (0-based)")
    context: Optional[str] = Field(None, description="Additional context")


class AskChoiceTool(BaseTool):
    name: str = "ask_user_choice"
    description: str = (
        "Ask the user to choose from multiple options. "
        "Use this when you need user to pick from predefined choices. "
        "For example: 'Which database? [SQLite, PostgreSQL, MySQL]', "
        "'Choose authentication method: [JWT, Session, OAuth]'"
    )
    args_schema: Type[BaseModel] = AskChoiceInput

    def _run(
        self,
        question: str,
        choices: List[str],
        default_index: int = 0,
        context: Optional[str] = None,
    ) -> str:
        """Ask user to choose from options"""
        chat = get_interactive_chat()

        context_dict = {"context": context} if context else None

        answer = chat.ask_choice(
            question=question,
            choices=choices,
            default_index=default_index,
            context=context_dict,
            timeout=30,
        )

        return answer


class AskYesNoInput(BaseModel):
    """Input for AskYesNoTool"""

    question: str = Field(..., description="The yes/no question to ask")
    default: bool = Field(True, description="Default answer (True=yes, False=no)")
    context: Optional[str] = Field(None, description="Additional context")


class AskYesNoTool(BaseTool):
    name: str = "ask_user_yes_no"
    description: str = (
        "Ask the user a yes/no question. "
        "Use this when you need a boolean decision from the user. "
        "For example: 'Should I add logging?', "
        "'Do you want unit tests?', "
        "'Enable debug mode?'"
    )
    args_schema: Type[BaseModel] = AskYesNoInput

    def _run(self, question: str, default: bool = True, context: Optional[str] = None) -> str:
        """Ask user yes/no question"""
        chat = get_interactive_chat()

        context_dict = {"context": context} if context else None

        answer = chat.ask_yes_no(
            question=question, default=default, context=context_dict, timeout=30
        )

        return "yes" if answer else "no"


class NotifyUserInput(BaseModel):
    """Input for NotifyUserTool"""

    message: str = Field(..., description="Message to show to user")
    emoji: str = Field("ℹ️", description="Emoji to show with message")


class NotifyUserTool(BaseTool):
    name: str = "notify_user"
    description: str = (
        "Send a notification message to the user (no response needed). "
        "Use this to inform user about important events or decisions. "
        "For example: 'Starting database migration', "
        "'Generated 10 test cases', "
        "'Found potential security issue'"
    )
    args_schema: Type[BaseModel] = NotifyUserInput

    def _run(self, message: str, emoji: str = "ℹ️") -> str:
        """Notify user with a message"""
        notify(message, emoji)
        return f"User notified: {message}"


# Export all interactive tools
def get_interactive_tools():
    """Get all interactive tools for agents"""
    return [
        AskQuestionTool(),
        AskChoiceTool(),
        AskYesNoTool(),
        NotifyUserTool(),
    ]
