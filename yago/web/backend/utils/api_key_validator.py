"""
YAGO v8.3 - API Key Validator
Validates that required API keys are set before starting the application
"""
import os
import sys
from typing import Dict, List, Tuple


class APIKeyValidator:
    """Validate API keys on application startup"""

    # Required keys for production
    REQUIRED_KEYS = [
        "JWT_SECRET_KEY",
    ]

    # At least one AI provider key is required
    AI_PROVIDER_KEYS = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "CURSOR_API_KEY",
    ]

    # Optional keys (will show warnings)
    OPTIONAL_KEYS = [
        "DATABASE_URL",
    ]

    @classmethod
    def validate_all(cls, strict: bool = None) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all API keys

        Args:
            strict: If True, fail on missing optional keys. If None, use ENV variable.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        if strict is None:
            strict = os.getenv("ENV", "development") == "production"

        errors = []
        warnings = []

        # Check required keys
        for key in cls.REQUIRED_KEYS:
            value = os.getenv(key)
            if not value:
                errors.append(f"MISSING REQUIRED: {key} environment variable must be set")
            elif value in ["", "your-key-here", "change-me"]:
                errors.append(f"INVALID VALUE: {key} has placeholder value, set a real key")

        # Check AI provider keys (at least one required)
        ai_keys_present = []
        for key in cls.AI_PROVIDER_KEYS:
            value = os.getenv(key)
            if value and value not in ["", "your-key-here", "change-me"]:
                ai_keys_present.append(key)

        if not ai_keys_present:
            errors.append(
                f"MISSING AI PROVIDER: At least one AI provider API key is required:\n"
                f"  - {', '.join(cls.AI_PROVIDER_KEYS)}"
            )
        else:
            warnings.append(f"AI Providers configured: {', '.join(ai_keys_present)}")

        # Check optional keys
        for key in cls.OPTIONAL_KEYS:
            value = os.getenv(key)
            if not value:
                if strict:
                    warnings.append(f"RECOMMENDED: {key} should be set in production")
                else:
                    warnings.append(f"OPTIONAL: {key} not set (using defaults)")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    @classmethod
    def validate_or_exit(cls, strict: bool = None):
        """
        Validate API keys and exit if validation fails
        """
        is_valid, errors, warnings = cls.validate_all(strict)

        # Print warnings
        if warnings:
            print("\n⚠️  API KEY WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")

        # Print errors and exit if invalid
        if not is_valid:
            print("\n❌ API KEY VALIDATION FAILED:")
            for error in errors:
                print(f"   {error}")
            print("\n📖 Setup Guide:")
            print("   1. Copy .env.example to .env")
            print("   2. Fill in your API keys")
            print("   3. Restart the application")
            print("\n🔑 Generate JWT secret: openssl rand -hex 32")
            sys.exit(1)

        print("\n✅ API key validation passed")
        return True

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of configured AI providers"""
        providers = []
        for key in cls.AI_PROVIDER_KEYS:
            value = os.getenv(key)
            if value and value not in ["", "your-key-here", "change-me"]:
                provider_name = key.replace("_API_KEY", "").lower()
                providers.append(provider_name)
        return providers

    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """Check if a specific provider is configured"""
        key = f"{provider.upper()}_API_KEY"
        value = os.getenv(key)
        return bool(value and value not in ["", "your-key-here", "change-me"])


# Convenience functions
def validate_api_keys(strict: bool = None) -> bool:
    """Validate API keys and return True if valid"""
    is_valid, errors, warnings = APIKeyValidator.validate_all(strict)
    return is_valid


def validate_api_keys_or_exit(strict: bool = None):
    """Validate API keys and exit if invalid"""
    APIKeyValidator.validate_or_exit(strict)


def get_available_providers() -> List[str]:
    """Get list of configured AI providers"""
    return APIKeyValidator.get_available_providers()


def is_provider_available(provider: str) -> bool:
    """Check if a specific provider is configured"""
    return APIKeyValidator.is_provider_available(provider)
