"""
YAGO v8.0 - Item Validator
Validate marketplace items before publishing
"""

import logging
import re
from typing import List, Dict, Any

from .base import MarketplaceItem, Plugin, Template, Integration

logger = logging.getLogger(__name__)


class ValidationError:
    """Validation error"""

    def __init__(self, field: str, message: str, severity: str = "error"):
        self.field = field
        self.message = message
        self.severity = severity  # error, warning, info

    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity
        }


class ItemValidator:
    """
    Validate marketplace items
    """

    def __init__(self):
        self.min_name_length = 3
        self.max_name_length = 100
        self.min_description_length = 20
        self.max_description_length = 500
        self.version_pattern = re.compile(r'^\d+\.\d+\.\d+$')

    def validate_item(self, item: MarketplaceItem) -> tuple[bool, List[ValidationError]]:
        """
        Validate a marketplace item

        Args:
            item: Item to validate

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Common validations
        errors.extend(self._validate_name(item.name))
        errors.extend(self._validate_description(item.description))
        errors.extend(self._validate_version(item.version))
        errors.extend(self._validate_author(item.author))
        errors.extend(self._validate_tags(item.tags))
        errors.extend(self._validate_license(item.license))

        # Type-specific validations
        if isinstance(item, Plugin):
            errors.extend(self._validate_plugin(item))
        elif isinstance(item, Template):
            errors.extend(self._validate_template(item))
        elif isinstance(item, Integration):
            errors.extend(self._validate_integration(item))

        # Check if any critical errors
        has_errors = any(e.severity == "error" for e in errors)

        return not has_errors, errors

    def _validate_name(self, name: str) -> List[ValidationError]:
        """Validate item name"""
        errors = []

        if not name:
            errors.append(ValidationError("name", "Name is required"))
            return errors

        if len(name) < self.min_name_length:
            errors.append(
                ValidationError(
                    "name",
                    f"Name must be at least {self.min_name_length} characters"
                )
            )

        if len(name) > self.max_name_length:
            errors.append(
                ValidationError(
                    "name",
                    f"Name must not exceed {self.max_name_length} characters"
                )
            )

        # Check for special characters
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            errors.append(
                ValidationError(
                    "name",
                    "Name contains invalid characters",
                    "warning"
                )
            )

        return errors

    def _validate_description(self, description: str) -> List[ValidationError]:
        """Validate description"""
        errors = []

        if not description:
            errors.append(ValidationError("description", "Description is required"))
            return errors

        if len(description) < self.min_description_length:
            errors.append(
                ValidationError(
                    "description",
                    f"Description must be at least {self.min_description_length} characters"
                )
            )

        if len(description) > self.max_description_length:
            errors.append(
                ValidationError(
                    "description",
                    f"Description must not exceed {self.max_description_length} characters"
                )
            )

        return errors

    def _validate_version(self, version: str) -> List[ValidationError]:
        """Validate semantic version"""
        errors = []

        if not version:
            errors.append(ValidationError("version", "Version is required"))
            return errors

        if not self.version_pattern.match(version):
            errors.append(
                ValidationError(
                    "version",
                    "Version must follow semantic versioning (e.g., 1.0.0)"
                )
            )

        return errors

    def _validate_author(self, author: str) -> List[ValidationError]:
        """Validate author"""
        errors = []

        if not author:
            errors.append(ValidationError("author", "Author is required"))
            return errors

        if len(author) < 2:
            errors.append(
                ValidationError("author", "Author name too short")
            )

        return errors

    def _validate_tags(self, tags: List[str]) -> List[ValidationError]:
        """Validate tags"""
        errors = []

        if not tags:
            errors.append(
                ValidationError(
                    "tags",
                    "At least one tag is recommended",
                    "warning"
                )
            )
            return errors

        if len(tags) > 10:
            errors.append(
                ValidationError("tags", "Maximum 10 tags allowed")
            )

        # Check individual tags
        for tag in tags:
            if len(tag) < 2:
                errors.append(
                    ValidationError(
                        "tags",
                        f"Tag '{tag}' too short",
                        "warning"
                    )
                )

            if len(tag) > 30:
                errors.append(
                    ValidationError(
                        "tags",
                        f"Tag '{tag}' too long",
                        "warning"
                    )
                )

        return errors

    def _validate_license(self, license: str) -> List[ValidationError]:
        """Validate license"""
        errors = []

        if not license:
            errors.append(
                ValidationError(
                    "license",
                    "License is required",
                    "warning"
                )
            )

        # Common open source licenses
        common_licenses = [
            "MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause",
            "ISC", "MPL-2.0", "LGPL-3.0"
        ]

        if license not in common_licenses:
            errors.append(
                ValidationError(
                    "license",
                    f"Uncommon license: {license}. Consider using a standard license.",
                    "info"
                )
            )

        return errors

    def _validate_plugin(self, plugin: Plugin) -> List[ValidationError]:
        """Validate plugin-specific fields"""
        errors = []

        if not plugin.entry_point:
            errors.append(
                ValidationError("entry_point", "Entry point is required for plugins")
            )

        if not plugin.plugin_type:
            errors.append(
                ValidationError("plugin_type", "Plugin type is required")
            )

        # Validate entry point format (module:class)
        if plugin.entry_point and ':' not in plugin.entry_point:
            errors.append(
                ValidationError(
                    "entry_point",
                    "Entry point must be in format 'module:class'",
                    "warning"
                )
            )

        return errors

    def _validate_template(self, template: Template) -> List[ValidationError]:
        """Validate template-specific fields"""
        errors = []

        if not template.template_type:
            errors.append(
                ValidationError("template_type", "Template type is required")
            )

        if not template.variables:
            errors.append(
                ValidationError(
                    "variables",
                    "Template should define variables",
                    "warning"
                )
            )

        return errors

    def _validate_integration(self, integration: Integration) -> List[ValidationError]:
        """Validate integration-specific fields"""
        errors = []

        if not integration.service_name:
            errors.append(
                ValidationError("service_name", "Service name is required")
            )

        if not integration.authentication_type:
            errors.append(
                ValidationError(
                    "authentication_type",
                    "Authentication type is required"
                )
            )

        # Validate auth type
        valid_auth_types = ["oauth", "api_key", "basic", "none"]
        if integration.authentication_type not in valid_auth_types:
            errors.append(
                ValidationError(
                    "authentication_type",
                    f"Authentication type must be one of: {', '.join(valid_auth_types)}"
                )
            )

        return errors

    def get_validation_report(
        self,
        item: MarketplaceItem
    ) -> Dict[str, Any]:
        """
        Get comprehensive validation report

        Args:
            item: Item to validate

        Returns:
            Validation report
        """
        is_valid, errors = self.validate_item(item)

        # Group by severity
        error_count = len([e for e in errors if e.severity == "error"])
        warning_count = len([e for e in errors if e.severity == "warning"])
        info_count = len([e for e in errors if e.severity == "info"])

        return {
            "is_valid": is_valid,
            "item_id": item.item_id,
            "item_name": item.name,
            "total_issues": len(errors),
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "can_publish": is_valid and error_count == 0,
            "issues": [e.to_dict() for e in errors],
            "message": (
                "Ready to publish" if is_valid
                else f"Cannot publish: {error_count} error(s) found"
            )
        }
