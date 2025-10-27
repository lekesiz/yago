"""
Template Loader for YAGO
Loads and manages project templates
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger("YAGO")


class TemplateLoader:
    """Loads and manages project templates"""

    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_cache: Dict[str, Dict] = {}
        self._load_all_templates()

    def _load_all_templates(self):
        """Load all available templates into cache"""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return

        # Scan all YAML files in templates directory
        for yaml_file in self.templates_dir.rglob("*.yaml"):
            try:
                template_name = yaml_file.stem
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)

                self.templates_cache[template_name] = template_data
                logger.debug(f"Loaded template: {template_name}")
            except Exception as e:
                logger.error(f"Failed to load template {yaml_file}: {e}")

        logger.info(f"📦 Loaded {len(self.templates_cache)} templates")

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates with metadata"""
        templates = []
        for name, data in self.templates_cache.items():
            templates.append({
                "name": name,
                "display_name": data.get("name", name),
                "category": data.get("category", "unknown"),
                "description": data.get("description", ""),
                "difficulty": data.get("difficulty", "medium"),
                "time": data.get("estimated_time", "unknown"),
                "tags": data.get("tags", [])
            })
        return templates

    def get_template(self, template_name: str) -> Optional[Dict]:
        """Get a specific template by name"""
        return self.templates_cache.get(template_name)

    def get_template_idea(self, template_name: str) -> Optional[str]:
        """Get the project idea from a template"""
        template = self.get_template(template_name)
        if template:
            return template.get("project_idea", "")
        return None

    def get_config_overrides(self, template_name: str) -> Optional[Dict]:
        """Get configuration overrides from a template"""
        template = self.get_template(template_name)
        if template:
            return template.get("config_overrides", {})
        return {}

    def apply_template(self, template_name: str, custom_idea: Optional[str] = None) -> Dict:
        """
        Apply a template and return the combined configuration

        Args:
            template_name: Name of the template to use
            custom_idea: Optional custom project idea (overrides template's idea)

        Returns:
            Dictionary with project_idea and config_overrides
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Use custom idea if provided, otherwise use template's idea
        project_idea = custom_idea or template.get("project_idea", "")

        # Get config overrides
        config_overrides = template.get("config_overrides", {})

        return {
            "project_idea": project_idea,
            "config_overrides": config_overrides,
            "template_name": template_name,
            "template_metadata": {
                "name": template.get("name"),
                "category": template.get("category"),
                "difficulty": template.get("difficulty"),
                "estimated_time": template.get("estimated_time"),
                "tech_stack": template.get("tech_stack")
            }
        }

    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get all templates in a specific category"""
        return [
            {"name": name, **data}
            for name, data in self.templates_cache.items()
            if data.get("category") == category
        ]

    def search_templates(self, query: str) -> List[Dict]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for name, data in self.templates_cache.items():
            # Search in name
            if query_lower in name.lower():
                results.append({"name": name, **data})
                continue

            # Search in description
            desc = data.get("description", "").lower()
            if query_lower in desc:
                results.append({"name": name, **data})
                continue

            # Search in tags
            tags = data.get("tags", [])
            if any(query_lower in tag.lower() for tag in tags):
                results.append({"name": name, **data})

        return results

    def print_templates_list(self):
        """Print a formatted list of all templates"""
        templates = self.list_templates()

        if not templates:
            print("No templates available")
            return

        print("\n" + "=" * 80)
        print("📦 AVAILABLE YAGO TEMPLATES")
        print("=" * 80)

        # Group by category
        categories = {}
        for template in templates:
            cat = template["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(template)

        for category, temps in sorted(categories.items()):
            print(f"\n## {category.upper()}")
            print("-" * 80)

            for temp in temps:
                difficulty_emoji = {
                    "easy": "🟢",
                    "medium": "🟡",
                    "hard": "🔴"
                }.get(temp["difficulty"], "⚪")

                print(f"\n{difficulty_emoji} {temp['display_name']}")
                print(f"   ID: {temp['name']}")
                print(f"   {temp['description']}")
                print(f"   Time: {temp['time']} | Difficulty: {temp['difficulty']}")
                if temp['tags']:
                    print(f"   Tags: {', '.join(temp['tags'])}")

        print("\n" + "=" * 80)
        print(f"Total: {len(templates)} templates")
        print("\nUsage: python main.py --template <template_id>")
        print("=" * 80 + "\n")


# Singleton instance
_template_loader = None


def get_template_loader() -> TemplateLoader:
    """Get or create template loader singleton"""
    global _template_loader
    if _template_loader is None:
        _template_loader = TemplateLoader()
    return _template_loader
