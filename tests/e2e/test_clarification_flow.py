"""
YAGO v8.1 - Clarification Flow E2E Tests
Testing the complete clarification workflow for gathering requirements
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session


@pytest.mark.e2e
@pytest.mark.requires_api
class TestClarificationFlow:
    """
    Test complete clarification workflow:
    1. Start clarification session
    2. Answer questions one by one
    3. Complete session
    4. Generate project brief
    5. Create project from brief
    """

    @pytest.mark.asyncio
    async def test_complete_clarification_flow(self, client: AsyncClient, test_clarification_data):
        """Test full clarification workflow from start to project creation"""

        # ============================================
        # STEP 1: Start Clarification Session
        # ============================================
        print("\n[TEST] Step 1: Starting clarification session...")
        start_response = await client.post(
            "/api/v1/clarifications/start",
            json=test_clarification_data
        )

        assert start_response.status_code == 201, f"Failed to start session: {start_response.text}"
        session = start_response.json()

        assert "session_id" in session
        assert session["project_idea"] == test_clarification_data["project_idea"]
        assert session["depth"] == test_clarification_data["depth"]
        assert session["total_questions"] > 0
        assert session["is_completed"] is False
        assert len(session["questions"]) > 0

        session_id = session["session_id"]
        total_questions = session["total_questions"]
        print(f"[TEST] ✓ Session started: {session_id}")
        print(f"[TEST]   - Total questions: {total_questions}")

        # ============================================
        # STEP 2: Get Session Details
        # ============================================
        print(f"[TEST] Step 2: Fetching session details...")
        get_response = await client.get(f"/api/v1/clarifications/{session_id}")

        assert get_response.status_code == 200
        session_details = get_response.json()

        assert session_details["session_id"] == session_id
        assert session_details["total_questions"] == total_questions
        print(f"[TEST] ✓ Session details retrieved")

        # ============================================
        # STEP 3: Answer Questions
        # ============================================
        print(f"[TEST] Step 3: Answering questions...")

        sample_answers = [
            "FastAPI with PostgreSQL",
            "JWT authentication with refresh tokens",
            "React with TypeScript",
            "Stripe for payment processing",
            "AWS or similar cloud provider",
            "Docker and Kubernetes",
            "CI/CD with GitHub Actions",
            "Unit tests with pytest, 80% coverage minimum",
            "Small to medium e-commerce businesses",
            "Must be scalable and secure"
        ]

        for i in range(min(total_questions, len(sample_answers))):
            answer_data = {
                "question_index": i,
                "answer": sample_answers[i]
            }

            answer_response = await client.post(
                f"/api/v1/clarifications/{session_id}/answer",
                json=answer_data
            )

            assert answer_response.status_code == 200, f"Failed to answer question {i}"
            answer_result = answer_response.json()

            assert answer_result["question_index"] == i
            assert answer_result["answer"] == sample_answers[i]
            assert "progress" in answer_result

            print(f"[TEST]   ✓ Answered question {i+1}/{total_questions} ({answer_result['progress']:.1f}%)")

        # ============================================
        # STEP 4: Verify All Answers Recorded
        # ============================================
        print(f"[TEST] Step 4: Verifying answers...")
        get_response = await client.get(f"/api/v1/clarifications/{session_id}")

        assert get_response.status_code == 200
        updated_session = get_response.json()

        assert len(updated_session["answers"]) > 0
        print(f"[TEST] ✓ {len(updated_session['answers'])} answers recorded")

        # ============================================
        # STEP 5: Complete Session
        # ============================================
        print(f"[TEST] Step 5: Completing session...")
        complete_data = {
            "agent_role": "senior_developer",
            "strategy": "balanced",
            "primary_model": "gpt-4-turbo-preview"
        }

        complete_response = await client.post(
            f"/api/v1/clarifications/{session_id}/complete",
            json=complete_data
        )

        assert complete_response.status_code == 200
        completion_result = complete_response.json()

        assert completion_result["is_completed"] is True
        assert "project_brief" in completion_result
        assert completion_result["project_brief"] is not None

        project_brief = completion_result["project_brief"]
        print(f"[TEST] ✓ Session completed")
        print(f"[TEST]   - Tech stack: {project_brief.get('tech_stack', 'N/A')}")
        print(f"[TEST]   - Features: {len(project_brief.get('key_features', []))}")

        # ============================================
        # STEP 6: Create Project from Brief
        # ============================================
        print(f"[TEST] Step 6: Creating project from brief...")
        project_data = {
            "name": "E2E Clarification Test Project",
            "description": "Project created from clarification session",
            "brief": project_brief,
            "config": complete_data
        }

        create_response = await client.post("/api/v1/projects", json=project_data)

        assert create_response.status_code == 201
        project = create_response.json()

        assert "id" in project
        assert project["name"] == project_data["name"]
        print(f"[TEST] ✓ Project created: {project['id']}")

        # Cleanup
        await client.delete(f"/api/v1/projects/{project['id']}")
        print(f"[TEST] ✓ Cleanup complete")

        print("\n[TEST] ✅ Complete clarification flow test PASSED")

    @pytest.mark.asyncio
    async def test_clarification_depth_levels(self, client: AsyncClient, test_clarification_data):
        """Test different clarification depth levels"""

        depths = ["minimal", "standard", "full"]

        for depth in depths:
            print(f"\n[TEST] Testing depth: {depth}")

            # Start session with specific depth
            data = test_clarification_data.copy()
            data["depth"] = depth

            response = await client.post("/api/v1/clarifications/start", json=data)
            assert response.status_code == 201

            session = response.json()
            total_questions = session["total_questions"]

            # Verify question count based on depth
            if depth == "minimal":
                assert 5 <= total_questions <= 15, f"Minimal should have 5-15 questions, got {total_questions}"
            elif depth == "standard":
                assert 15 <= total_questions <= 25, f"Standard should have 15-25 questions, got {total_questions}"
            elif depth == "full":
                assert 25 <= total_questions <= 50, f"Full should have 25-50 questions, got {total_questions}"

            print(f"[TEST] ✓ {depth}: {total_questions} questions")

    @pytest.mark.asyncio
    async def test_clarification_error_handling(self, client: AsyncClient):
        """Test error handling in clarification flow"""

        print("\n[TEST] Testing clarification error handling...")

        # Test 1: Invalid depth
        invalid_data = {
            "project_idea": "Test project",
            "depth": "invalid_depth",
            "provider": "openai"
        }
        response = await client.post("/api/v1/clarifications/start", json=invalid_data)
        assert response.status_code in [400, 422]
        print("[TEST] ✓ Invalid depth rejected")

        # Test 2: Get non-existent session
        response = await client.get("/api/v1/clarifications/nonexistent-id")
        assert response.status_code == 404
        print("[TEST] ✓ 404 for non-existent session")

        # Test 3: Answer to non-existent session
        answer_data = {"question_index": 0, "answer": "Test answer"}
        response = await client.post("/api/v1/clarifications/nonexistent-id/answer", json=answer_data)
        assert response.status_code == 404
        print("[TEST] ✓ 404 for answering non-existent session")

        # Test 4: Complete non-existent session
        response = await client.post("/api/v1/clarifications/nonexistent-id/complete")
        assert response.status_code == 404
        print("[TEST] ✓ 404 for completing non-existent session")

    @pytest.mark.asyncio
    async def test_partial_clarification_flow(self, client: AsyncClient, test_clarification_data):
        """Test partially answering questions and resuming later"""

        print("\n[TEST] Testing partial clarification flow...")

        # Start session
        start_response = await client.post("/api/v1/clarifications/start", json=test_clarification_data)
        session = start_response.json()
        session_id = session["session_id"]

        # Answer only half of the questions
        half = min(3, session["total_questions"] // 2)
        for i in range(half):
            answer_data = {
                "question_index": i,
                "answer": f"Answer {i+1}"
            }
            response = await client.post(f"/api/v1/clarifications/{session_id}/answer", json=answer_data)
            assert response.status_code == 200

        print(f"[TEST] ✓ Answered {half} questions")

        # Get session to verify partial progress
        get_response = await client.get(f"/api/v1/clarifications/{session_id}")
        updated_session = get_response.json()

        assert len(updated_session["answers"]) == half
        assert updated_session["is_completed"] is False
        print(f"[TEST] ✓ Session remains incomplete")

        # Try to complete without all answers
        complete_response = await client.post(f"/api/v1/clarifications/{session_id}/complete")
        # Should fail because not all questions answered
        assert complete_response.status_code in [400, 422]
        print(f"[TEST] ✓ Cannot complete without all answers")

    @pytest.mark.asyncio
    async def test_multiple_clarification_sessions(self, client: AsyncClient, test_clarification_data):
        """Test creating multiple clarification sessions"""

        print("\n[TEST] Creating multiple clarification sessions...")

        session_ids = []

        # Create 3 sessions
        for i in range(3):
            data = test_clarification_data.copy()
            data["project_idea"] = f"Test project {i+1}"

            response = await client.post("/api/v1/clarifications/start", json=data)
            assert response.status_code == 201

            session = response.json()
            session_ids.append(session["session_id"])

        print(f"[TEST] ✓ Created {len(session_ids)} sessions")

        # Verify all sessions exist independently
        for session_id in session_ids:
            response = await client.get(f"/api/v1/clarifications/{session_id}")
            assert response.status_code == 200
            session = response.json()
            assert session["session_id"] == session_id

        print(f"[TEST] ✓ All sessions verified")

    @pytest.mark.asyncio
    async def test_clarification_answer_validation(self, client: AsyncClient, test_clarification_data):
        """Test answer validation in clarification flow"""

        print("\n[TEST] Testing answer validation...")

        # Start session
        start_response = await client.post("/api/v1/clarifications/start", json=test_clarification_data)
        session = start_response.json()
        session_id = session["session_id"]

        # Test invalid question index (negative)
        response = await client.post(
            f"/api/v1/clarifications/{session_id}/answer",
            json={"question_index": -1, "answer": "Test"}
        )
        assert response.status_code in [400, 422]
        print("[TEST] ✓ Negative index rejected")

        # Test invalid question index (out of range)
        response = await client.post(
            f"/api/v1/clarifications/{session_id}/answer",
            json={"question_index": 999, "answer": "Test"}
        )
        assert response.status_code in [400, 422]
        print("[TEST] ✓ Out of range index rejected")

        # Test empty answer
        response = await client.post(
            f"/api/v1/clarifications/{session_id}/answer",
            json={"question_index": 0, "answer": ""}
        )
        assert response.status_code in [400, 422]
        print("[TEST] ✓ Empty answer rejected")

        # Test valid answer
        response = await client.post(
            f"/api/v1/clarifications/{session_id}/answer",
            json={"question_index": 0, "answer": "Valid answer"}
        )
        assert response.status_code == 200
        print("[TEST] ✓ Valid answer accepted")


@pytest.mark.e2e
class TestClarificationAIProviders:
    """Test clarification with different AI providers"""

    @pytest.mark.asyncio
    @pytest.mark.requires_ai
    async def test_clarification_with_different_providers(self, client: AsyncClient, test_clarification_data):
        """Test starting clarification with different AI providers"""

        providers = ["openai", "anthropic", "gemini", "auto"]

        for provider in providers:
            print(f"\n[TEST] Testing provider: {provider}")

            data = test_clarification_data.copy()
            data["provider"] = provider

            response = await client.post("/api/v1/clarifications/start", json=data)

            # Should succeed or return 503 if provider unavailable
            assert response.status_code in [201, 503]

            if response.status_code == 201:
                session = response.json()
                assert session["ai_provider"] in ["openai", "anthropic", "gemini"]
                print(f"[TEST] ✓ {provider} -> {session['ai_provider']}")
            else:
                print(f"[TEST] ⚠ {provider} unavailable")
