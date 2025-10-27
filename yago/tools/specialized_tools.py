"""
YAGO v7.0 - Specialized Tools for Dynamic Agents
Each dynamic agent gets specialized tools for their domain
"""

from crewai.tools import tool
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("YAGO.SpecializedTools")


# ============================================================================
# SECURITY AGENT TOOLS
# ============================================================================

@tool("security_scan")
def security_scan(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Scan code for security vulnerabilities

    Args:
        code: Code to scan
        language: Programming language

    Returns:
        Security scan results
    """
    vulnerabilities = []

    # Common security checks
    if language.lower() == "python":
        if "eval(" in code:
            vulnerabilities.append({
                "type": "CODE_INJECTION",
                "severity": "HIGH",
                "line": code.find("eval("),
                "message": "Use of eval() can lead to code injection"
            })

        if "exec(" in code:
            vulnerabilities.append({
                "type": "CODE_INJECTION",
                "severity": "HIGH",
                "line": code.find("exec("),
                "message": "Use of exec() can lead to code injection"
            })

        if "pickle.loads(" in code:
            vulnerabilities.append({
                "type": "INSECURE_DESERIALIZATION",
                "severity": "HIGH",
                "line": code.find("pickle.loads("),
                "message": "pickle.loads() can execute arbitrary code"
            })

        if "os.system(" in code or "subprocess.call(" in code:
            vulnerabilities.append({
                "type": "COMMAND_INJECTION",
                "severity": "HIGH",
                "line": code.find("os.system("),
                "message": "Command execution without sanitization"
            })

    return {
        "vulnerabilities": vulnerabilities,
        "total_issues": len(vulnerabilities),
        "severity_breakdown": {
            "HIGH": sum(1 for v in vulnerabilities if v["severity"] == "HIGH"),
            "MEDIUM": sum(1 for v in vulnerabilities if v["severity"] == "MEDIUM"),
            "LOW": sum(1 for v in vulnerabilities if v["severity"] == "LOW"),
        }
    }


@tool("check_authentication")
def check_authentication(code: str) -> Dict[str, Any]:
    """
    Check authentication and authorization implementation

    Args:
        code: Code to check

    Returns:
        Authentication analysis
    """
    issues = []
    recommendations = []

    # Check for common auth patterns
    has_auth = any(keyword in code for keyword in [
        "authenticate", "login", "token", "jwt", "oauth", "session"
    ])

    if not has_auth:
        issues.append("No authentication mechanism detected")
        recommendations.append("Implement authentication (JWT, OAuth2, or session-based)")

    # Check for password handling
    if "password" in code.lower():
        if "bcrypt" not in code and "scrypt" not in code and "argon2" not in code:
            issues.append("Password not properly hashed")
            recommendations.append("Use bcrypt, scrypt, or argon2 for password hashing")

    # Check for hardcoded secrets
    if any(keyword in code for keyword in ["api_key =", "secret =", "password ="]):
        issues.append("Potential hardcoded credentials detected")
        recommendations.append("Use environment variables for sensitive data")

    return {
        "has_authentication": has_auth,
        "issues": issues,
        "recommendations": recommendations,
        "score": 100 - (len(issues) * 20)
    }


@tool("encrypt_data")
def encrypt_data(data: str, algorithm: str = "AES256") -> Dict[str, Any]:
    """
    Generate encryption code for data protection

    Args:
        data: Data type to encrypt
        algorithm: Encryption algorithm

    Returns:
        Encryption implementation
    """
    return {
        "algorithm": algorithm,
        "implementation": f"""
from cryptography.fernet import Fernet
import base64
import os

# Generate key (store securely!)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted_{data} = cipher.encrypt({data}.encode())

# Decrypt
decrypted_{data} = cipher.decrypt(encrypted_{data}).decode()
        """,
        "dependencies": ["cryptography"],
        "best_practices": [
            "Store encryption keys in secure key management service",
            "Rotate keys regularly",
            "Use different keys for different data types"
        ]
    }


# ============================================================================
# DEVOPS AGENT TOOLS
# ============================================================================

@tool("generate_dockerfile")
def generate_dockerfile(
    language: str,
    framework: Optional[str] = None,
    dependencies: Optional[List[str]] = None
) -> str:
    """
    Generate Dockerfile for application

    Args:
        language: Programming language
        framework: Framework (e.g., Flask, Django, Express)
        dependencies: Additional dependencies

    Returns:
        Dockerfile content
    """
    if language.lower() == "python":
        base_image = "python:3.11-slim"
        install_cmd = "pip install --no-cache-dir -r requirements.txt"

        if framework and "django" in framework.lower():
            cmd = 'CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]'
        elif framework and "flask" in framework.lower():
            cmd = 'CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]'
        else:
            cmd = 'CMD ["python", "main.py"]'

    elif language.lower() == "node":
        base_image = "node:18-alpine"
        install_cmd = "npm ci --only=production"
        cmd = 'CMD ["node", "index.js"]'

    else:
        base_image = "ubuntu:22.04"
        install_cmd = "# Add your install commands"
        cmd = 'CMD ["./app"]'

    dockerfile = f"""FROM {base_image}

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt ./
# COPY package.json package-lock.json ./

# Install dependencies
RUN {install_cmd}

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
{cmd}
"""

    return dockerfile


@tool("generate_kubernetes_manifest")
def generate_kubernetes_manifest(
    app_name: str,
    replicas: int = 3,
    port: int = 8000
) -> Dict[str, str]:
    """
    Generate Kubernetes deployment manifest

    Args:
        app_name: Application name
        replicas: Number of replicas
        port: Application port

    Returns:
        Kubernetes manifests
    """
    deployment = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {app_name}:latest
        ports:
        - containerPort: {port}
        env:
        - name: PORT
          value: "{port}"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: {port}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: {port}
          initialDelaySeconds: 5
          periodSeconds: 5
"""

    service = f"""apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
spec:
  selector:
    app: {app_name}
  ports:
  - protocol: TCP
    port: 80
    targetPort: {port}
  type: LoadBalancer
"""

    return {
        "deployment.yaml": deployment,
        "service.yaml": service
    }


@tool("setup_cicd_pipeline")
def setup_cicd_pipeline(
    platform: str = "github",
    language: str = "python",
    tests: bool = True
) -> str:
    """
    Generate CI/CD pipeline configuration

    Args:
        platform: CI/CD platform (github, gitlab, jenkins)
        language: Programming language
        tests: Include test stage

    Returns:
        Pipeline configuration
    """
    if platform.lower() == "github":
        pipeline = f"""name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up {language.title()}
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    {"- name: Run tests" if tests else "# Tests disabled"}
      {"run: pytest --cov=. --cov-report=xml" if tests else ""}

    - name: Security scan
      run: |
        pip install bandit
        bandit -r . -f json -o bandit-report.json

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t app:${{{{ github.sha }}}} .

    - name: Push to registry
      run: |
        echo "${{{{ secrets.DOCKER_PASSWORD }}}}" | docker login -u "${{{{ secrets.DOCKER_USERNAME }}}}" --password-stdin
        docker push app:${{{{ github.sha }}}}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        # Add deployment commands here
        echo "Deploying to production..."
"""
        return pipeline

    else:
        return f"# {platform} pipeline configuration not yet implemented"


# ============================================================================
# DATABASE AGENT TOOLS
# ============================================================================

@tool("generate_database_schema")
def generate_database_schema(
    entities: List[str],
    database_type: str = "postgresql"
) -> str:
    """
    Generate database schema from entities

    Args:
        entities: List of entity names
        database_type: Database type (postgresql, mysql, mongodb)

    Returns:
        Database schema SQL/NoSQL
    """
    if database_type.lower() in ["postgresql", "postgres", "mysql"]:
        schema = "-- Database Schema\n\n"

        for entity in entities:
            schema += f"""CREATE TABLE {entity.lower()}s (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_{entity.lower()}s_name ON {entity.lower()}s(name);

"""

        return schema

    elif database_type.lower() == "mongodb":
        schema = "// MongoDB Schema (Mongoose)\n\n"

        for entity in entities:
            schema += f"""const {entity}Schema = new Schema({{
  name: {{ type: String, required: true }},
  createdAt: {{ type: Date, default: Date.now }},
  updatedAt: {{ type: Date, default: Date.now }}
}});

const {entity} = mongoose.model('{entity}', {entity}Schema);

"""

        return schema

    else:
        return f"# {database_type} schema generation not yet implemented"


@tool("optimize_query")
def optimize_query(query: str, database_type: str = "postgresql") -> Dict[str, Any]:
    """
    Analyze and optimize database query

    Args:
        query: SQL query to optimize
        database_type: Database type

    Returns:
        Optimization suggestions
    """
    suggestions = []
    optimized_query = query

    # Check for missing indexes
    if "WHERE" in query.upper() and "INDEX" not in query.upper():
        suggestions.append({
            "type": "MISSING_INDEX",
            "severity": "MEDIUM",
            "message": "Consider adding index on WHERE clause columns"
        })

    # Check for SELECT *
    if "SELECT *" in query.upper():
        suggestions.append({
            "type": "SELECT_ALL",
            "severity": "LOW",
            "message": "Avoid SELECT *, specify only needed columns"
        })
        optimized_query = query.replace("SELECT *", "SELECT id, name, created_at")

    # Check for N+1 queries
    if "JOIN" not in query.upper() and "SELECT" in query.upper():
        suggestions.append({
            "type": "POTENTIAL_N_PLUS_1",
            "severity": "HIGH",
            "message": "Consider using JOIN instead of multiple queries"
        })

    return {
        "original_query": query,
        "optimized_query": optimized_query,
        "suggestions": suggestions,
        "estimated_improvement": f"{len(suggestions) * 15}%"
    }


@tool("generate_migration")
def generate_migration(
    table_name: str,
    operation: str,
    columns: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate database migration script

    Args:
        table_name: Table name
        operation: create, alter, drop
        columns: Column definitions

    Returns:
        Migration script
    """
    if operation.lower() == "create":
        migration = f"""-- Migration: Create {table_name}
-- Date: {import_datetime()}

CREATE TABLE {table_name} (
    id SERIAL PRIMARY KEY,
"""

        if columns:
            for col in columns:
                migration += f"    {col['name']} {col['type']},\n"

        migration += """    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rollback
-- DROP TABLE {table_name};
"""

        return migration

    elif operation.lower() == "alter":
        migration = f"""-- Migration: Alter {table_name}
-- Date: {import_datetime()}

ALTER TABLE {table_name}
"""

        if columns:
            for col in columns:
                migration += f"    ADD COLUMN {col['name']} {col['type']},\n"

        migration = migration.rstrip(",\n") + ";\n"

        return migration

    else:
        return f"-- {operation} operation not yet implemented"


def import_datetime():
    """Helper to import datetime"""
    from datetime import datetime
    return datetime.now().isoformat()


# ============================================================================
# FRONTEND AGENT TOOLS
# ============================================================================

@tool("generate_react_component")
def generate_react_component(
    component_name: str,
    component_type: str = "functional",
    has_state: bool = False
) -> str:
    """
    Generate React component boilerplate

    Args:
        component_name: Component name
        component_type: functional or class
        has_state: Whether component has state

    Returns:
        React component code
    """
    if component_type.lower() == "functional":
        if has_state:
            component = f"""import React, {{ useState, useEffect }} from 'react';

interface {component_name}Props {{
  // Add your props here
}}

const {component_name}: React.FC<{component_name}Props> = (props) => {{
  const [state, setState] = useState<any>(null);

  useEffect(() => {{
    // Component did mount
    return () => {{
      // Cleanup
    }};
  }}, []);

  return (
    <div className="{component_name.lower()}">
      <h1>{component_name}</h1>
      {{/* Your JSX here */}}
    </div>
  );
}};

export default {component_name};
"""
        else:
            component = f"""import React from 'react';

interface {component_name}Props {{
  // Add your props here
}}

const {component_name}: React.FC<{component_name}Props> = (props) => {{
  return (
    <div className="{component_name.lower()}">
      <h1>{component_name}</h1>
      {{/* Your JSX here */}}
    </div>
  );
}};

export default {component_name};
"""

        return component

    else:
        return f"# Class components not recommended in modern React"


@tool("generate_api_client")
def generate_api_client(
    base_url: str,
    endpoints: List[str]
) -> str:
    """
    Generate API client for frontend

    Args:
        base_url: API base URL
        endpoints: List of endpoints

    Returns:
        API client code
    """
    client = f"""import axios from 'axios';

const API_BASE_URL = '{base_url}';

const apiClient = axios.create({{
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {{
    'Content-Type': 'application/json',
  }},
}});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {{
    const token = localStorage.getItem('auth_token');
    if (token) {{
      config.headers.Authorization = `Bearer ${{token}}`;
    }}
    return config;
  }},
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {{
    if (error.response?.status === 401) {{
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }}
    return Promise.reject(error);
  }}
);

"""

    for endpoint in endpoints:
        endpoint_name = endpoint.strip('/').replace('/', '_')
        client += f"""
export const get{endpoint_name.title().replace('_', '')} = async () => {{
  const response = await apiClient.get('{endpoint}');
  return response.data;
}};

export const create{endpoint_name.title().replace('_', '')} = async (data: any) => {{
  const response = await apiClient.post('{endpoint}', data);
  return response.data;
}};

export const update{endpoint_name.title().replace('_', '')} = async (id: string, data: any) => {{
  const response = await apiClient.put(`{endpoint}/${{id}}`, data);
  return response.data;
}};

export const delete{endpoint_name.title().replace('_', '')} = async (id: string) => {{
  const response = await apiClient.delete(`{endpoint}/${{id}}`);
  return response.data;
}};
"""

    return client


# ============================================================================
# API DESIGN AGENT TOOLS
# ============================================================================

@tool("design_rest_api")
def design_rest_api(
    resources: List[str],
    authentication: str = "JWT"
) -> Dict[str, Any]:
    """
    Design RESTful API structure

    Args:
        resources: List of resources
        authentication: Auth type (JWT, OAuth2, Basic)

    Returns:
        API design specification
    """
    endpoints = {}

    for resource in resources:
        resource_lower = resource.lower()
        endpoints[resource] = {
            "list": {
                "method": "GET",
                "path": f"/api/v1/{resource_lower}s",
                "description": f"Get list of {resource_lower}s",
                "auth_required": True,
                "query_params": ["page", "limit", "sort", "filter"]
            },
            "get": {
                "method": "GET",
                "path": f"/api/v1/{resource_lower}s/{{id}}",
                "description": f"Get single {resource_lower}",
                "auth_required": True,
                "path_params": ["id"]
            },
            "create": {
                "method": "POST",
                "path": f"/api/v1/{resource_lower}s",
                "description": f"Create new {resource_lower}",
                "auth_required": True,
                "body": {resource_lower: "object"}
            },
            "update": {
                "method": "PUT",
                "path": f"/api/v1/{resource_lower}s/{{id}}",
                "description": f"Update {resource_lower}",
                "auth_required": True,
                "path_params": ["id"],
                "body": {resource_lower: "object"}
            },
            "delete": {
                "method": "DELETE",
                "path": f"/api/v1/{resource_lower}s/{{id}}",
                "description": f"Delete {resource_lower}",
                "auth_required": True,
                "path_params": ["id"]
            }
        }

    return {
        "api_version": "v1",
        "base_url": "/api/v1",
        "authentication": authentication,
        "endpoints": endpoints,
        "response_format": {
            "success": {
                "status": "success",
                "data": "object"
            },
            "error": {
                "status": "error",
                "message": "string",
                "code": "string"
            }
        }
    }


# ============================================================================
# PERFORMANCE AGENT TOOLS
# ============================================================================

@tool("analyze_performance")
def analyze_performance(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code for performance issues

    Args:
        code: Code to analyze
        language: Programming language

    Returns:
        Performance analysis
    """
    issues = []
    recommendations = []

    if language.lower() == "python":
        # Check for inefficient patterns
        if "for " in code and "append(" in code:
            issues.append({
                "type": "INEFFICIENT_LOOP",
                "severity": "MEDIUM",
                "message": "List comprehension may be faster than loop + append"
            })
            recommendations.append("Use list comprehension instead of loop + append")

        if ".get(" in code and "for " in code:
            issues.append({
                "type": "N_PLUS_1",
                "severity": "HIGH",
                "message": "Potential N+1 query pattern detected"
            })
            recommendations.append("Consider batching database queries")

        if "time.sleep(" in code:
            issues.append({
                "type": "BLOCKING_CALL",
                "severity": "HIGH",
                "message": "Blocking sleep detected, consider async"
            })
            recommendations.append("Use asyncio.sleep() for async operations")

    return {
        "issues": issues,
        "recommendations": recommendations,
        "performance_score": 100 - (len(issues) * 15),
        "estimated_optimization": f"{len(issues) * 20}% faster"
    }


@tool("implement_caching")
def implement_caching(
    cache_type: str = "redis",
    ttl: int = 3600
) -> str:
    """
    Generate caching implementation

    Args:
        cache_type: Cache type (redis, memcached, in-memory)
        ttl: Time to live in seconds

    Returns:
        Caching code
    """
    if cache_type.lower() == "redis":
        return f"""import redis
from functools import wraps
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl={ttl}):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{{func.__name__}}:{{args}}:{{kwargs}}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )

            return result
        return wrapper
    return decorator

# Usage:
# @cache_result(ttl={ttl})
# def expensive_function():
#     # Your code here
#     pass
"""

    else:
        return f"# {cache_type} caching not yet implemented"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def get_tools_for_agent(agent_role: str) -> List:
    """
    Get specialized tools for an agent based on their role

    Args:
        agent_role: Agent's role name

    Returns:
        List of tools for that agent
    """
    tool_mapping = {
        "SecurityAgent": [
            security_scan,
            check_authentication,
            encrypt_data
        ],
        "DevOpsAgent": [
            generate_dockerfile,
            generate_kubernetes_manifest,
            setup_cicd_pipeline
        ],
        "DatabaseAgent": [
            generate_database_schema,
            optimize_query,
            generate_migration
        ],
        "FrontendAgent": [
            generate_react_component,
            generate_api_client
        ],
        "APIDesignAgent": [
            design_rest_api
        ],
        "PerformanceAgent": [
            analyze_performance,
            implement_caching
        ]
    }

    return tool_mapping.get(agent_role, [])


# Standalone usage example
if __name__ == "__main__":
    # Test security scan
    test_code = """
import os

def dangerous_function(user_input):
    eval(user_input)  # Dangerous!
    os.system(f"ls {user_input}")  # Command injection!
"""

    result = security_scan(test_code, "python")
    print("\n🔒 Security Scan Result:")
    print(f"Total Issues: {result['total_issues']}")
    for vuln in result['vulnerabilities']:
        print(f"  • [{vuln['severity']}] {vuln['message']}")

    # Test Dockerfile generation
    dockerfile = generate_dockerfile("python", "flask", ["redis", "celery"])
    print("\n🐳 Generated Dockerfile:")
    print(dockerfile)

    # Test API design
    api_design = design_rest_api(["User", "Product", "Order"], "JWT")
    print("\n🌐 API Design:")
    print(f"Base URL: {api_design['base_url']}")
    print(f"Resources: {len(api_design['endpoints'])}")
