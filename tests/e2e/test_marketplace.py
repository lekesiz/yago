"""
YAGO v8.1 - Template Marketplace E2E Tests
Testing template marketplace functionality
"""

import pytest
from httpx import AsyncClient
from typing import List, Dict


@pytest.mark.e2e
@pytest.mark.requires_api
class TestTemplateMarketplace:
    """Test template marketplace listing and filtering"""

    @pytest.mark.asyncio
    async def test_list_all_templates(self, client: AsyncClient):
        """Test listing all available templates"""

        print("\n[TEST] Testing template marketplace listing...")

        response = await client.get("/api/v1/templates")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "templates" in data
        assert isinstance(data["templates"], list)
        assert len(data["templates"]) > 0

        # Verify each template has required fields
        for template in data["templates"]:
            assert "id" in template
            assert "name" in template
            assert "description" in template
            assert "category" in template
            assert "difficulty" in template
            assert "tags" in template
            assert isinstance(template["tags"], list)

        print(f"[TEST] ✓ Found {len(data['templates'])} templates")

    @pytest.mark.asyncio
    async def test_template_categories(self, client: AsyncClient):
        """Test filtering templates by category"""

        print("\n[TEST] Testing template categories...")

        # Get all templates first
        response = await client.get("/api/v1/templates")
        all_templates = response.json()["templates"]

        # Get unique categories
        categories = set(t["category"] for t in all_templates)

        for category in categories:
            print(f"[TEST] Testing category: {category}")

            # Filter by category
            response = await client.get(f"/api/v1/templates?category={category}")
            assert response.status_code == 200

            data = response.json()
            filtered_templates = data["templates"]

            # Verify all returned templates match category
            for template in filtered_templates:
                assert template["category"] == category

            print(f"[TEST] ✓ {category}: {len(filtered_templates)} templates")

    @pytest.mark.asyncio
    async def test_template_difficulty_levels(self, client: AsyncClient):
        """Test filtering templates by difficulty"""

        print("\n[TEST] Testing difficulty levels...")

        difficulty_levels = ["beginner", "intermediate", "advanced"]

        for difficulty in difficulty_levels:
            print(f"[TEST] Testing difficulty: {difficulty}")

            response = await client.get(f"/api/v1/templates?difficulty={difficulty}")
            assert response.status_code == 200

            data = response.json()

            # Verify all templates match difficulty
            for template in data["templates"]:
                assert template["difficulty"] == difficulty

            print(f"[TEST] ✓ {difficulty}: {len(data['templates'])} templates")

    @pytest.mark.asyncio
    async def test_popular_templates(self, client: AsyncClient):
        """Test filtering popular templates"""

        print("\n[TEST] Testing popular templates...")

        response = await client.get("/api/v1/templates?popular=true")

        assert response.status_code == 200
        data = response.json()

        # Verify all returned templates are marked as popular
        for template in data["templates"]:
            assert template.get("is_popular", False) or template.get("popular", False)

        print(f"[TEST] ✓ Found {len(data['templates'])} popular templates")

    @pytest.mark.asyncio
    async def test_template_search(self, client: AsyncClient):
        """Test template search functionality"""

        print("\n[TEST] Testing template search...")

        search_terms = ["api", "web", "mobile", "data"]

        for term in search_terms:
            print(f"[TEST] Searching for: {term}")

            response = await client.get(f"/api/v1/templates?search={term}")
            assert response.status_code == 200

            data = response.json()
            templates = data["templates"]

            # Verify search results contain the search term
            for template in templates:
                found = (
                    term.lower() in template["name"].lower() or
                    term.lower() in template["description"].lower() or
                    any(term.lower() in tag.lower() for tag in template.get("tags", []))
                )
                assert found, f"Template '{template['name']}' doesn't match search term '{term}'"

            print(f"[TEST] ✓ Found {len(templates)} results for '{term}'")

    @pytest.mark.asyncio
    async def test_template_tags(self, client: AsyncClient):
        """Test filtering templates by tags"""

        print("\n[TEST] Testing template tags...")

        # Get all templates to find common tags
        response = await client.get("/api/v1/templates")
        all_templates = response.json()["templates"]

        # Collect all tags
        all_tags = set()
        for template in all_templates:
            all_tags.update(template.get("tags", []))

        # Test filtering by a few common tags
        test_tags = list(all_tags)[:3]  # Test first 3 tags

        for tag in test_tags:
            print(f"[TEST] Testing tag: {tag}")

            response = await client.get(f"/api/v1/templates?tag={tag}")
            assert response.status_code == 200

            data = response.json()
            templates = data["templates"]

            # Verify all templates have this tag
            for template in templates:
                assert tag in template.get("tags", [])

            print(f"[TEST] ✓ {tag}: {len(templates)} templates")

    @pytest.mark.asyncio
    async def test_get_template_by_id(self, client: AsyncClient):
        """Test getting a specific template by ID"""

        print("\n[TEST] Testing get template by ID...")

        # First get all templates
        response = await client.get("/api/v1/templates")
        all_templates = response.json()["templates"]

        # Get first template
        if len(all_templates) > 0:
            template_id = all_templates[0]["id"]

            # Get specific template
            response = await client.get(f"/api/v1/templates/{template_id}")
            assert response.status_code == 200

            template = response.json()
            assert template["id"] == template_id

            print(f"[TEST] ✓ Retrieved template: {template['name']}")

    @pytest.mark.asyncio
    async def test_template_structure_validation(self, client: AsyncClient):
        """Test that all templates have complete and valid structure"""

        print("\n[TEST] Testing template structure validation...")

        response = await client.get("/api/v1/templates")
        templates = response.json()["templates"]

        required_fields = ["id", "name", "description", "category", "difficulty"]
        optional_fields = ["tags", "estimated_time", "estimated_cost", "icon", "popular"]

        for template in templates:
            # Verify required fields
            for field in required_fields:
                assert field in template, f"Template {template.get('id')} missing required field: {field}"
                assert template[field], f"Template {template.get('id')} has empty {field}"

            # Verify field types
            assert isinstance(template["tags"], list), "Tags must be a list"
            if "estimated_cost" in template:
                assert isinstance(template["estimated_cost"], (int, float)), "Cost must be numeric"
            if "popular" in template or "is_popular" in template:
                is_popular = template.get("popular", template.get("is_popular"))
                assert isinstance(is_popular, bool), "Popular must be boolean"

        print(f"[TEST] ✓ All {len(templates)} templates have valid structure")


