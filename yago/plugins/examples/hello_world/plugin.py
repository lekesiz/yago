"""
YAGO Plugin Example: Hello World
Demonstrates basic plugin structure and functionality
"""

from datetime import datetime
from typing import Dict, Any
import logging

from yago.plugins.core import ToolPlugin, PluginMetadata, PluginContext

logger = logging.getLogger(__name__)


class HelloWorldPlugin(ToolPlugin):
    """
    Simple example plugin that demonstrates:
    - Plugin initialization
    - Configuration handling
    - Tool execution
    - Context usage
    - Health monitoring
    """

    GREETINGS = {
        "formal": {
            "en": "Good day, {name}. How may I assist you today?",
            "fr": "Bonjour, {name}. Comment puis-je vous aider aujourd'hui?",
            "tr": "İyi günler, {name}. Bugün size nasıl yardımcı olabilirim?",
            "de": "Guten Tag, {name}. Wie kann ich Ihnen heute helfen?",
        },
        "casual": {
            "en": "Hey {name}! What's up?",
            "fr": "Salut {name}! Quoi de neuf?",
            "tr": "Selam {name}! Naber?",
            "de": "Hey {name}! Was geht?",
        },
        "friendly": {
            "en": "Hello {name}! Nice to see you!",
            "fr": "Bonjour {name}! Ravi de vous voir!",
            "tr": "Merhaba {name}! Seni görmek güzel!",
            "de": "Hallo {name}! Schön dich zu sehen!",
        }
    }

    async def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            logger.info(f"Initializing {self.metadata.name}")

            # Set up initial context data
            self.context.set_data("initialized_at", datetime.utcnow().isoformat())
            self.context.set_data("greeting_count", 0)

            logger.info(f"{self.metadata.name} initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Error initializing HelloWorldPlugin: {e}")
            return False

    async def execute(self, input_data: Any = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the plugin - generate a greeting

        Args:
            input_data: Dict with optional 'name' key
            **kwargs: Additional arguments

        Returns:
            Dict with greeting and metadata
        """
        try:
            # Get configuration
            style = self.context.get_config("greeting_style", "friendly")
            include_time = self.context.get_config("include_time", True)
            language = self.context.get_config("language", "en")

            # Get name from input
            name = "Friend"
            if isinstance(input_data, dict):
                name = input_data.get("name", "Friend")
            elif isinstance(input_data, str):
                name = input_data

            # Generate greeting
            greeting_template = self.GREETINGS.get(style, self.GREETINGS["friendly"])
            greeting = greeting_template.get(language, greeting_template["en"])
            greeting = greeting.format(name=name)

            # Add time if configured
            if include_time:
                current_time = datetime.now().strftime("%H:%M")
                greeting += f" (Current time: {current_time})"

            # Update greeting count
            count = self.context.get_data("greeting_count", 0)
            self.context.set_data("greeting_count", count + 1)

            result = {
                "greeting": greeting,
                "name": name,
                "style": style,
                "language": language,
                "timestamp": datetime.utcnow().isoformat(),
                "greeting_number": count + 1
            }

            logger.info(f"Generated greeting for {name}")
            return result

        except Exception as e:
            logger.error(f"Error executing HelloWorldPlugin: {e}")
            return {
                "error": str(e),
                "greeting": "Hello! (Error occurred)",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def invoke(self, *args, **kwargs) -> str:
        """
        Tool-specific invocation method

        Returns:
            Simple greeting string
        """
        result = await self.execute(*args, **kwargs)
        return result.get("greeting", "Hello!")

    def get_schema(self) -> Dict[str, Any]:
        """
        Get tool schema for LLM integration

        Returns:
            JSON schema describing the tool
        """
        return {
            "name": "greet",
            "description": "Generate a personalized greeting message",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the person to greet",
                        "default": "Friend"
                    }
                }
            },
            "returns": {
                "type": "object",
                "properties": {
                    "greeting": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "greeting_number": {"type": "integer"}
                }
            }
        }

    async def validate(self) -> bool:
        """Validate plugin configuration"""
        try:
            style = self.context.get_config("greeting_style")
            if style and style not in self.GREETINGS:
                logger.error(f"Invalid greeting style: {style}")
                return False

            language = self.context.get_config("language")
            if language:
                valid_languages = set()
                for style_greetings in self.GREETINGS.values():
                    valid_languages.update(style_greetings.keys())

                if language not in valid_languages:
                    logger.error(f"Invalid language: {language}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check plugin health"""
        health = await super().health_check()

        # Add custom health metrics
        health.update({
            "greeting_count": self.context.get_data("greeting_count", 0),
            "initialized_at": self.context.get_data("initialized_at"),
            "config_valid": await self.validate()
        })

        return health

    async def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        try:
            logger.info(f"Cleaning up {self.metadata.name}")

            # Log final stats
            count = self.context.get_data("greeting_count", 0)
            logger.info(f"Total greetings generated: {count}")

            return True

        except Exception as e:
            logger.error(f"Error cleaning up HelloWorldPlugin: {e}")
            return False
