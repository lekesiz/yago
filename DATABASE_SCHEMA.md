# YAGO v8.0 - PostgreSQL Database Schema

## Tables

### 1. projects
Stores all user projects

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'creating',
    progress INTEGER DEFAULT 0,

    -- Brief and configuration (JSON)
    brief JSONB,
    config JSONB,

    -- Model selection
    primary_model VARCHAR(100),
    agent_role VARCHAR(100),
    strategy VARCHAR(50) DEFAULT 'balanced',
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 4000,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Results
    project_path VARCHAR(500),
    cost_estimate FLOAT DEFAULT 0.0,
    actual_cost FLOAT DEFAULT 0.0,
    files_generated INTEGER DEFAULT 0,
    lines_of_code INTEGER DEFAULT 0,

    -- Errors and logs
    errors JSONB DEFAULT '[]'::jsonb,
    logs JSONB DEFAULT '[]'::jsonb,

    -- User reference (for future auth)
    user_id UUID,

    CONSTRAINT status_check CHECK (status IN ('creating', 'in_progress', 'executing', 'completed', 'failed', 'paused'))
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
CREATE INDEX idx_projects_user_id ON projects(user_id);
```

### 2. clarification_sessions
Stores clarification Q&A sessions

```sql
CREATE TABLE clarification_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- Session data
    project_idea TEXT NOT NULL,
    depth VARCHAR(20) NOT NULL,
    questions JSONB NOT NULL,
    answers JSONB DEFAULT '{}'::jsonb,

    -- State
    current_question INTEGER DEFAULT 0,
    total_questions INTEGER NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,

    -- AI provider used
    ai_provider VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    CONSTRAINT depth_check CHECK (depth IN ('minimal', 'standard', 'full'))
);

CREATE INDEX idx_sessions_project_id ON clarification_sessions(project_id);
CREATE INDEX idx_sessions_created_at ON clarification_sessions(created_at DESC);
```

### 3. generated_files
Tracks generated code files

```sql
CREATE TABLE generated_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

    -- File info
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    content TEXT,
    size INTEGER,
    lines INTEGER,

    -- Metadata
    ai_provider VARCHAR(50),
    generated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(project_id, file_path)
);

CREATE INDEX idx_files_project_id ON generated_files(project_id);
CREATE INDEX idx_files_type ON generated_files(file_type);
```

### 4. ai_provider_usage
Tracks AI provider usage and costs

```sql
CREATE TABLE ai_provider_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

    -- Provider details
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,

    -- Usage metrics
    request_type VARCHAR(50),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    cost FLOAT,

    -- Performance
    latency_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    -- Timestamp
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT provider_check CHECK (provider IN ('openai', 'anthropic', 'gemini', 'cursor'))
);

CREATE INDEX idx_usage_provider ON ai_provider_usage(provider);
CREATE INDEX idx_usage_project_id ON ai_provider_usage(project_id);
CREATE INDEX idx_usage_created_at ON ai_provider_usage(created_at DESC);
```

### 5. users (for future auth)
User accounts

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

---

## Relationships

```
users (1) ─┬─> (n) projects
           │
projects (1) ─┬─> (1) clarification_sessions
              ├─> (n) generated_files
              └─> (n) ai_provider_usage
```

---

## Sample Queries

### Get project with all related data
```sql
SELECT
    p.*,
    cs.questions,
    cs.answers,
    COUNT(gf.id) as file_count,
    SUM(apu.cost) as total_ai_cost
FROM projects p
LEFT JOIN clarification_sessions cs ON cs.project_id = p.id
LEFT JOIN generated_files gf ON gf.project_id = p.id
LEFT JOIN ai_provider_usage apu ON apu.project_id = p.id
WHERE p.id = $1
GROUP BY p.id, cs.id;
```

### Get provider usage statistics
```sql
SELECT
    provider,
    model,
    COUNT(*) as total_requests,
    SUM(total_tokens) as total_tokens,
    SUM(cost) as total_cost,
    AVG(latency_ms) as avg_latency,
    (SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
FROM ai_provider_usage
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY provider, model
ORDER BY total_cost DESC;
```

### Get recent active projects
```sql
SELECT
    id,
    name,
    status,
    progress,
    files_generated,
    actual_cost,
    updated_at
FROM projects
WHERE status IN ('in_progress', 'executing')
ORDER BY updated_at DESC
LIMIT 10;
```

---

## Migration Strategy

1. **Phase 1**: Create tables (this schema)
2. **Phase 2**: Create SQLAlchemy models
3. **Phase 3**: Update endpoints to use database
4. **Phase 4**: Migrate in-memory data (if any)
5. **Phase 5**: Remove in-memory dictionaries

---

**Created**: 2025-10-29
**Version**: 8.0.0
**Status**: Schema Design Complete
