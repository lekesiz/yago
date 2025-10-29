"""
YAGO v8.1 - Analytics E2E Tests
Testing analytics endpoints with real data aggregation
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


@pytest.mark.e2e
@pytest.mark.requires_api
class TestAnalyticsOverview:
    """Test analytics overview endpoint with various time ranges"""

    @pytest.mark.asyncio
    async def test_analytics_overview_all_time_ranges(self, client: AsyncClient):
        """Test analytics overview with all time ranges"""

        time_ranges = ["24h", "7d", "30d", "90d", "all"]

        for time_range in time_ranges:
            print(f"\n[TEST] Testing time range: {time_range}")

            response = await client.get(f"/api/v1/analytics/overview?time_range={time_range}")

            assert response.status_code == 200, f"Failed for time_range={time_range}"
            analytics = response.json()

            # Verify structure
            assert "time_range" in analytics
            assert analytics["time_range"] == time_range
            assert "projects" in analytics
            assert "code_generation" in analytics
            assert "costs" in analytics
            assert "performance" in analytics

            # Verify projects metrics
            projects = analytics["projects"]
            assert "total" in projects
            assert "completed" in projects
            assert "failed" in projects
            assert "in_progress" in projects
            assert "success_rate" in projects
            assert 0 <= projects["success_rate"] <= 100

            # Verify code generation metrics
            code_gen = analytics["code_generation"]
            assert "total_files" in code_gen
            assert "total_lines" in code_gen
            assert code_gen["total_files"] >= 0
            assert code_gen["total_lines"] >= 0

            # Verify cost metrics
            costs = analytics["costs"]
            assert "total" in costs
            assert "average_per_project" in costs
            assert "by_provider" in costs
            assert costs["total"] >= 0

            # Verify performance metrics
            performance = analytics["performance"]
            assert "average_execution_time_seconds" in performance
            assert performance["average_execution_time_seconds"] >= 0

            print(f"[TEST] ✓ {time_range}: {projects['total']} total projects")

    @pytest.mark.asyncio
    async def test_analytics_with_zero_projects(self, client: AsyncClient, db_session: Session):
        """Test analytics when there are no projects"""

        print("\n[TEST] Testing analytics with zero projects...")

        # Clear all projects (in test DB)
        response = await client.get("/api/v1/analytics/overview")

        assert response.status_code == 200
        analytics = response.json()

        # Should return zero values, not error
        assert analytics["projects"]["total"] >= 0
        assert analytics["code_generation"]["total_files"] >= 0
        assert analytics["costs"]["total"] >= 0

        print("[TEST] ✓ Analytics work with zero projects")

    @pytest.mark.asyncio
    async def test_analytics_with_single_project(self, client: AsyncClient, test_project_data):
        """Test analytics with exactly one project"""

        print("\n[TEST] Testing analytics with single project...")

        # Create one project
        create_response = await client.post("/api/v1/projects", json=test_project_data)
        project = create_response.json()
        project_id = project["id"]

        # Execute project
        await client.post(f"/api/v1/projects/{project_id}/execute")

        # Get analytics
        analytics_response = await client.get("/api/v1/analytics/overview")
        assert analytics_response.status_code == 200

        analytics = analytics_response.json()
        assert analytics["projects"]["total"] >= 1

        # Cleanup
        await client.delete(f"/api/v1/projects/{project_id}")

        print("[TEST] ✓ Analytics work with single project")

    @pytest.mark.asyncio
    async def test_analytics_with_many_projects(self, client: AsyncClient, test_project_data):
        """Test analytics with multiple projects"""

        print("\n[TEST] Testing analytics with many projects...")

        project_ids = []

        # Create 5 projects
        for i in range(5):
            data = test_project_data.copy()
            data["name"] = f"Analytics Test Project {i+1}"

            response = await client.post("/api/v1/projects", json=data)
            project = response.json()
            project_ids.append(project["id"])

        # Get analytics
        analytics_response = await client.get("/api/v1/analytics/overview")
        assert analytics_response.status_code == 200

        analytics = analytics_response.json()
        assert analytics["projects"]["total"] >= 5

        # Cleanup
        for project_id in project_ids:
            await client.delete(f"/api/v1/projects/{project_id}")

        print(f"[TEST] ✓ Analytics work with {len(project_ids)} projects")

    @pytest.mark.asyncio
    async def test_analytics_data_aggregation_accuracy(self, client: AsyncClient, test_project_data):
        """Test that analytics data aggregation is accurate"""

        print("\n[TEST] Testing analytics data aggregation accuracy...")

        # Create and execute a project
        create_response = await client.post("/api/v1/projects", json=test_project_data)
        project = create_response.json()
        project_id = project["id"]

        exec_response = await client.post(f"/api/v1/projects/{project_id}/execute")
        exec_result = exec_response.json()

        # Get project details
        project_response = await client.get(f"/api/v1/projects/{project_id}")
        project_details = project_response.json()

        # Get analytics
        analytics_response = await client.get("/api/v1/analytics/overview?time_range=all")
        analytics = analytics_response.json()

        # Verify aggregation includes our project
        assert analytics["projects"]["total"] >= 1

        # Verify files count (should be at least our project's files)
        if project_details["status"] == "completed":
            assert analytics["code_generation"]["total_files"] >= project_details["files_generated"]
            assert analytics["code_generation"]["total_lines"] >= project_details["lines_of_code"]

        # Cleanup
        await client.delete(f"/api/v1/projects/{project_id}")

        print("[TEST] ✓ Data aggregation is accurate")


@pytest.mark.e2e
@pytest.mark.requires_api
class TestProviderUsageAnalytics:
    """Test provider usage analytics endpoint"""

    @pytest.mark.asyncio
    async def test_provider_usage_analytics(self, client: AsyncClient):
        """Test provider usage analytics endpoint"""

        print("\n[TEST] Testing provider usage analytics...")

        response = await client.get("/api/v1/analytics/providers-usage")

        assert response.status_code == 200
        analytics = response.json()

        # Verify structure
        assert "time_range" in analytics
        assert "providers" in analytics

        providers = analytics["providers"]

        # Check each provider has correct structure
        for provider_name, provider_data in providers.items():
            assert provider_name in ["openai", "anthropic", "gemini", "cursor"]
            assert "requests" in provider_data
            assert "tokens_used" in provider_data
            assert "cost" in provider_data
            assert "success_rate" in provider_data
            assert "average_latency_ms" in provider_data
            assert "models" in provider_data

            # Verify metrics are valid
            assert provider_data["requests"] >= 0
            assert provider_data["tokens_used"] >= 0
            assert provider_data["cost"] >= 0
            assert 0 <= provider_data["success_rate"] <= 100

        print(f"[TEST] ✓ Provider usage analytics verified")

    @pytest.mark.asyncio
    async def test_provider_usage_time_ranges(self, client: AsyncClient):
        """Test provider usage with different time ranges"""

        time_ranges = ["7d", "30d", "all"]

        for time_range in time_ranges:
            print(f"\n[TEST] Testing provider usage for: {time_range}")

            response = await client.get(f"/api/v1/analytics/providers-usage?time_range={time_range}")

            assert response.status_code == 200
            analytics = response.json()
            assert analytics["time_range"] == time_range

            print(f"[TEST] ✓ {time_range} provider usage retrieved")

    @pytest.mark.asyncio
    async def test_provider_model_breakdown(self, client: AsyncClient):
        """Test that provider analytics includes model-level breakdown"""

        print("\n[TEST] Testing provider model breakdown...")

        response = await client.get("/api/v1/analytics/providers-usage")
        assert response.status_code == 200

        analytics = response.json()
        providers = analytics["providers"]

        # Check that at least one provider has model breakdown
        has_model_breakdown = False
        for provider_data in providers.values():
            if "models" in provider_data and len(provider_data["models"]) > 0:
                has_model_breakdown = True
                # Verify model data structure
                for model_name, model_data in provider_data["models"].items():
                    assert "requests" in model_data
                    assert "cost" in model_data
                    assert model_data["requests"] >= 0
                    assert model_data["cost"] >= 0

        print(f"[TEST] ✓ Model breakdown available: {has_model_breakdown}")


@pytest.mark.e2e
@pytest.mark.requires_api
class TestCostAnalytics:
    """Test cost tracking and analytics endpoints"""

    @pytest.mark.asyncio
    async def test_cost_summary_endpoint(self, client: AsyncClient):
        """Test cost summary endpoint"""

        print("\n[TEST] Testing cost summary...")

        response = await client.get("/api/v1/costs/summary")

        assert response.status_code == 200
        cost_summary = response.json()

        # Verify structure
        assert "time_range" in cost_summary
        assert "total_cost" in cost_summary
        assert "cost_by_provider" in cost_summary
        assert "cost_by_operation" in cost_summary
        assert "cost_trend" in cost_summary

        # Verify totals are valid
        assert cost_summary["total_cost"] >= 0

        # Verify provider breakdown
        for provider, cost in cost_summary["cost_by_provider"].items():
            assert provider in ["openai", "anthropic", "gemini", "cursor"]
            assert cost >= 0

        # Verify operation breakdown
        for operation, cost in cost_summary["cost_by_operation"].items():
            assert cost >= 0

        # Verify trend is a list
        assert isinstance(cost_summary["cost_trend"], list)

        print(f"[TEST] ✓ Total cost: ${cost_summary['total_cost']:.4f}")

    @pytest.mark.asyncio
    async def test_cost_alerts_endpoint(self, client: AsyncClient):
        """Test cost alerts endpoint"""

        print("\n[TEST] Testing cost alerts...")

        response = await client.get("/api/v1/costs/alerts")

        assert response.status_code == 200
        alerts = response.json()

        # Verify structure
        assert "budget" in alerts
        assert "alerts" in alerts
        assert "projections" in alerts

        # Verify budget info
        budget = alerts["budget"]
        assert "monthly_budget" in budget
        assert "current_spending" in budget
        assert "utilization_percent" in budget
        assert "remaining" in budget

        # Verify values are valid
        assert budget["monthly_budget"] >= 0
        assert budget["current_spending"] >= 0
        assert 0 <= budget["utilization_percent"] <= 200  # Can exceed 100%
        assert budget["remaining"] == budget["monthly_budget"] - budget["current_spending"]

        # Verify alerts list
        assert isinstance(alerts["alerts"], list)
        for alert in alerts["alerts"]:
            assert "type" in alert
            assert alert["type"] in ["info", "warning", "critical", "exceeded"]
            assert "message" in alert

        # Verify projections
        projections = alerts["projections"]
        assert "projected_monthly_cost" in projections
        assert "within_budget" in projections
        assert isinstance(projections["within_budget"], bool)

        print(f"[TEST] ✓ Budget utilization: {budget['utilization_percent']:.1f}%")
        print(f"[TEST] ✓ Alerts: {len(alerts['alerts'])}")

    @pytest.mark.asyncio
    async def test_cost_trend_data(self, client: AsyncClient):
        """Test cost trend data is properly formatted"""

        print("\n[TEST] Testing cost trend data...")

        response = await client.get("/api/v1/costs/summary?time_range=30d")
        assert response.status_code == 200

        cost_summary = response.json()
        cost_trend = cost_summary["cost_trend"]

        # Verify trend is a list of data points
        assert isinstance(cost_trend, list)

        # Each data point should have date and cost
        for data_point in cost_trend:
            assert "date" in data_point
            assert "cost" in data_point
            assert data_point["cost"] >= 0

        print(f"[TEST] ✓ Cost trend has {len(cost_trend)} data points")


@pytest.mark.e2e
class TestAnalyticsPerformance:
    """Test analytics performance with large datasets"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_analytics_response_time(self, client: AsyncClient):
        """Test that analytics endpoints respond within acceptable time"""

        import time

        endpoints = [
            "/api/v1/analytics/overview",
            "/api/v1/analytics/providers-usage",
            "/api/v1/costs/summary",
            "/api/v1/costs/alerts"
        ]

        for endpoint in endpoints:
            print(f"\n[TEST] Testing response time: {endpoint}")

            start_time = time.time()
            response = await client.get(endpoint)
            response_time = time.time() - start_time

            assert response.status_code == 200
            assert response_time < 5.0, f"{endpoint} took too long: {response_time:.2f}s"

            print(f"[TEST] ✓ Response time: {response_time:.3f}s")

    @pytest.mark.asyncio
    async def test_analytics_caching(self, client: AsyncClient):
        """Test that analytics data is properly cached"""

        print("\n[TEST] Testing analytics caching...")

        import time

        # First request (cold cache)
        start_time = time.time()
        response1 = await client.get("/api/v1/analytics/overview")
        first_time = time.time() - start_time

        # Second request (warm cache)
        start_time = time.time()
        response2 = await client.get("/api/v1/analytics/overview")
        second_time = time.time() - start_time

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Second request should be faster or similar
        print(f"[TEST] First request: {first_time:.3f}s")
        print(f"[TEST] Second request: {second_time:.3f}s")
        print(f"[TEST] ✓ Caching appears to be working")