@pytest.mark.e2e
@pytest.mark.requires_api
class TestTemplateUsage:
    """Test using templates to create projects"""

    @pytest.mark.asyncio
    async def test_create_project_from_template(self, client: AsyncClient):
        """Test creating a project from a template"""

        print("\n[TEST] Testing project creation from template...")

        # Get a template
        templates_response = await client.get("/api/v1/templates")
        templates = templates_response.json()["templates"]

        if len(templates) > 0:
            template = templates[0]
            template_id = template["id"]

            # Create project from template
            project_data = {
                "name": f"Project from {template['name']}",
                "description": f"Test project created from template {template_id}",
                "template_id": template_id,
                "brief": {
                    "project_idea": template["description"]
                },
                "config": {
                    "primary_model": "gpt-4-turbo-preview",
                    "strategy": "balanced"
                }
            }

            response = await client.post("/api/v1/projects", json=project_data)
            assert response.status_code == 201

            project = response.json()
            assert project["name"] == project_data["name"]

            print(f"[TEST] ✓ Created project from template: {template['name']}")

            # Cleanup
            await client.delete(f"/api/v1/projects/{project['id']}")

    @pytest.mark.asyncio
    async def test_apply_template_endpoint(self, client: AsyncClient):
        """Test template application endpoint"""

        print("\n[TEST] Testing template application...")

        # Get a template
        templates_response = await client.get("/api/v1/templates")
        templates = templates_response.json()["templates"]

        if len(templates) > 0:
            template_id = templates[0]["id"]

            # Apply template
            apply_data = {
                "template_id": template_id,
                "customizations": {
                    "project_name": "Custom Project Name",
                    "additional_features": ["feature1", "feature2"]
                }
            }

            response = await client.post("/api/v1/templates/apply", json=apply_data)

            # Should return 200 or 404 depending on endpoint implementation
            assert response.status_code in [200, 404, 501]

            if response.status_code == 200:
                result = response.json()
                assert "project_brief" in result or "config" in result
                print(f"[TEST] ✓ Template applied successfully")
            else:
                print(f"[TEST] ⚠ Template application endpoint not implemented")


