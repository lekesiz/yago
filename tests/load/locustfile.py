"""
YAGO v8.1 Load Testing Suite with Locust
========================================

Comprehensive load testing scenarios for YAGO backend API.

Test Scenarios:
1. Normal Load - 10 users for 5 minutes
2. Spike Load - 10 to 100 users in 1 minute
3. Stress Test - 200+ users to find breaking point
4. Endurance Test - 50 users for 30 minutes

Performance Targets:
- 95% of requests < 200ms
- 99% of requests < 500ms
- 0% error rate under normal load
- < 5% error rate under stress

Usage:
    # Run with Web UI
    locust -f locustfile.py --host=http://localhost:8000

    # Run headless (normal load)
    locust -f locustfile.py --host=http://localhost:8000 --users 10 --spawn-rate 2 --run-time 5m --headless

    # Run specific scenario
    locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 3m --headless NormalLoadUser
"""

from locust import HttpUser, task, between, events, tag
from locust.runners import MasterRunner, WorkerRunner
import random
import string
import json
import time
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Test Data Generators
# ============================================================================

class TestDataGenerator:
    """Generate realistic test data"""

    PROJECT_IDEAS = [
        "Build a REST API for task management with user authentication",
        "Create a real-time chat application with WebSocket support",
        "Develop a blog platform with markdown support and comments",
        "Build an e-commerce product catalog with search and filters",
        "Create a portfolio website with dynamic project showcase",
        "Develop a weather dashboard with API integration",
        "Build a todo list app with drag-and-drop functionality",
        "Create a recipe sharing platform with ratings",
        "Develop a URL shortener service with analytics",
        "Build a simple CRM system for managing contacts"
    ]

    TEMPLATES = [
        "minimal_api", "full_stack_app", "dashboard",
        "blog", "ecommerce", "portfolio"
    ]

    MODES = ["minimal", "full"]

    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def random_project_idea() -> str:
        """Get random project idea"""
        return random.choice(TestDataGenerator.PROJECT_IDEAS)

    @staticmethod
    def random_template() -> str:
        """Get random template"""
        return random.choice(TestDataGenerator.TEMPLATES)

    @staticmethod
    def random_mode() -> str:
        """Get random mode"""
        return random.choice(TestDataGenerator.MODES)

    @staticmethod
    def create_project_payload() -> Dict[str, Any]:
        """Create realistic project creation payload"""
        return {
            "idea": TestDataGenerator.random_project_idea(),
            "mode": TestDataGenerator.random_mode(),
            "template": TestDataGenerator.random_template() if random.random() > 0.5 else None,
            "interactive": random.choice([True, False]),
            "auto_debug": True
        }


# ============================================================================
# Custom Metrics Tracking
# ============================================================================

class MetricsTracker:
    """Track custom performance metrics"""

    def __init__(self):
        self.response_times = []
        self.error_count = 0
        self.request_count = 0
        self.project_creation_times = []
        self.start_time = None

    def record_request(self, response_time: float, success: bool):
        """Record request metrics"""
        self.request_count += 1
        if success:
            self.response_times.append(response_time)
        else:
            self.error_count += 1

    def record_project_creation(self, duration: float):
        """Record project creation time"""
        self.project_creation_times.append(duration)

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        if not self.response_times:
            return {
                "avg_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
                "error_rate": 100 if self.request_count > 0 else 0,
                "total_requests": self.request_count
            }

        sorted_times = sorted(self.response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)

        return {
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "p95_response_time": sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1],
            "p99_response_time": sorted_times[p99_index] if p99_index < len(sorted_times) else sorted_times[-1],
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "total_requests": self.request_count,
            "successful_requests": len(self.response_times)
        }


# Global metrics tracker
metrics_tracker = MetricsTracker()


