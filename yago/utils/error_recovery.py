"""
Intelligent Error Recovery System
YAGO v5.2.0

Otomatik hata tespiti ve kurtarma stratejileri.
Profesyonel mod: Durma, otomatik çöz, devam et.
"""

import re
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("YAGO.ErrorRecovery")


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"  # Uyarı, devam edilebilir
    MEDIUM = "medium"  # Otomatik düzeltilebilir
    HIGH = "high"  # Alternatif strateji gerekli
    CRITICAL = "critical"  # Kullanıcı müdahalesi gerekli


@dataclass
class RecoveryStrategy:
    """Recovery strategy for an error"""
    name: str
    severity: ErrorSeverity
    pattern: str  # Regex pattern to match error
    recovery_func: Callable
    description: str
    auto_apply: bool = True  # Otomatik uygula


class ErrorRecoverySystem:
    """
    Intelligent error recovery system

    Automatically detects and recovers from common errors:
    - API limit errors -> Wait and retry
    - Input errors -> Use defaults
    - Context too large -> Truncate and retry
    - Git conflicts -> Auto-resolve
    - File exists -> Auto-overwrite or backup
    """

    def __init__(self, professional_mode: bool = True):
        """
        Initialize error recovery system

        Args:
            professional_mode: If True, auto-recover without user input
        """
        self.professional_mode = professional_mode
        self.recovery_strategies: List[RecoveryStrategy] = []
        self.error_history: List[Dict] = []
        self._register_default_strategies()

    def _register_default_strategies(self):
        """Register default recovery strategies"""

        # 1. EOF/Input errors -> Use default answer
        self.register_strategy(
            name="auto_input_default",
            severity=ErrorSeverity.MEDIUM,
            pattern=r"EOF when reading a line|EOFError",
            recovery_func=self._recover_input_error,
            description="Kullanıcı input hatası: otomatik default cevap kullan"
        )

        # 2. API Rate Limit -> Wait and retry
        self.register_strategy(
            name="api_rate_limit",
            severity=ErrorSeverity.MEDIUM,
            pattern=r"rate[_ ]?limit|429|too many requests",
            recovery_func=self._recover_rate_limit,
            description="API rate limit: bekle ve tekrar dene"
        )

        # 3. Context too large -> Truncate
        self.register_strategy(
            name="context_truncate",
            severity=ErrorSeverity.HIGH,
            pattern=r"context[_ ]?(?:too[_ ]?)?large|maximum context|token limit|Invalid response from LLM",
            recovery_func=self._recover_context_overflow,
            description="Context çok büyük: kısalt ve tekrar dene"
        )

        # 4. File exists -> Auto overwrite
        self.register_strategy(
            name="file_exists",
            severity=ErrorSeverity.LOW,
            pattern=r"file (?:already )?exists|FileExistsError",
            recovery_func=self._recover_file_exists,
            description="Dosya zaten var: otomatik üzerine yaz"
        )

        # 5. API Server Error -> Retry with backoff
        self.register_strategy(
            name="api_server_error",
            severity=ErrorSeverity.HIGH,
            pattern=r"Internal server error|500|502|503|504|api_error",
            recovery_func=self._recover_api_server_error,
            description="API sunucu hatası: bekle ve alternatif yol dene"
        )

        # 6. Git conflicts -> Auto resolve
        self.register_strategy(
            name="git_conflict",
            severity=ErrorSeverity.MEDIUM,
            pattern=r"git[_ ]?conflict|merge conflict",
            recovery_func=self._recover_git_conflict,
            description="Git conflict: otomatik çöz"
        )

        # 6. Permission errors -> Retry with sudo
        self.register_strategy(
            name="permission_error",
            severity=ErrorSeverity.MEDIUM,
            pattern=r"permission denied|PermissionError",
            recovery_func=self._recover_permission_error,
            description="Yetki hatası: alternatif yol dene"
        )

        # 7. Network errors -> Retry
        self.register_strategy(
            name="network_error",
            severity=ErrorSeverity.MEDIUM,
            pattern=r"connection (?:error|refused|timeout)|network error",
            recovery_func=self._recover_network_error,
            description="Ağ hatası: tekrar dene"
        )

        # 8. Import errors -> Install missing package
        self.register_strategy(
            name="import_error",
            severity=ErrorSeverity.MEDIUM,
            pattern=r"ModuleNotFoundError|ImportError|No module named",
            recovery_func=self._recover_import_error,
            description="Import hatası: eksik paketi yükle"
        )

    def register_strategy(self,
                         name: str,
                         severity: ErrorSeverity,
                         pattern: str,
                         recovery_func: Callable,
                         description: str,
                         auto_apply: bool = True):
        """Register a new recovery strategy"""
        strategy = RecoveryStrategy(
            name=name,
            severity=severity,
            pattern=pattern,
            recovery_func=recovery_func,
            description=description,
            auto_apply=auto_apply
        )
        self.recovery_strategies.append(strategy)
        logger.info(f"Registered recovery strategy: {name}")

    def analyze_error(self, error: Exception, context: Optional[str] = None) -> Optional[RecoveryStrategy]:
        """
        Analyze error and find matching recovery strategy

        Args:
            error: Exception object
            context: Additional context (error message, stack trace)

        Returns:
            Matching RecoveryStrategy or None
        """
        error_text = str(error)
        if context:
            error_text += f" {context}"

        error_text = error_text.lower()

        # Find matching strategy
        for strategy in self.recovery_strategies:
            if re.search(strategy.pattern, error_text, re.IGNORECASE):
                logger.info(f"✅ Found recovery strategy: {strategy.name} ({strategy.severity.value})")
                return strategy

        logger.warning(f"❌ No recovery strategy found for error: {error}")
        return None

    def recover(self, error: Exception, context: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Attempt to recover from error

        Args:
            error: Exception object
            context: Additional context
            **kwargs: Additional arguments for recovery function

        Returns:
            Recovery result dict with 'success', 'action', 'message'
        """
        strategy = self.analyze_error(error, context)

        if not strategy:
            return {
                "success": False,
                "action": "no_strategy",
                "message": f"No recovery strategy for: {error}"
            }

        # Record error in history
        self.error_history.append({
            "error": str(error),
            "strategy": strategy.name,
            "severity": strategy.severity.value
        })

        # Apply recovery if professional mode or auto_apply
        if self.professional_mode and strategy.auto_apply:
            logger.info(f"🔧 Applying recovery: {strategy.description}")
            try:
                result = strategy.recovery_func(error, context, **kwargs)
                return {
                    "success": True,
                    "action": strategy.name,
                    "message": strategy.description,
                    "result": result
                }
            except Exception as e:
                logger.error(f"❌ Recovery failed: {e}")
                return {
                    "success": False,
                    "action": strategy.name,
                    "message": f"Recovery failed: {e}"
                }
        else:
            return {
                "success": False,
                "action": "manual_required",
                "message": f"Manual intervention needed: {strategy.description}"
            }

    # Recovery Functions

    def _recover_input_error(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from input/EOF errors by using default answers"""
        logger.info("🔧 Auto-recovery: Using default answer for input prompt")

        # Common defaults based on context
        if "update" in str(context).lower() or "overwrite" in str(context).lower():
            return "u"  # Update
        elif "delete" in str(context).lower():
            return "k"  # Keep
        elif "yes" in str(context).lower() or "no" in str(context).lower():
            return "y"  # Yes
        else:
            return ""  # Empty/default

    def _recover_rate_limit(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from rate limit by waiting"""
        import time
        wait_time = kwargs.get('wait_time', 60)
        logger.info(f"🔧 Auto-recovery: Waiting {wait_time}s for rate limit...")
        time.sleep(wait_time)
        return f"Waited {wait_time}s"

    def _recover_context_overflow(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from context overflow by truncating"""
        logger.info("🔧 Auto-recovery: Truncating context to fit limits")

        max_length = kwargs.get('max_length', 50000)

        # Suggest truncation strategy
        return f"Truncate to {max_length} chars, focus on key files only"

    def _recover_file_exists(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from file exists by overwriting"""
        logger.info("🔧 Auto-recovery: Overwriting existing file")
        return "overwrite"

    def _recover_git_conflict(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from git conflicts"""
        logger.info("🔧 Auto-recovery: Resolving git conflict with 'theirs' strategy")
        return "git merge --strategy-option theirs"

    def _recover_permission_error(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from permission errors"""
        logger.info("🔧 Auto-recovery: Trying alternative path without sudo")
        return "use_alternative_path"

    def _recover_network_error(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from network errors by retrying"""
        import time
        retry_count = kwargs.get('retry_count', 3)
        logger.info(f"🔧 Auto-recovery: Retrying network request ({retry_count} attempts)")
        time.sleep(2)
        return f"retry_{retry_count}"

    def _recover_api_server_error(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from API server errors (500, 502, 503, 504)"""
        import time
        logger.info("🔧 Auto-recovery: API server error detected")

        retry_count = kwargs.get('retry_count', 1)
        max_retries = kwargs.get('max_retries', 3)

        if retry_count < max_retries:
            # Exponential backoff: 2, 4, 8 seconds
            wait_time = 2 ** retry_count
            logger.info(f"⏳ Waiting {wait_time}s before retry ({retry_count}/{max_retries})...")
            time.sleep(wait_time)
            return f"retry_after_{wait_time}s"
        else:
            # Max retries reached, try alternative approach
            logger.warning("⚠️ Max retries reached, switching to alternative method")
            return "use_alternative_method"

    def _recover_import_error(self, error: Exception, context: Optional[str], **kwargs) -> str:
        """Recover from import errors by suggesting package install"""
        import re
        match = re.search(r"No module named ['\"]([^'\"]+)", str(error))
        if match:
            module = match.group(1)
            logger.info(f"🔧 Auto-recovery: Suggesting install for {module}")
            return f"pip install {module}"
        return "check_requirements"

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error recovery statistics"""
        if not self.error_history:
            return {"total": 0, "strategies": {}}

        stats = {
            "total": len(self.error_history),
            "strategies": {}
        }

        for error in self.error_history:
            strategy = error["strategy"]
            stats["strategies"][strategy] = stats["strategies"].get(strategy, 0) + 1

        return stats


# Singleton instance
_error_recovery_instance = None


def get_error_recovery(professional_mode: bool = True) -> ErrorRecoverySystem:
    """Get ErrorRecoverySystem singleton"""
    global _error_recovery_instance
    if _error_recovery_instance is None:
        _error_recovery_instance = ErrorRecoverySystem(professional_mode)
    return _error_recovery_instance


def reset_error_recovery():
    """Reset singleton (for testing)"""
    global _error_recovery_instance
    _error_recovery_instance = None


if __name__ == "__main__":
    # Test error recovery
    recovery = get_error_recovery(professional_mode=True)

    # Test 1: EOF error
    try:
        raise EOFError("EOF when reading a line")
    except Exception as e:
        result = recovery.recover(e, context="update, delete, or keep?")
        print(f"Recovery result: {result}")

    # Test 2: Context overflow
    try:
        raise ValueError("Invalid response from LLM call - None or empty.")
    except Exception as e:
        result = recovery.recover(e, context="Context too large")
        print(f"Recovery result: {result}")

    # Test 3: Stats
    print(f"\nError stats: {recovery.get_error_stats()}")
