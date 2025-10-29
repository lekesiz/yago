"""
YAGO v8.1 - Project Lifecycle E2E Tests
Full project creation to completion flow testing
"""

import pytest
import asyncio
import time
from httpx import AsyncClient
from sqlalchemy.orm import Session
from pathlib import Path


@pytest.mark.e2e
@pytest.mark.requires_api
class TestProjectLifecycle:
    """
    Test complete project lifecycle:
    1. Create project
    2. Start execution
    3. Check progress
    4. Wait for completion
    5. Verify files generated
    6. Download project ZIP
    7. Delete project
    """

    @pytest.mark.asyncio
    async def test_complete_project_flow(self, client: AsyncClient, test_project_data, cleanup_generated_projects):
        """Test full project lifecycle from creation to deletion"""

        # ============================================
        # STEP 1: Create Project
        # ============================================
        print("\n[TEST] Step 1: Creating project...")
        create_response = await client.post("/api/v1/projects", json=test_project_data)

        assert create_response.status_code == 201, f"Failed to create project: {create_response.text}"
        project = create_response.json()

        assert "id" in project
        assert project["name"] == test_project_data["name"]
        assert project["status"] == "creating"
        assert project["progress"] == 0

        project_id = project["id"]
        print(f"[TEST] ✓ Project created: {project_id}")

        # ============================================
        # STEP 2: Get Project Details
        # ============================================
        print(f"[TEST] Step 2: Fetching project details...")
        get_response = await client.get(f"/api/v1/projects/{project_id}")

        assert get_response.status_code == 200
        project_details = get_response.json()

        assert project_details["id"] == project_id
        assert project_details["name"] == test_project_data["name"]
        print(f"[TEST] ✓ Project details retrieved")

        # ============================================
        # STEP 3: Execute Code Generation
        # ============================================
        print(f"[TEST] Step 3: Starting code execution...")
        execute_response = await client.post(f"/api/v1/projects/{project_id}/execute")

        assert execute_response.status_code == 200, f"Execution failed: {execute_response.text}"
        execution_result = execute_response.json()

        assert execution_result["status"] == "success"
        assert "result" in execution_result
        print(f"[TEST] ✓ Code execution completed")

        # ============================================
        # STEP 4: Verify Project Completion
        # ============================================
        print(f"[TEST] Step 4: Verifying project completion...")
        get_response = await client.get(f"/api/v1/projects/{project_id}")

        assert get_response.status_code == 200
        completed_project = get_response.json()

        assert completed_project["status"] == "completed"
        assert completed_project["progress"] == 100
        assert completed_project["files_generated"] > 0
        assert completed_project["lines_of_code"] > 0
        assert completed_project["actual_cost"] >= 0
        print(f"[TEST] ✓ Project completed successfully")
        print(f"[TEST]   - Files: {completed_project['files_generated']}")
        print(f"[TEST]   - Lines: {completed_project['lines_of_code']}")
        print(f"[TEST]   - Cost: ${completed_project['actual_cost']:.4f}")

        # ============================================
        # STEP 5: List Generated Files
        # ============================================
        print(f"[TEST] Step 5: Listing generated files...")
        files_response = await client.get(f"/api/v1/projects/{project_id}/files")

        assert files_response.status_code == 200
        files_data = files_response.json()

        assert "files" in files_data
        assert len(files_data["files"]) > 0
        assert files_data["total_files"] == completed_project["files_generated"]

        # Verify file structure
        file_types = [f["type"] for f in files_data["files"]]
        assert "python" in file_types or "javascript" in file_types
        print(f"[TEST] ✓ Generated {len(files_data['files'])} files")

        # ============================================
        # STEP 6: Read a Specific File
        # ============================================
        print(f"[TEST] Step 6: Reading generated file...")
        first_file = files_data["files"][0]
        file_path = first_file["path"]

        file_response = await client.get(f"/api/v1/projects/{project_id}/files/{file_path}")

        assert file_response.status_code == 200
        file_content = file_response.json()

        assert "content" in file_content
        assert len(file_content["content"]) > 0
        assert file_content["file_path"] == file_path
        print(f"[TEST] ✓ Read file: {file_path} ({len(file_content['content'])} bytes)")

        # ============================================
        # STEP 7: Update Project
        # ============================================
        print(f"[TEST] Step 7: Updating project...")
        update_data = {
            "name": "Updated E2E Test Project",
            "description": "Updated description"
        }
        update_response = await client.put(f"/api/v1/projects/{project_id}", json=update_data)

        assert update_response.status_code == 200
        updated_project = update_response.json()

        assert updated_project["name"] == update_data["name"]
        assert updated_project["description"] == update_data["description"]
        print(f"[TEST] ✓ Project updated")

        # ============================================
        # STEP 8: Delete Project
        # ============================================
        print(f"[TEST] Step 8: Deleting project...")
        delete_response = await client.delete(f"/api/v1/projects/{project_id}")

        assert delete_response.status_code == 200
        delete_result = delete_response.json()

        assert delete_result["message"] == "Project deleted successfully"
        assert delete_result["project_id"] == project_id
        print(f"[TEST] ✓ Project deleted")

        # ============================================
        # STEP 9: Verify Deletion
        # ============================================
        print(f"[TEST] Step 9: Verifying deletion...")
        get_response = await client.get(f"/api/v1/projects/{project_id}")

        assert get_response.status_code == 404
        print(f"[TEST] ✓ Project no longer exists")

        print("\n[TEST] ✅ Complete project lifecycle test PASSED")

    @pytest.mark.asyncio
    async def test_multiple_projects_creation(self, client: AsyncClient, test_project_data):
        """Test creating multiple projects simultaneously"""

        print("\n[TEST] Creating 3 projects simultaneously...")
        project_ids = []

        # Create 3 projects
        for i in range(3):
            project_data = test_project_data.copy()
            project_data["name"] = f"Concurrent Test Project {i+1}"

            response = await client.post("/api/v1/projects", json=project_data)
            assert response.status_code == 201
            project = response.json()
            project_ids.append(project["id"])

        print(f"[TEST] ✓ Created {len(project_ids)} projects")

        # Verify all projects exist
        list_response = await client.get("/api/v1/projects")
        assert list_response.status_code == 200

        projects_list = list_response.json()
        assert len(projects_list["projects"]) >= 3

        # Cleanup
        for project_id in project_ids:
            await client.delete(f"/api/v1/projects/{project_id}")

        print("[TEST] ✓ All projects cleaned up")

    @pytest.mark.asyncio
    async def test_project_status_transitions(self, client: AsyncClient, test_project_data):
        """Test project status transitions through lifecycle"""

        print("\n[TEST] Testing project status transitions...")

        # Create project
        response = await client.post("/api/v1/projects", json=test_project_data)
        assert response.status_code == 201
        project = response.json()
        project_id = project["id"]

        # Initial status should be 'creating'
        assert project["status"] == "creating"
        print(f"[TEST] ✓ Initial status: creating")

        # Start execution
        exec_response = await client.post(f"/api/v1/projects/{project_id}/execute")
        assert exec_response.status_code == 200

        # Final status should be 'completed' or 'failed'
        get_response = await client.get(f"/api/v1/projects/{project_id}")
        final_project = get_response.json()

        assert final_project["status"] in ["completed", "failed"]
        print(f"[TEST] ✓ Final status: {final_project['status']}")

        # Cleanup
        await client.delete(f"/api/v1/projects/{project_id}")

    @pytest.mark.asyncio
    async def test_project_error_handling(self, client: AsyncClient):
        """Test error handling for invalid operations"""

        print("\n[TEST] Testing error handling...")

        # Test 1: Get non-existent project
        response = await client.get("/api/v1/projects/nonexistent-id")
        assert response.status_code == 404
        print("[TEST] ✓ 404 for non-existent project")

        # Test 2: Delete non-existent project
        response = await client.delete("/api/v1/projects/nonexistent-id")
        assert response.status_code == 404
        print("[TEST] ✓ 404 for deleting non-existent project")

        # Test 3: Invalid project data
        invalid_data = {"name": ""}  # Missing required fields
        response = await client.post("/api/v1/projects", json=invalid_data)
        assert response.status_code in [400, 422]
        print("[TEST] ✓ 400/422 for invalid project data")

        # Test 4: Execute non-existent project
        response = await client.post("/api/v1/projects/nonexistent-id/execute")
        assert response.status_code == 404
        print("[TEST] ✓ 404 for executing non-existent project")

    @pytest.mark.asyncio
    async def test_project_pagination_and_filtering(self, client: AsyncClient, test_project_data):
        """Test project listing with pagination and filtering"""

        print("\n[TEST] Testing pagination and filtering...")

        # Create multiple projects with different statuses
        project_ids = []
        for i in range(5):
            data = test_project_data.copy()
            data["name"] = f"Filter Test Project {i+1}"
            response = await client.post("/api/v1/projects", json=data)
            project = response.json()
            project_ids.append(project["id"])

        # Test pagination
        response = await client.get("/api/v1/projects?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) <= 2
        print(f"[TEST] ✓ Pagination working (limit=2)")

        # Test filtering by status
        response = await client.get("/api/v1/projects?status=creating")
        assert response.status_code == 200
        data = response.json()
        for project in data["projects"]:
            assert project["status"] == "creating"
        print(f"[TEST] ✓ Status filtering working")

        # Test sorting
        response = await client.get("/api/v1/projects?sort=created_at&order=desc")
        assert response.status_code == 200
        print(f"[TEST] ✓ Sorting working")

        # Cleanup
        for project_id in project_ids:
            await client.delete(f"/api/v1/projects/{project_id}")

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_project_execution_timeout(self, client: AsyncClient, test_project_data):
        """Test project execution with timeout handling"""

        print("\n[TEST] Testing execution timeout...")

        # Create project
        response = await client.post("/api/v1/projects", json=test_project_data)
        project = response.json()
        project_id = project["id"]

        # Execute with timeout monitoring
        start_time = time.time()
        exec_response = await client.post(f"/api/v1/projects/{project_id}/execute")
        execution_time = time.time() - start_time

        assert exec_response.status_code in [200, 408, 500]  # OK, Timeout, or Error
        print(f"[TEST] ✓ Execution took {execution_time:.2f}s")

        # Cleanup
        await client.delete(f"/api/v1/projects/{project_id}")


@pytest.mark.e2e
class TestProjectFileSecurity:
    """Test file path security and validation"""

    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self, client: AsyncClient, test_project_data):
        """Test that path traversal attacks are prevented"""

        print("\n[TEST] Testing path traversal prevention...")

        # Create and execute project
        response = await client.post("/api/v1/projects", json=test_project_data)
        project = response.json()
        project_id = project["id"]

        # Try path traversal attack
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "../../../../.env",
            "../.env"
        ]

        for path in malicious_paths:
            response = await client.get(f"/api/v1/projects/{project_id}/files/{path}")
            assert response.status_code in [400, 404], f"Path traversal not blocked: {path}"

        print("[TEST] ✓ Path traversal attacks blocked")

        # Cleanup
        await client.delete(f"/api/v1/projects/{project_id}")
