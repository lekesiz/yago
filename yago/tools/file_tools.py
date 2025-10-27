"""
YAGO File Tools - Güvenli dosya işlemleri
Sadece workspace/ dizininde çalışır
"""

import os
from pathlib import Path
from typing import Optional
from crewai.tools import tool

WORKSPACE_DIR = "./workspace"


class FileTools:
    """Sandbox içinde güvenli dosya işlemleri"""

    @staticmethod
    def _get_safe_path(path: str) -> Path:
        """Path'i workspace içine sınırla"""
        workspace = Path(WORKSPACE_DIR).resolve()
        target = (workspace / path).resolve()

        # Security check: path traversal prevention
        if not str(target).startswith(str(workspace)):
            raise ValueError(f"Güvenlik hatası: {path} workspace dışında!")

        return target

    @tool("Dosyaya Yaz")
    def write_file(path: str, content: str) -> str:
        """
        İçeriği belirtilen dosyaya yazar.
        Sadece workspace/ içinde çalışır.

        Args:
            path: Dosya yolu (workspace'e göre relative)
            content: Yazılacak içerik

        Returns:
            Başarı mesajı
        """
        try:
            target = FileTools._get_safe_path(path)
            target.parent.mkdir(parents=True, exist_ok=True)

            with open(target, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"✓ Dosya yazıldı: {target.relative_to(Path(WORKSPACE_DIR).resolve())}"

        except Exception as e:
            return f"✗ Hata: {str(e)}"

    @tool("Dosyayı Oku")
    def read_file(path: str) -> str:
        """
        Belirtilen dosyayı okur.
        Sadece workspace/ içinde çalışır.

        Args:
            path: Dosya yolu (workspace'e göre relative)

        Returns:
            Dosya içeriği veya hata mesajı
        """
        try:
            target = FileTools._get_safe_path(path)

            if not target.exists():
                return f"✗ Dosya bulunamadı: {path}"

            with open(target, 'r', encoding='utf-8') as f:
                content = f.read()

            return content

        except Exception as e:
            return f"✗ Hata: {str(e)}"

    @tool("Dosya Listele")
    def list_files(directory: str = ".") -> str:
        """
        Belirtilen dizindeki dosyaları listeler.

        Args:
            directory: Dizin yolu (workspace'e göre relative)

        Returns:
            Dosya listesi
        """
        try:
            target = FileTools._get_safe_path(directory)

            if not target.exists():
                return f"✗ Dizin bulunamadı: {directory}"

            if not target.is_dir():
                return f"✗ Bu bir dizin değil: {directory}"

            files = []
            for item in sorted(target.iterdir()):
                rel_path = item.relative_to(Path(WORKSPACE_DIR).resolve())
                file_type = "📁" if item.is_dir() else "📄"
                files.append(f"{file_type} {rel_path}")

            return "\n".join(files) if files else "Dizin boş"

        except Exception as e:
            return f"✗ Hata: {str(e)}"

    @tool("Dosya Sil")
    def delete_file(path: str) -> str:
        """
        Belirtilen dosyayı siler.

        Args:
            path: Dosya yolu

        Returns:
            Başarı mesajı
        """
        try:
            target = FileTools._get_safe_path(path)

            if not target.exists():
                return f"✗ Dosya zaten yok: {path}"

            if target.is_dir():
                return f"✗ Dizin silinemez (güvenlik): {path}"

            target.unlink()
            return f"✓ Dosya silindi: {path}"

        except Exception as e:
            return f"✗ Hata: {str(e)}"
