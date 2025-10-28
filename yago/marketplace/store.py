"""
YAGO v8.0 - Marketplace Store
Manage installations and purchases
"""

import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from .base import (
    MarketplaceItem,
    InstallationRecord,
    ItemType,
)
from .registry import MarketplaceRegistry

logger = logging.getLogger(__name__)


class MarketplaceStore:
    """
    Manage marketplace installations
    """

    def __init__(
        self,
        registry: MarketplaceRegistry,
        installation_dir: str = "./yago_plugins"
    ):
        self.registry = registry
        self.installation_dir = Path(installation_dir)
        self.installations: Dict[str, InstallationRecord] = {}

        # Create installation directory
        self.installation_dir.mkdir(parents=True, exist_ok=True)

    def install_item(
        self,
        item_id: str,
        auto_update: bool = False,
        configuration: Optional[Dict] = None
    ) -> Optional[InstallationRecord]:
        """
        Install a marketplace item

        Args:
            item_id: Item to install
            auto_update: Enable auto-updates
            configuration: Installation configuration

        Returns:
            Installation record or None if failed
        """
        # Get item
        item = self.registry.get_item(item_id)

        if not item:
            logger.error(f"Item not found: {item_id}")
            return None

        # Check if already installed
        existing = self.get_installation(item_id)
        if existing:
            logger.warning(f"Item already installed: {item_id}")
            return existing

        # Determine installation path
        install_path = self._get_installation_path(item)

        # Create installation record
        installation = InstallationRecord(
            installation_id=f"install_{uuid.uuid4().hex[:12]}",
            item_id=item_id,
            item_type=item.item_type,
            version=item.version,
            installed_at=datetime.utcnow(),
            installation_path=str(install_path),
            active=True,
            auto_update=auto_update,
            configuration=configuration or {}
        )

        # Store installation
        self.installations[item_id] = installation

        # Increment download count
        self.registry.increment_downloads(item_id)

        logger.info(
            f"Installed {item.item_type.value}: {item.name} "
            f"(version {item.version})"
        )

        return installation

    def uninstall_item(self, item_id: str) -> bool:
        """
        Uninstall a marketplace item

        Args:
            item_id: Item to uninstall

        Returns:
            True if successful
        """
        if item_id not in self.installations:
            logger.error(f"Item not installed: {item_id}")
            return False

        installation = self.installations[item_id]

        # Deactivate
        installation.active = False

        # Remove from installations
        del self.installations[item_id]

        logger.info(f"Uninstalled item: {item_id}")
        return True

    def update_item(
        self,
        item_id: str,
        target_version: Optional[str] = None
    ) -> bool:
        """
        Update an installed item

        Args:
            item_id: Item to update
            target_version: Specific version to update to (None = latest)

        Returns:
            True if successful
        """
        installation = self.get_installation(item_id)

        if not installation:
            logger.error(f"Item not installed: {item_id}")
            return False

        item = self.registry.get_item(item_id)

        if not item:
            logger.error(f"Item not found: {item_id}")
            return False

        # Get target version
        new_version = target_version or item.version

        if new_version == installation.version:
            logger.info(f"Item already at version {new_version}")
            return True

        # Update installation
        installation.version = new_version
        installation.last_updated = datetime.utcnow()

        logger.info(
            f"Updated {item.name} from {installation.version} to {new_version}"
        )

        return True

    def get_installation(self, item_id: str) -> Optional[InstallationRecord]:
        """Get installation record"""
        return self.installations.get(item_id)

    def list_installations(
        self,
        item_type: Optional[ItemType] = None,
        active_only: bool = True
    ) -> List[InstallationRecord]:
        """
        List all installations

        Args:
            item_type: Filter by type
            active_only: Only active installations

        Returns:
            List of installations
        """
        installations = list(self.installations.values())

        if item_type:
            installations = [
                i for i in installations
                if i.item_type == item_type
            ]

        if active_only:
            installations = [i for i in installations if i.active]

        # Sort by installation date
        installations.sort(key=lambda i: i.installed_at, reverse=True)

        return installations

    def is_installed(self, item_id: str) -> bool:
        """Check if item is installed"""
        return item_id in self.installations and self.installations[item_id].active

    def get_installed_count(self) -> int:
        """Get count of installed items"""
        return len([i for i in self.installations.values() if i.active])

    def check_updates(self) -> List[Dict]:
        """
        Check for available updates

        Returns:
            List of items with available updates
        """
        updates = []

        for installation in self.installations.values():
            if not installation.active:
                continue

            item = self.registry.get_item(installation.item_id)

            if not item:
                continue

            # Check if newer version available
            if item.version != installation.version:
                updates.append({
                    "item_id": installation.item_id,
                    "name": item.name,
                    "current_version": installation.version,
                    "latest_version": item.version,
                    "auto_update": installation.auto_update
                })

        return updates

    def enable_item(self, item_id: str) -> bool:
        """Enable an installed item"""
        installation = self.get_installation(item_id)

        if not installation:
            return False

        installation.active = True
        logger.info(f"Enabled item: {item_id}")
        return True

    def disable_item(self, item_id: str) -> bool:
        """Disable an installed item"""
        installation = self.get_installation(item_id)

        if not installation:
            return False

        installation.active = False
        logger.info(f"Disabled item: {item_id}")
        return True

    def configure_item(self, item_id: str, configuration: Dict) -> bool:
        """
        Update item configuration

        Args:
            item_id: Item to configure
            configuration: New configuration

        Returns:
            True if successful
        """
        installation = self.get_installation(item_id)

        if not installation:
            return False

        installation.configuration.update(configuration)
        logger.info(f"Updated configuration for: {item_id}")
        return True

    def _get_installation_path(self, item: MarketplaceItem) -> Path:
        """Get installation path for an item"""
        item_type_dir = self.installation_dir / item.item_type.value
        item_type_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize name for filesystem
        safe_name = "".join(
            c if c.isalnum() or c in ('-', '_') else '_'
            for c in item.name.lower()
        )

        return item_type_dir / safe_name