# ============================================================================
# Event Handlers
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts"""
    logger.info("=" * 80)
    logger.info("YAGO v8.1 Load Test Starting")
    logger.info(f"Target: {environment.host}")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    metrics_tracker.start_time = time.time()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    stats = metrics_tracker.get_stats()
    duration = time.time() - metrics_tracker.start_time if metrics_tracker.start_time else 0

    logger.info("=" * 80)
    logger.info("YAGO v8.1 Load Test Results")
    logger.info("=" * 80)
    logger.info(f"Total Duration: {duration:.2f}s")
    logger.info(f"Total Requests: {stats['total_requests']}")
    logger.info(f"Successful Requests: {stats['successful_requests']}")
    logger.info(f"Failed Requests: {metrics_tracker.error_count}")
    logger.info(f"Error Rate: {stats['error_rate']:.2f}%")
    logger.info(f"Average Response Time: {stats['avg_response_time']:.2f}ms")
    logger.info(f"P95 Response Time: {stats['p95_response_time']:.2f}ms")
    logger.info(f"P99 Response Time: {stats['p99_response_time']:.2f}ms")
    logger.info(f"RPS: {stats['total_requests'] / duration:.2f}" if duration > 0 else "N/A")
    logger.info("=" * 80)

    # Check against performance targets
    passed_checks = []
    failed_checks = []

    if stats['p95_response_time'] < 200:
        passed_checks.append("P95 < 200ms")
    else:
        failed_checks.append(f"P95 ({stats['p95_response_time']:.2f}ms) >= 200ms")

    if stats['p99_response_time'] < 500:
        passed_checks.append("P99 < 500ms")
    else:
        failed_checks.append(f"P99 ({stats['p99_response_time']:.2f}ms) >= 500ms")

    if stats['error_rate'] < 5:
        passed_checks.append("Error rate < 5%")
    else:
        failed_checks.append(f"Error rate ({stats['error_rate']:.2f}%) >= 5%")

    if passed_checks:
        logger.info("PASSED CHECKS:")
        for check in passed_checks:
            logger.info(f"  ✓ {check}")

    if failed_checks:
        logger.warning("FAILED CHECKS:")
        for check in failed_checks:
            logger.warning(f"  ✗ {check}")

    logger.info("=" * 80)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track each request"""
    success = exception is None
    metrics_tracker.record_request(response_time, success)


# ============================================================================
# Base User Class
# ============================================================================