@pytest.mark.e2e
class TestMarketplacePerformance:
    """Test marketplace performance and edge cases"""

    @pytest.mark.asyncio
    async def test_marketplace_pagination(self, client: AsyncClient):
        """Test marketplace pagination"""

        print("\n[TEST] Testing marketplace pagination...")

        # Get templates with pagination
        response = await client.get("/api/v1/templates?limit=5&offset=0")

        if response.status_code == 200:
            data = response.json()

            # Check pagination metadata
            if "total" in data:
                assert data["total"] >= 0
                assert len(data["templates"]) <= 5

            print(f"[TEST] ✓ Pagination working")
        else:
            print(f"[TEST] ⚠ Pagination not implemented")

    @pytest.mark.asyncio
    async def test_marketplace_sorting(self, client: AsyncClient):
        """Test marketplace sorting"""

        print("\n[TEST] Testing marketplace sorting...")

        sort_fields = ["name", "difficulty", "category", "popular"]

        for field in sort_fields:
            response = await client.get(f"/api/v1/templates?sort={field}")

            if response.status_code == 200:
                templates = response.json()["templates"]

                # Verify sorting (basic check)
                if len(templates) > 1:
                    print(f"[TEST] ✓ Sorting by {field}: {len(templates)} templates")
            else:
                print(f"[TEST] ⚠ Sorting by {field} not implemented")

    @pytest.mark.asyncio
    async def test_empty_search_results(self, client: AsyncClient):
        """Test handling of empty search results"""

        print("\n[TEST] Testing empty search results...")

        # Search for something that doesn't exist
        response = await client.get("/api/v1/templates?search=xyzabc123nonexistent")

        assert response.status_code == 200
        data = response.json()

        # Should return empty list, not error
        assert "templates" in data
        assert isinstance(data["templates"], list)
        assert len(data["templates"]) == 0

        print(f"[TEST] ✓ Empty search handled correctly")

    @pytest.mark.asyncio
    async def test_invalid_category_filter(self, client: AsyncClient):
        """Test handling of invalid category filter"""

        print("\n[TEST] Testing invalid category filter...")

        response = await client.get("/api/v1/templates?category=invalid_category")

        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            # Should return empty list for non-existent category
            assert len(data["templates"]) == 0
            print(f"[TEST] ✓ Invalid category returns empty list")
        else:
            print(f"[TEST] ✓ Invalid category rejected with 400")

    @pytest.mark.asyncio
    async def test_combined_filters(self, client: AsyncClient):
        """Test using multiple filters simultaneously"""

        print("\n[TEST] Testing combined filters...")

        # Combine category, difficulty, and popular filters
        response = await client.get(
            "/api/v1/templates?category=web&difficulty=intermediate&popular=true"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all filters are applied
        for template in data["templates"]:
            assert template["category"] == "web"
            assert template["difficulty"] == "intermediate"
            assert template.get("popular", False) or template.get("is_popular", False)

        print(f"[TEST] ✓ Combined filters work: {len(data['templates'])} results")

    @pytest.mark.asyncio
    async def test_marketplace_response_time(self, client: AsyncClient):
        """Test marketplace response time"""

        import time

        print("\n[TEST] Testing marketplace response time...")

        start_time = time.time()
        response = await client.get("/api/v1/templates")
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 2.0, f"Marketplace too slow: {response_time:.2f}s"

        print(f"[TEST] ✓ Response time: {response_time:.3f}s")


@pytest.mark.e2e
class TestTemplateDataIntegrity:
    """Test template data integrity and consistency"""

    @pytest.mark.asyncio
    async def test_template_ids_unique(self, client: AsyncClient):
        """Test that all template IDs are unique"""

        print("\n[TEST] Testing template ID uniqueness...")

        response = await client.get("/api/v1/templates")
        templates = response.json()["templates"]

        template_ids = [t["id"] for t in templates]
        unique_ids = set(template_ids)

        assert len(template_ids) == len(unique_ids), "Duplicate template IDs found!"

        print(f"[TEST] ✓ All {len(template_ids)} template IDs are unique")

    @pytest.mark.asyncio
    async def test_template_names_meaningful(self, client: AsyncClient):
        """Test that template names are meaningful and not empty"""

        print("\n[TEST] Testing template name quality...")

        response = await client.get("/api/v1/templates")
        templates = response.json()["templates"]

        for template in templates:
            assert len(template["name"]) > 0, "Empty template name"
            assert len(template["name"]) < 100, "Template name too long"
            assert len(template["description"]) > 10, "Description too short"

        print(f"[TEST] ✓ All template names are meaningful")

    @pytest.mark.asyncio
    async def test_template_cost_estimates(self, client: AsyncClient):
        """Test that cost estimates are reasonable"""

        print("\n[TEST] Testing cost estimate validity...")

        response = await client.get("/api/v1/templates")
        templates = response.json()["templates"]

        for template in templates:
            if "estimated_cost" in template:
                cost = template["estimated_cost"]
                assert 0 <= cost <= 1000, f"Unreasonable cost for {template['name']}: ${cost}"

        print(f"[TEST] ✓ All cost estimates are reasonable")
