"""
YAGO Terminal Tools - Güvenli terminal komutları
Sadece workspace/ dizininde çalışır
"""

import subprocess
from pathlib import Path
from typing import List
from crewai.tools import tool

WORKSPACE_DIR = "./workspace"

# Güvenlik: Yasaklı komutlar
BLOCKED_COMMANDS = [
    "rm -rf /",
    "sudo",
    "chmod 777",
    "curl",
    "wget",
    "dd",
    "mkfs",
    "shutdown",
    "reboot",
]


class TerminalTools:
    """Sandbox içinde güvenli terminal işlemleri"""

    @staticmethod
    def _is_safe_command(command: str) -> bool:
        """Komutun güvenli olup olmadığını kontrol eder"""
        command_lower = command.lower()

        for blocked in BLOCKED_COMMANDS:
            if blocked in command_lower:
                return False

        return True

    @tool("Terminal Komutu Çalıştır")
    def run_command(command: str, timeout: int = 30) -> str:
        """
        Belirtilen terminal komutunu workspace dizininde çalıştırır.

        Args:
            command: Çalıştırılacak komut
            timeout: Maksimum çalışma süresi (saniye)

        Returns:
            Komut çıktısı veya hata mesajı
        """
        # Güvenlik kontrolü
        if not TerminalTools._is_safe_command(command):
            return f"✗ GÜVENLİK HATASI: Bu komut yasaklanmıştır: {command}"

        try:
            workspace_path = Path(WORKSPACE_DIR).resolve()
            workspace_path.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                command,
                shell=True,
                cwd=str(workspace_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )

            output = []
            if result.stdout:
                output.append(f"📤 Çıktı:\n{result.stdout}")
            if result.stderr:
                output.append(f"⚠️  Hata:\n{result.stderr}")
            if result.returncode != 0:
                output.append(f"❌ Exit code: {result.returncode}")
            else:
                output.append(f"✅ Başarılı (exit code: 0)")

            return "\n".join(output) if output else "Komut çıktısız tamamlandı"

        except subprocess.TimeoutExpired:
            return f"✗ Timeout: Komut {timeout} saniyede tamamlanamadı"
        except Exception as e:
            return f"✗ Hata: {str(e)}"

    @tool("Python Kodu Çalıştır")
    def run_python(script_path: str) -> str:
        """
        Workspace içindeki Python dosyasını çalıştırır.

        Args:
            script_path: Python dosya yolu

        Returns:
            Çıktı veya hata
        """
        if not script_path.endswith('.py'):
            return "✗ Sadece .py uzantılı dosyalar çalıştırılabilir"

        command = f"python3 {script_path}"
        return TerminalTools.run_command(command)

    @tool("Test Çalıştır")
    def run_tests(test_path: str = "tests/") -> str:
        """
        Pytest ile testleri çalıştırır.

        Args:
            test_path: Test dizini veya dosyası

        Returns:
            Test sonuçları
        """
        command = f"pytest {test_path} -v --tb=short"
        return TerminalTools.run_command(command, timeout=60)
