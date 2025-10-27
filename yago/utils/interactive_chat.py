"""
Interactive Chat Mode for YAGO
Allows real-time user interaction during code generation
"""

import sys
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger("YAGO")


class InteractiveChat:
    """Handles interactive chat during YAGO execution"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.input_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.conversation_history = []
        self.current_context = {}
        self.input_thread = None
        self.waiting_for_input = False
        self.lock = threading.Lock()

    def start(self):
        """Start the interactive chat system"""
        if not self.enabled:
            return

        logger.info("💬 Interactive chat mode enabled")
        logger.info("   You can provide input when YAGO asks questions")
        logger.info("   Type 'skip' to use default answer")
        logger.info("   Type 'auto' to disable interactive mode\n")

    def ask_question(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        default_answer: Optional[str] = None,
        timeout: int = 30,
    ) -> str:
        """
        Ask user a question and wait for response

        Args:
            question: Question to ask
            context: Additional context information
            default_answer: Default answer if user skips or timeout
            timeout: Seconds to wait for response (0 = infinite)

        Returns:
            User's answer or default answer
        """
        if not self.enabled:
            return default_answer or ""

        with self.lock:
            self.current_context = context or {}

        # Format and display question
        self._display_question(question, default_answer, context)

        # Get user input
        answer = self._get_user_input(timeout)

        # Handle special commands
        if answer.lower() == "skip":
            answer = default_answer or ""
            logger.info(f"   → Using default: {answer}\n")
        elif answer.lower() == "auto":
            self.enabled = False
            logger.info("   → Interactive mode disabled\n")
            answer = default_answer or ""

        # Record in conversation history
        self._record_interaction(question, answer, context)

        return answer

    def ask_choice(
        self,
        question: str,
        choices: list,
        default_index: int = 0,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> str:
        """
        Ask user to choose from multiple options

        Args:
            question: Question to ask
            choices: List of choices
            default_index: Default choice index
            context: Additional context
            timeout: Seconds to wait

        Returns:
            Selected choice
        """
        if not self.enabled:
            return choices[default_index]

        # Display question with choices
        print(f"\n{'='*60}")
        print(f"🤔 {question}")
        print(f"{'='*60}")

        for i, choice in enumerate(choices):
            marker = "→" if i == default_index else " "
            print(f"  {marker} {i+1}. {choice}")

        if context:
            print(f"\nContext: {context}")

        print(f"\nDefault: {choices[default_index]}")
        print(f"Enter number (1-{len(choices)}) or 'skip' for default:")

        # Get input
        answer = self._get_user_input(timeout)

        # Parse choice
        if answer.lower() == "skip" or not answer:
            selected = choices[default_index]
            logger.info(f"   → Using default: {selected}\n")
        elif answer.lower() == "auto":
            self.enabled = False
            selected = choices[default_index]
            logger.info("   → Interactive mode disabled\n")
        else:
            try:
                index = int(answer) - 1
                if 0 <= index < len(choices):
                    selected = choices[index]
                else:
                    logger.warning(f"Invalid choice, using default")
                    selected = choices[default_index]
            except ValueError:
                logger.warning(f"Invalid input, using default")
                selected = choices[default_index]

        # Record interaction
        self._record_interaction(question, selected, context)

        return selected

    def ask_yes_no(
        self,
        question: str,
        default: bool = True,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> bool:
        """
        Ask user a yes/no question

        Args:
            question: Question to ask
            default: Default answer (True/False)
            context: Additional context
            timeout: Seconds to wait

        Returns:
            True for yes, False for no
        """
        default_text = "yes" if default else "no"
        prompt = f"{question} [Y/n]" if default else f"{question} [y/N]"

        answer = self.ask_question(
            prompt, context=context, default_answer=default_text, timeout=timeout
        )

        # Parse yes/no
        answer_lower = answer.lower()
        if answer_lower in ["y", "yes", "true", "1"]:
            return True
        elif answer_lower in ["n", "no", "false", "0"]:
            return False
        else:
            return default

    def notify(self, message: str, emoji: str = "ℹ️"):
        """Send a notification to user (no response needed)"""
        if not self.enabled:
            return

        print(f"\n{emoji} {message}")

    def _display_question(
        self,
        question: str,
        default: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Display a formatted question"""
        print(f"\n{'='*60}")
        print(f"🤔 YAGO Question:")
        print(f"{'='*60}")
        print(f"{question}")

        if context:
            print(f"\nContext:")
            for key, value in context.items():
                print(f"  • {key}: {value}")

        if default:
            print(f"\nDefault answer: {default}")

        print(f"\nYour answer (or 'skip'/'auto'):")
        sys.stdout.flush()

    def _get_user_input(self, timeout: int) -> str:
        """Get user input with optional timeout"""
        if timeout > 0:
            # Use thread-based timeout
            result = {"answer": ""}

            def input_thread():
                try:
                    result["answer"] = input("→ ").strip()
                except EOFError:
                    result["answer"] = ""

            thread = threading.Thread(target=input_thread, daemon=True)
            thread.start()
            thread.join(timeout)

            if thread.is_alive():
                logger.warning(f"\n⏱️  Timeout ({timeout}s), using default answer")
                return ""

            return result["answer"]
        else:
            # No timeout
            try:
                return input("→ ").strip()
            except EOFError:
                return ""

    def _record_interaction(
        self, question: str, answer: str, context: Optional[Dict[str, Any]] = None
    ):
        """Record interaction in history"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "context": context or {},
        }
        self.conversation_history.append(interaction)

    def get_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history

    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "total_interactions": len(self.conversation_history),
            "enabled": self.enabled,
            "history": self.conversation_history,
        }

    def export_history(self, filepath: str = "chat_history.json"):
        """Export conversation history to file"""
        import json

        with open(filepath, "w") as f:
            json.dump(
                {"summary": self.get_summary(), "interactions": self.conversation_history},
                f,
                indent=2,
            )

        logger.info(f"💾 Chat history exported to {filepath}")


# Singleton instance
_interactive_chat: Optional[InteractiveChat] = None


def get_interactive_chat(enabled: bool = True) -> InteractiveChat:
    """Get or create interactive chat singleton"""
    global _interactive_chat
    if _interactive_chat is None:
        _interactive_chat = InteractiveChat(enabled=enabled)
    return _interactive_chat


def reset_interactive_chat(enabled: bool = True):
    """Reset interactive chat (for new run)"""
    global _interactive_chat
    _interactive_chat = InteractiveChat(enabled=enabled)


def ask(question: str, default: Optional[str] = None, **kwargs) -> str:
    """Quick helper to ask a question"""
    chat = get_interactive_chat()
    return chat.ask_question(question, default_answer=default, **kwargs)


def ask_choice(question: str, choices: list, default: int = 0, **kwargs) -> str:
    """Quick helper to ask for choice"""
    chat = get_interactive_chat()
    return chat.ask_choice(question, choices, default_index=default, **kwargs)


def ask_yes_no(question: str, default: bool = True, **kwargs) -> bool:
    """Quick helper to ask yes/no"""
    chat = get_interactive_chat()
    return chat.ask_yes_no(question, default=default, **kwargs)


def notify(message: str, emoji: str = "ℹ️"):
    """Quick helper to send notification"""
    chat = get_interactive_chat()
    chat.notify(message, emoji)