class YAGOUser(HttpUser):
    """Base class for YAGO load testing users"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when user starts"""
        self.project_ids = []
        self.generator = TestDataGenerator()
        logger.info(f"User {self.environment.runner.user_count} started")

    def on_stop(self):
        """Called when user stops"""
        logger.info(f"User stopped. Created {len(self.project_ids)} projects")

    @tag('health')
    @task(1)
    def health_check(self):
        """Health check endpoint (lowest weight)"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @tag('status')
    @task(4)
    def get_status(self):
        """Get system status"""
        with self.client.get("/api/status", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "running":
                    response.success()
                else:
                    response.failure("Invalid status response")
            else:
                response.failure(f"Status check failed: {response.status_code}")

    @tag('templates')
    @task(3)
    def list_templates(self):
        """List available templates"""
        with self.client.get("/api/templates", catch_response=True) as response:
            if response.status_code == 200:
                templates = response.json()
                if isinstance(templates, list):
                    response.success()
                else:
                    response.failure("Invalid templates response")
            else:
                response.failure(f"Templates list failed: {response.status_code}")

    @tag('projects', 'list')
    @task(5)
    def list_projects(self):
        """List all projects (highest weight for read operations)"""
        with self.client.get("/api/projects", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "projects" in data and "total" in data:
                    response.success()
                else:
                    response.failure("Invalid projects list response")
            else:
                response.failure(f"Projects list failed: {response.status_code}")

    @tag('projects', 'create')
    @task(2)
    def create_project(self):
        """Create a new project"""
        start_time = time.time()
        payload = self.generator.create_project_payload()

        with self.client.post(
            "/api/projects",
            json=payload,
            catch_response=True,
            name="/api/projects [POST]"
        ) as response:
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if "project_id" in data:
                    self.project_ids.append(data["project_id"])
                    metrics_tracker.record_project_creation(duration * 1000)  # Convert to ms
                    response.success()
                else:
                    response.failure("No project_id in response")
            else:
                response.failure(f"Project creation failed: {response.status_code}")

    @tag('projects', 'detail')
    @task(3)
    def get_project_detail(self):
        """Get project details"""
        if not self.project_ids:
            # Create a project first if none exist
            return

        project_id = random.choice(self.project_ids)
        with self.client.get(
            f"/api/projects/{project_id}",
            catch_response=True,
            name="/api/projects/{id} [GET]"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == project_id:
                    response.success()
                else:
                    response.failure("Invalid project detail response")
            elif response.status_code == 404:
                # Project might have been deleted
                response.success()
            else:
                response.failure(f"Project detail failed: {response.status_code}")


# ============================================================================
# Scenario 1: Normal Load User
# ============================================================================

class NormalLoadUser(YAGOUser):
    """
    Normal Load Scenario
    - 10 concurrent users
    - Typical usage patterns
    - Run for 5 minutes
    """
    wait_time = between(2, 5)  # Slower pace for normal usage


# ============================================================================
# Scenario 2: Spike Load User
# ============================================================================

class SpikeLoadUser(YAGOUser):
    """
    Spike Load Scenario
    - Ramp from 10 to 100 users in 1 minute
    - Hold 100 users for 2 minutes
    - Test rapid scaling
    """
    wait_time = between(1, 2)  # Faster pace during spike


# ============================================================================
# Scenario 3: Stress Test User
# ============================================================================

class StressTestUser(YAGOUser):
    """
    Stress Test Scenario
    - 200+ concurrent users
    - Find breaking point
    - Minimal wait time
    """
    wait_time = between(0.5, 1.5)  # Aggressive load

    @task(10)  # Higher weight for write operations
    def aggressive_create(self):
        """More aggressive project creation"""
        self.create_project()


# ============================================================================
# Scenario 4: Endurance Test User
# ============================================================================

class EnduranceTestUser(YAGOUser):
    """
    Endurance Test Scenario
    - 50 concurrent users
    - Run for 30 minutes
    - Check for memory leaks
    """
    wait_time = between(3, 6)  # Steady, sustained load


# ============================================================================
# Custom Shape Classes for Specific Load Patterns
# ============================================================================

from locust import LoadTestShape

class NormalLoadShape(LoadTestShape):
    """
    Normal Load Shape: 10 users for 5 minutes
    """
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},   # Ramp up to 10 in 1 min
        {"duration": 300, "users": 10, "spawn_rate": 0},  # Hold 10 for 5 min
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None


class SpikeLoadShape(LoadTestShape):
    """
    Spike Load Shape: 10 -> 100 users in 1 min, hold for 2 min
    """
    stages = [
        {"duration": 10, "users": 10, "spawn_rate": 2},    # Start with 10
        {"duration": 70, "users": 100, "spawn_rate": 10},  # Spike to 100 in 1 min
        {"duration": 190, "users": 100, "spawn_rate": 0},  # Hold for 2 min
        {"duration": 220, "users": 10, "spawn_rate": 10},  # Ramp down
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None


class StressTestShape(LoadTestShape):
    """
    Stress Test Shape: Gradually increase to 200+ users
    """
    stages = [
        {"duration": 60, "users": 50, "spawn_rate": 5},
        {"duration": 120, "users": 100, "spawn_rate": 5},
        {"duration": 180, "users": 150, "spawn_rate": 5},
        {"duration": 240, "users": 200, "spawn_rate": 5},
        {"duration": 300, "users": 250, "spawn_rate": 5},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None


class EnduranceTestShape(LoadTestShape):
    """
    Endurance Test Shape: 50 users for 30 minutes
    """
    stages = [
        {"duration": 120, "users": 50, "spawn_rate": 5},    # Ramp up to 50 in 2 min
        {"duration": 1800, "users": 50, "spawn_rate": 0},   # Hold for 30 min
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import os
    import sys

    print("=" * 80)
    print("YAGO v8.1 Load Testing Suite")
    print("=" * 80)
    print("\nAvailable User Classes:")
    print("  1. NormalLoadUser - Normal load scenario (10 users, 5 min)")
    print("  2. SpikeLoadUser - Spike load scenario (10->100 users)")
    print("  3. StressTestUser - Stress test (200+ users)")
    print("  4. EnduranceTestUser - Endurance test (50 users, 30 min)")
    print("\nAvailable Load Shapes:")
    print("  1. NormalLoadShape")
    print("  2. SpikeLoadShape")
    print("  3. StressTestShape")
    print("  4. EnduranceTestShape")
    print("\nUsage Examples:")
    print("  # Web UI (default)")
    print("  locust -f locustfile.py --host=http://localhost:8000")
    print("\n  # Headless with normal load shape")
    print("  locust -f locustfile.py --host=http://localhost:8000 \\")
    print("         --users 10 --spawn-rate 2 --run-time 5m --headless")
    print("\n  # Specific user class")
    print("  locust -f locustfile.py --host=http://localhost:8000 \\")
    print("         --users 100 --spawn-rate 10 StressTestUser --headless")
    print("=" * 80)
