# 📚 YAGO v8.0 - Complete API Documentation

**Version**: 8.0.0
**Base URL**: `http://localhost:8000`
**Last Updated**: 2025-10-29

---

## 📋 Table of Contents

1. [Health & Status](#health--status)
2. [Projects](#projects)
3. [Code Execution](#code-execution)
4. [File Management](#file-management)
5. [Clarification Sessions](#clarification-sessions)
6. [AI Providers](#ai-providers)
7. [Analytics](#analytics)
8. [Cost Tracking](#cost-tracking)

---

## 🏥 Health & Status

### GET `/health`

Check API health and version information.

**Response**:
```json
{
  "status": "healthy",
  "version": "8.0.0",
  "environment": "development",
  "timestamp": "2025-10-29T18:00:00.000Z",
  "components": {
    "api": "operational",
    "database": "operational",
    "ai_providers": {
      "openai": "operational",
      "anthropic": "operational",
      "gemini": "operational",
      "cursor": "operational"
    }
  }
}
```

**Status Codes**:
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is degraded

---

## 📁 Projects

### POST `/api/v1/projects`

Create a new project.

**Request Body**:
```json
{
  "name": "My Task Management API",
  "description": "REST API for task management with user authentication",
  "brief": {
    "project_idea": "REST API for task management",
    "key_features": ["CRUD operations", "User authentication", "PostgreSQL database"],
    "tech_stack": "FastAPI, PostgreSQL, JWT",
    "target_audience": "Small businesses",
    "constraints": "Must be RESTful",
    "success_criteria": "100% test coverage"
  },
  "config": {
    "primary_model": "gpt-4-turbo-preview",
    "agent_role": "senior_developer",
    "strategy": "balanced",
    "temperature": 0.7,
    "max_tokens": 4000
  }
}
```

**Response**:
```json
{
  "id": "145d44c5-b964-485d-9980-7ac1053436e3",
  "name": "My Task Management API",
  "description": "REST API for task management with user authentication",
  "status": "creating",
  "progress": 0,
  "brief": { ... },
  "config": { ... },
  "created_at": "2025-10-29T18:00:00.000Z",
  "updated_at": "2025-10-29T18:00:00.000Z",
  "cost_estimate": 0.0,
  "actual_cost": 0.0
}
```

**Status Codes**:
- `201 Created` - Project created successfully
- `400 Bad Request` - Invalid request body
- `500 Internal Server Error` - Server error

---

### GET `/api/v1/projects`

List all projects with optional filtering.

**Query Parameters**:
- `status` (optional): Filter by status (`creating`, `in_progress`, `executing`, `completed`, `failed`, `paused`)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Skip N results (default: 0)
- `sort` (optional): Sort field (default: `created_at`)
- `order` (optional): Sort order (`asc` or `desc`, default: `desc`)

**Example**: `/api/v1/projects?status=completed&limit=10`

**Response**:
```json
{
  "projects": [
    {
      "id": "145d44c5-b964-485d-9980-7ac1053436e3",
      "name": "My Task Management API",
      "description": "REST API for task management",
      "status": "completed",
      "progress": 100,
      "files_generated": 7,
      "lines_of_code": 386,
      "actual_cost": 0.0123,
      "created_at": "2025-10-29T17:00:00.000Z",
      "completed_at": "2025-10-29T18:00:00.000Z"
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

**Status Codes**:
- `200 OK` - Projects retrieved successfully

---

### GET `/api/v1/projects/{project_id}`

Get a specific project by ID.

**Path Parameters**:
- `project_id` (required): Project UUID

**Response**:
```json
{
  "id": "145d44c5-b964-485d-9980-7ac1053436e3",
  "name": "My Task Management API",
  "description": "REST API for task management",
  "status": "completed",
  "progress": 100,
  "brief": {
    "project_idea": "REST API for task management",
    "key_features": ["CRUD operations", "User auth"]
  },
  "config": {
    "primary_model": "gpt-4-turbo-preview",
    "temperature": 0.7
  },
  "project_path": "generated_projects/145d44c5-b964-485d-9980-7ac1053436e3",
  "files_generated": 7,
  "lines_of_code": 386,
  "cost_estimate": 0.01,
  "actual_cost": 0.0123,
  "created_at": "2025-10-29T17:00:00.000Z",
  "started_at": "2025-10-29T17:30:00.000Z",
  "completed_at": "2025-10-29T18:00:00.000Z",
  "errors": [],
  "logs": [
    "Architecture generated",
    "Main file created",
    "Tests generated"
  ]
}
```

**Status Codes**:
- `200 OK` - Project found
- `404 Not Found` - Project not found

---

### PUT `/api/v1/projects/{project_id}`

Update a project.

**Path Parameters**:
- `project_id` (required): Project UUID

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "paused"
}
```

**Response**: Same as GET `/api/v1/projects/{project_id}`

**Status Codes**:
- `200 OK` - Project updated successfully
- `404 Not Found` - Project not found
- `400 Bad Request` - Invalid request body

---

### DELETE `/api/v1/projects/{project_id}`

Delete a project and all associated files.

**Path Parameters**:
- `project_id` (required): Project UUID

**Response**:
```json
{
  "message": "Project deleted successfully",
  "project_id": "145d44c5-b964-485d-9980-7ac1053436e3",
  "files_deleted": 7
}
```

**Status Codes**:
- `200 OK` - Project deleted successfully
- `404 Not Found` - Project not found

---

## 🚀 Code Execution

### POST `/api/v1/projects/{project_id}/execute`

Execute AI code generation for a project. This is the core feature of YAGO!

**Path Parameters**:
- `project_id` (required): Project UUID

**Process**:
1. Generates system architecture using GPT-4 Turbo
2. Creates main application file
3. Generates data models
4. Creates API endpoints using Claude Opus
5. Generates unit tests using GPT-3.5 Turbo
6. Creates README documentation
7. Generates dependencies file (requirements.txt or package.json)
8. Saves all files to filesystem
9. Calculates statistics (lines of code, cost)
10. Updates project status to `completed`

**Response**:
```json
{
  "status": "success",
  "message": "✅ Code generation completed!",
  "result": {
    "files_generated": 7,
    "lines_of_code": 386,
    "project_path": "generated_projects/145d44c5-b964-485d-9980-7ac1053436e3",
    "cost": 0.0123,
    "execution_time_seconds": 45.2,
    "files": [
      {"path": "src/main.py", "lines": 42, "size": 1218},
      {"path": "src/models.py", "lines": 38, "size": 992},
      {"path": "src/api.py", "lines": 56, "size": 1582},
      {"path": "tests/test_main.py", "lines": 51, "size": 1482},
      {"path": "tests/test_models.py", "lines": 98, "size": 2894},
      {"path": "README.md", "lines": 95, "size": 2881},
      {"path": "requirements.txt", "lines": 6, "size": 105}
    ]
  }
}
```

**Status Codes**:
- `200 OK` - Code generation completed successfully
- `404 Not Found` - Project not found
- `400 Bad Request` - Project already executed or invalid state
- `500 Internal Server Error` - AI provider error or execution failure

**Errors**:
```json
{
  "status": "error",
  "message": "Code generation failed",
  "error": "OpenAI API rate limit exceeded",
  "project_id": "145d44c5-b964-485d-9980-7ac1053436e3"
}
```

---

## 📂 File Management

### GET `/api/v1/projects/{project_id}/files`

List all generated files for a project.

**Path Parameters**:
- `project_id` (required): Project UUID

**Response**:
```json
{
  "project_id": "145d44c5-b964-485d-9980-7ac1053436e3",
  "project_path": "generated_projects/145d44c5-b964-485d-9980-7ac1053436e3",
  "total_files": 7,
  "total_size": 11154,
  "files": [
    {
      "path": "src/main.py",
      "size": 1218,
      "modified": "2025-10-29T18:00:00.000Z",
      "type": "python"
    },
    {
      "path": "src/models.py",
      "size": 992,
      "modified": "2025-10-29T18:00:00.000Z",
      "type": "python"
    },
    {
      "path": "src/api.py",
      "size": 1582,
      "modified": "2025-10-29T18:00:00.000Z",
      "type": "python"
    },
    {
      "path": "tests/test_main.py",
      "size": 1482,
      "modified": "2025-10-29T18:00:00.000Z",
      "type": "python"
    },
    {
      "path": "tests/test_models.py",
      "size": 2894,
      "modified": "2025-10-29T18:00:00.000Z",
      "type": "python"
    },
    {
      "path": "README.md",
      "size": 2881,
      "modified": "2025-10-29T18:00:00.000Z",
      "type": "markdown"
    },
    {
      "path": "requirements.txt",
      "size": 105,
      "modified": "2025-10-29T18:00:00.000Z",
      "type": "text"
    }
  ]
}
```

**Status Codes**:
- `200 OK` - Files retrieved successfully
- `404 Not Found` - Project not found or no files generated

---

### GET `/api/v1/projects/{project_id}/files/{file_path:path}`

Get content of a specific generated file.

**Path Parameters**:
- `project_id` (required): Project UUID
- `file_path` (required): Relative file path (e.g., `src/main.py`)

**Security**: Prevents path traversal attacks (rejects paths with `..`)

**Response**:
```json
{
  "project_id": "145d44c5-b964-485d-9980-7ac1053436e3",
  "file_path": "src/main.py",
  "content": "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/\")\nasync def root():\n    return {\"message\": \"Hello World\"}",
  "size": 1218,
  "lines": 42,
  "type": "python",
  "modified": "2025-10-29T18:00:00.000Z"
}
```

**Status Codes**:
- `200 OK` - File content retrieved successfully
- `404 Not Found` - Project or file not found
- `400 Bad Request` - Invalid file path (security violation)

---

## 💬 Clarification Sessions

### POST `/api/v1/clarifications/start`

Start a new clarification session to gather project requirements.

**Request Body**:
```json
{
  "project_idea": "E-commerce platform with product catalog and checkout",
  "depth": "standard",
  "provider": "openai"
}
```

**Parameters**:
- `project_idea` (required): Brief description of the project
- `depth` (required): `minimal` (~10 questions), `standard` (~20 questions), or `full` (~40 questions)
- `provider` (optional): AI provider to use (`openai`, `anthropic`, `gemini`, `cursor`, or `auto`)

**Response**:
```json
{
  "session_id": "a5d8c2e1-3f4b-4a1d-9e2c-8b7a6f5d4c3e",
  "project_idea": "E-commerce platform with product catalog and checkout",
  "depth": "standard",
  "total_questions": 18,
  "current_question": 0,
  "questions": [
    {
      "id": 0,
      "question": "What programming language and framework do you prefer for the backend?",
      "category": "technical",
      "importance": "high"
    },
    {
      "id": 1,
      "question": "What database system would you like to use?",
      "category": "technical",
      "importance": "high"
    }
  ],
  "ai_provider": "openai",
  "is_completed": false,
  "created_at": "2025-10-29T18:00:00.000Z"
}
```

**Status Codes**:
- `201 Created` - Session created successfully
- `400 Bad Request` - Invalid request body
- `503 Service Unavailable` - AI provider unavailable

---

### GET `/api/v1/clarifications/{session_id}`

Get details of a clarification session.

**Path Parameters**:
- `session_id` (required): Session UUID

**Response**:
```json
{
  "session_id": "a5d8c2e1-3f4b-4a1d-9e2c-8b7a6f5d4c3e",
  "project_idea": "E-commerce platform",
  "depth": "standard",
  "total_questions": 18,
  "current_question": 5,
  "questions": [ ... ],
  "answers": {
    "0": "FastAPI with PostgreSQL",
    "1": "PostgreSQL with SQLAlchemy ORM",
    "2": "JWT authentication",
    "3": "React with TypeScript",
    "4": "Stripe for payments"
  },
  "is_completed": false,
  "ai_provider": "openai",
  "created_at": "2025-10-29T18:00:00.000Z",
  "updated_at": "2025-10-29T18:05:00.000Z"
}
```

**Status Codes**:
- `200 OK` - Session found
- `404 Not Found` - Session not found

---

### POST `/api/v1/clarifications/{session_id}/answer`

Answer a question in a clarification session.

**Path Parameters**:
- `session_id` (required): Session UUID

**Request Body**:
```json
{
  "question_index": 0,
  "answer": "FastAPI with PostgreSQL"
}
```

**Response**:
```json
{
  "session_id": "a5d8c2e1-3f4b-4a1d-9e2c-8b7a6f5d4c3e",
  "question_index": 0,
  "answer": "FastAPI with PostgreSQL",
  "next_question": {
    "id": 1,
    "question": "What database system would you like to use?",
    "category": "technical"
  },
  "progress": 5.56,
  "current_question": 1,
  "total_questions": 18
}
```

**Status Codes**:
- `200 OK` - Answer recorded successfully
- `404 Not Found` - Session not found
- `400 Bad Request` - Invalid question index or answer

---

### POST `/api/v1/clarifications/{session_id}/complete`

Complete a clarification session and generate project brief.

**Path Parameters**:
- `session_id` (required): Session UUID

**Request Body** (optional):
```json
{
  "agent_role": "senior_developer",
  "strategy": "balanced",
  "primary_model": "gpt-4-turbo-preview"
}
```

**Response**:
```json
{
  "session_id": "a5d8c2e1-3f4b-4a1d-9e2c-8b7a6f5d4c3e",
  "is_completed": true,
  "project_brief": {
    "project_idea": "E-commerce platform",
    "tech_stack": "FastAPI, PostgreSQL, React, Stripe",
    "key_features": [
      "Product catalog with search and filters",
      "Shopping cart with session management",
      "User authentication with JWT",
      "Stripe payment integration",
      "Admin dashboard for product management"
    ],
    "architecture": "RESTful API with React SPA frontend",
    "database_schema": {
      "tables": ["users", "products", "orders", "order_items", "payments"]
    },
    "api_endpoints": [
      "GET /api/products",
      "POST /api/cart",
      "POST /api/checkout"
    ],
    "testing_requirements": "Unit tests with pytest, 80% coverage minimum"
  },
  "completed_at": "2025-10-29T18:15:00.000Z"
}
```

**Status Codes**:
- `200 OK` - Session completed successfully
- `404 Not Found` - Session not found
- `400 Bad Request` - Not all questions answered

---

## 🤖 AI Providers

### GET `/api/v1/providers/status`

Check the availability and status of all AI providers.

**Response**:
```json
{
  "providers": {
    "openai": {
      "status": "operational",
      "models_available": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
      "last_check": "2025-10-29T18:00:00.000Z",
      "response_time_ms": 145
    },
    "anthropic": {
      "status": "operational",
      "models_available": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
      "last_check": "2025-10-29T18:00:00.000Z",
      "response_time_ms": 178
    },
    "gemini": {
      "status": "operational",
      "models_available": ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
      "last_check": "2025-10-29T18:00:00.000Z",
      "response_time_ms": 201
    },
    "cursor": {
      "status": "operational",
      "models_available": ["cursor-large"],
      "last_check": "2025-10-29T18:00:00.000Z",
      "response_time_ms": 122
    }
  },
  "summary": {
    "total_providers": 4,
    "operational": 4,
    "degraded": 0,
    "down": 0
  }
}
```

**Status Codes**:
- `200 OK` - Provider status retrieved successfully

---

### GET `/api/v1/providers/models`

List all available AI models with their capabilities and pricing.

**Response**:
```json
{
  "models": [
    {
      "id": "gpt-4-turbo-preview",
      "provider": "openai",
      "name": "GPT-4 Turbo",
      "capabilities": ["chat", "code_generation", "architecture_design"],
      "context_window": 128000,
      "pricing": {
        "input_per_1k_tokens": 0.01,
        "output_per_1k_tokens": 0.03
      },
      "recommended_for": ["complex_projects", "architecture", "high_quality_code"]
    },
    {
      "id": "claude-3-opus-20240229",
      "provider": "anthropic",
      "name": "Claude 3 Opus",
      "capabilities": ["chat", "code_generation", "api_design"],
      "context_window": 200000,
      "pricing": {
        "input_per_1k_tokens": 0.015,
        "output_per_1k_tokens": 0.075
      },
      "recommended_for": ["api_endpoints", "complex_logic"]
    },
    {
      "id": "gpt-3.5-turbo",
      "provider": "openai",
      "name": "GPT-3.5 Turbo",
      "capabilities": ["chat", "test_generation", "documentation"],
      "context_window": 16385,
      "pricing": {
        "input_per_1k_tokens": 0.0005,
        "output_per_1k_tokens": 0.0015
      },
      "recommended_for": ["tests", "documentation", "quick_tasks"]
    }
  ],
  "total_models": 9
}
```

**Status Codes**:
- `200 OK` - Models retrieved successfully

---

## 📊 Analytics

### GET `/api/v1/analytics/overview`

Get overall platform analytics.

**Query Parameters**:
- `time_range` (optional): `24h`, `7d`, `30d`, `90d`, `all` (default: `30d`)

**Response**:
```json
{
  "time_range": "30d",
  "projects": {
    "total": 45,
    "completed": 38,
    "failed": 2,
    "in_progress": 5,
    "success_rate": 84.4
  },
  "code_generation": {
    "total_files": 315,
    "total_lines": 14732,
    "average_files_per_project": 7.0,
    "average_lines_per_project": 328.0
  },
  "costs": {
    "total": 5.67,
    "average_per_project": 0.126,
    "by_provider": {
      "openai": 3.45,
      "anthropic": 1.89,
      "gemini": 0.23,
      "cursor": 0.10
    }
  },
  "performance": {
    "average_execution_time_seconds": 52.3,
    "fastest_execution_seconds": 28.1,
    "slowest_execution_seconds": 98.7
  }
}
```

**Status Codes**:
- `200 OK` - Analytics retrieved successfully

---

### GET `/api/v1/analytics/providers-usage`

Get usage analytics per AI provider.

**Query Parameters**:
- `time_range` (optional): `24h`, `7d`, `30d`, `90d`, `all` (default: `30d`)

**Response**:
```json
{
  "time_range": "30d",
  "providers": {
    "openai": {
      "requests": 142,
      "tokens_used": 1245000,
      "cost": 3.45,
      "success_rate": 98.6,
      "average_latency_ms": 145,
      "models": {
        "gpt-4-turbo-preview": {"requests": 45, "cost": 2.10},
        "gpt-3.5-turbo": {"requests": 97, "cost": 1.35}
      }
    },
    "anthropic": {
      "requests": 45,
      "tokens_used": 567000,
      "cost": 1.89,
      "success_rate": 100.0,
      "average_latency_ms": 178,
      "models": {
        "claude-3-opus-20240229": {"requests": 45, "cost": 1.89}
      }
    }
  }
}
```

**Status Codes**:
- `200 OK` - Provider analytics retrieved successfully

---

## 💰 Cost Tracking

### GET `/api/v1/costs/summary`

Get cost summary and breakdown.

**Query Parameters**:
- `time_range` (optional): `24h`, `7d`, `30d`, `90d`, `all` (default: `30d`)

**Response**:
```json
{
  "time_range": "30d",
  "total_cost": 5.67,
  "cost_by_provider": {
    "openai": 3.45,
    "anthropic": 1.89,
    "gemini": 0.23,
    "cursor": 0.10
  },
  "cost_by_operation": {
    "code_generation": 3.89,
    "clarification": 1.23,
    "architecture": 0.45,
    "tests": 0.10
  },
  "cost_trend": [
    {"date": "2025-10-22", "cost": 0.15},
    {"date": "2025-10-23", "cost": 0.23},
    {"date": "2025-10-24", "cost": 0.18}
  ]
}
```

**Status Codes**:
- `200 OK` - Cost summary retrieved successfully

---

### GET `/api/v1/costs/alerts`

Get cost alerts and budget warnings.

**Response**:
```json
{
  "budget": {
    "monthly_budget": 100.0,
    "current_spending": 5.67,
    "utilization_percent": 5.67,
    "remaining": 94.33
  },
  "alerts": [
    {
      "type": "info",
      "message": "Budget on track",
      "threshold": "20%",
      "current": "5.67%"
    }
  ],
  "projections": {
    "projected_monthly_cost": 18.90,
    "projected_utilization_percent": 18.90,
    "within_budget": true
  }
}
```

**Alert Types**:
- `info` - Budget on track (< 50%)
- `warning` - Approaching budget (50-80%)
- `critical` - Near budget limit (80-100%)
- `exceeded` - Budget exceeded (> 100%)

**Status Codes**:
- `200 OK` - Cost alerts retrieved successfully

---

## 🔒 Authentication (Coming in v8.1)

Authentication endpoints will be available in the next version.

**Planned Endpoints**:
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (JWT tokens)
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user

---

## 📝 Error Responses

All error responses follow this format:

```json
{
  "status": "error",
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project with ID 'abc123' not found",
    "details": {
      "project_id": "abc123"
    }
  },
  "timestamp": "2025-10-29T18:00:00.000Z"
}
```

**Common Error Codes**:
- `PROJECT_NOT_FOUND` - Project doesn't exist
- `SESSION_NOT_FOUND` - Clarification session doesn't exist
- `INVALID_REQUEST` - Invalid request body or parameters
- `AI_PROVIDER_ERROR` - AI provider API error
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error

---

## 🔄 Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

---

## 📚 Additional Resources

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete user manual
- **[README.md](README.md)** - Project overview
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database schema
- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Alternative API docs)

---

**Last Updated**: 2025-10-29
**Version**: 8.0.0
**Status**: Production Ready

---

<p align="center">
  <b>YAGO v8.0 API Documentation</b><br>
  Built with ❤️ by Mikail Lekesiz and Claude AI
</p>
