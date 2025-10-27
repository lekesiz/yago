"""
YAGO Logging Handler - API çağrılarını yakalayıp token tracker'a kaydet
"""

import logging
import re
from utils.token_tracker import get_tracker

logger = logging.getLogger("YAGO")


class APILoggingFilter(logging.Filter):
    """API usage loglarını yakalayıp token tracker'a kaydet"""

    def filter(self, record):
        """
        Log record'u filtrele ve API usage'i parse et

        Returns:
            True (her zaman logla, sadece track et)
        """
        msg = record.getMessage()

        # Anthropic API usage yakalama
        if "Anthropic API usage:" in msg:
            self._track_anthropic(msg)

        # OpenAI API usage yakalama
        elif "OpenAI API usage:" in msg:
            self._track_openai(msg)

        # Google API tracking (manual log'dan gelecek)
        elif "Google API usage:" in msg:
            self._track_google(msg)

        return True  # Logu normal şekilde devam ettir

    def _track_anthropic(self, msg):
        """Anthropic API usage'i parse et ve track et"""
        try:
            # Örnek: "Anthropic API usage: {'input_tokens': 599, 'output_tokens': 898, 'total_tokens': 1497}"
            import ast
            match = re.search(r"Anthropic API usage: ({.+})", msg)
            if match:
                tokens = ast.literal_eval(match.group(1))
                tracker = get_tracker()
                tracker.track('anthropic', 'claude-3-5-sonnet-latest', tokens)
        except Exception as e:
            logger.debug(f"Token tracking error (Anthropic): {e}")

    def _track_openai(self, msg):
        """OpenAI API usage'i parse et ve track et"""
        try:
            # Örnek: "OpenAI API usage: {'prompt_tokens': 1515, 'completion_tokens': 2716, 'total_tokens': 4231}"
            import ast
            match = re.search(r"OpenAI API usage: ({.+})", msg)
            if match:
                tokens = ast.literal_eval(match.group(1))
                tracker = get_tracker()
                tracker.track('openai', 'gpt-4o', tokens)
        except Exception as e:
            logger.debug(f"Token tracking error (OpenAI): {e}")

    def _track_google(self, msg):
        """Google API usage'i parse et ve track et"""
        try:
            # Örnek: "Google API usage: {'input_tokens': 100, 'output_tokens': 200, 'total_tokens': 300}"
            import ast
            match = re.search(r"Google API usage: ({.+})", msg)
            if match:
                tokens = ast.literal_eval(match.group(1))
                tracker = get_tracker()
                tracker.track('google', 'gemini-2.0-flash-exp', tokens)
        except Exception as e:
            logger.debug(f"Token tracking error (Google): {e}")


def setup_api_logging():
    """API logging filter'ı root logger'a ekle"""
    root_logger = logging.getLogger()
    api_filter = APILoggingFilter()

    # Tüm handler'lara filter ekle
    for handler in root_logger.handlers:
        handler.addFilter(api_filter)

    logger.info("📊 Token Tracker aktif - API kullanımı izleniyor...")
