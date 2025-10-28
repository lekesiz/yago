"""
YAGO v8.0 - Package Installer
Install and manage marketplace packages
"""

import logging
import shutil
from typing import Optional, Dict, Any
from pathlib import Path

from .base import MarketplaceItem, ItemType

logger = logging.getLogger(__name__)


class PackageInstaller:
    """
    Install and manage marketplace packages
    """

    def __init__(self, base_path: str = "./yago_plugins"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def install_package(
        self,
        item: MarketplaceItem,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Install a package

        Args:
            item: Item to install
            source: Source URL or path (optional)

        Returns:
            Installation result
        """
        try:
            # Determine installation path
            install_path = self._get_install_path(item)
            install_path.mkdir(parents=True, exist_ok=True)

            # Create metadata file
            self._create_metadata_file(item, install_path)

            # In a real implementation, this would:
            # - Download package from source
            # - Extract files
            # - Install dependencies
            # - Run post-install scripts

            logger.info(
                f"Installed {item.name} to {install_path}"
            )

            return {
                "success": True,
                "item_id": item.item_id,
                "item_name": item.name,
                "version": item.version,
                "install_path": str(install_path),
                "message": f"Successfully installed {item.name}"
            }

        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return {
                "success": False,
                "item_id": item.item_id,
                "error": str(e),
                "message": f"Failed to install {item.name}: {str(e)}"
            }

    def uninstall_package(self, item_id: str, install_path: str) -> Dict[str, Any]:
        """
        Uninstall a package

        Args:
            item_id: Item identifier
            install_path: Installation path

        Returns:
            Uninstallation result
        """
        try:
            path = Path(install_path)

            if not path.exists():
                return {
                    "success": False,
                    "item_id": item_id,
                    "message": "Installation path not found"
                }

            # Remove directory
            if path.is_dir():
                shutil.rmtree(path)

            logger.info(f"Uninstalled package from {install_path}")

            return {
                "success": True,
                "item_id": item_id,
                "message": "Successfully uninstalled package"
            }

        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            return {
                "success": False,
                "item_id": item_id,
                "error": str(e),
                "message": f"Failed to uninstall: {str(e)}"
            }

    def verify_installation(self, install_path: str) -> bool:
        """
        Verify an installation

        Args:
            install_path: Path to verify

        Returns:
            True if valid
        """
        path = Path(install_path)

        if not path.exists():
            return False

        # Check for metadata file
        metadata_file = path / ".yago_metadata.json"
        return metadata_file.exists()

    def _get_install_path(self, item: MarketplaceItem) -> Path:
        """Get installation path"""
        type_dir = self.base_path / item.item_type.value
        type_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize name
        safe_name = "".join(
            c if c.isalnum() or c in ('-', '_') else '_'
            for c in item.name.lower()
        )

        return type_dir / safe_name

    def _create_metadata_file(self, item: MarketplaceItem, install_path: Path):
        """Create metadata file"""
        metadata_file = install_path / ".yago_metadata.json"

        metadata = {
            "item_id": item.item_id,
            "name": item.name,
            "version": item.version,
            "item_type": item.item_type.value,
            "author": item.author,
            "license": item.license
        }

        import json
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
