"""
YAGO v7.1 - Template API
Endpoints for project template management
"""

import yaml
import os
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])

# Template directory path
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


class TemplateInfo(BaseModel):
    """Template information model"""
    id: str
    name: str
    category: str
    difficulty: str
    icon: str
    tags: List[str]
    estimated_duration: str
    estimated_cost: float
    description: Optional[str] = None
    popular: bool = False
    file: Optional[str] = None


class TemplateDetail(BaseModel):
    """Detailed template model"""
    id: str
    name: str
    version: str
    category: str
    description: str
    icon: str
    tags: List[str]
    difficulty: str
    estimated_duration: str
    estimated_tokens: int
    estimated_cost: float
    tech_stack: Dict
    agents: List  # Accept both string and dict formats
    features: Optional[Union[Dict, List]] = None  # Accept both dict and list formats
    deployment: Optional[Union[Dict, List]] = None  # Accept both dict and list formats
    success_criteria: Optional[List[str]] = None
    metadata: Dict


class TemplateCategory(BaseModel):
    """Template category model"""
    id: str
    name: str
    description: str
    count: int


def load_template_index() -> Dict:
    """Load templates index file"""
    index_path = TEMPLATES_DIR / "templates_index.yaml"
    try:
        with open(index_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Templates index not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading templates index: {str(e)}")


def load_template_file(template_id: str) -> Dict:
    """Load individual template file"""
    # Find template file path from index
    index = load_template_index()
    template_info = next((t for t in index['templates'] if t['id'] == template_id), None)

    if not template_info:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    template_path = TEMPLATES_DIR / template_info['file']

    try:
        with open(template_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Template file not found: {template_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading template: {str(e)}")


@router.get("/", response_model=Dict)
async def list_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    popular_only: bool = False
):
    """
    Get list of all available templates

    Query params:
    - category: Filter by category (web, mobile, backend, etc.)
    - difficulty: Filter by difficulty (beginner, intermediate, advanced, expert)
    - popular_only: Show only popular templates
    """
    index = load_template_index()
    templates = index['templates']

    # Apply filters
    if category:
        templates = [t for t in templates if t['category'] == category]

    if difficulty:
        templates = [t for t in templates if t['difficulty'] == difficulty]

    if popular_only:
        templates = [t for t in templates if t.get('popular', False)]

    return {
        "total": len(templates),
        "templates": templates,
        "categories": index['categories'],
        "difficulty_levels": index['difficulty_levels']
    }


@router.get("/categories", response_model=List[TemplateCategory])
async def get_categories():
    """Get all template categories"""
    index = load_template_index()
    return index['categories']


@router.get("/popular", response_model=List[TemplateInfo])
async def get_popular_templates():
    """Get popular templates only"""
    index = load_template_index()
    popular = [t for t in index['templates'] if t.get('popular', False)]
    return popular


@router.get("/search", response_model=List[TemplateInfo])
async def search_templates(q: str):
    """
    Search templates by name, description, or tags

    Query params:
    - q: Search query string
    """
    index = load_template_index()
    templates = index['templates']

    q_lower = q.lower()

    # Search in name, tags, and description
    results = []
    for template in templates:
        # Load full template for description
        try:
            full_template = load_template_file(template['id'])
            description = full_template.get('description', '').lower()
        except:
            description = ''

        if (q_lower in template['name'].lower() or
            any(q_lower in tag.lower() for tag in template['tags']) or
            q_lower in description):
            results.append(template)

    return results


# Health check for templates system
@router.get("/health")
async def templates_health():
    """Health check for templates system"""
    try:
        index = load_template_index()
        return {
            "status": "healthy",
            "total_templates": index['total_templates'],
            "last_updated": index['last_updated'],
            "templates_dir": str(TEMPLATES_DIR),
            "templates_dir_exists": TEMPLATES_DIR.exists()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/{template_id}", response_model=TemplateDetail)
async def get_template(template_id: str):
    """Get detailed information about a specific template"""
    template_data = load_template_file(template_id)
    return template_data


@router.get("/{template_id}/preview", response_model=Dict)
async def preview_template(template_id: str):
    """Get template preview with key information"""
    template_data = load_template_file(template_id)

    # Return only key information for preview
    return {
        "id": template_data['id'],
        "name": template_data['name'],
        "description": template_data['description'],
        "icon": template_data['icon'],
        "difficulty": template_data['difficulty'],
        "estimated_duration": template_data['estimated_duration'],
        "estimated_cost": template_data['estimated_cost'],
        "tech_stack": template_data['tech_stack'],
        "features": list(template_data['features'].keys()) if isinstance(template_data['features'], dict) else template_data['features'],
        "tags": template_data['tags']
    }


@router.post("/{template_id}/apply")
async def apply_template(template_id: str, user_customizations: Optional[Dict] = None):
    """
    Apply a template to create a new project
    This will:
    1. Load template configuration
    2. Apply user customizations
    3. Generate customized clarification questions
    4. Return ready-to-use project configuration
    """
    template_data = load_template_file(template_id)

    # TODO: Apply user customizations
    # TODO: Generate customized questions based on template
    # TODO: Prepare project structure

    return {
        "status": "template_applied",
        "template_id": template_id,
        "template_name": template_data['name'],
        "message": f"Template '{template_data['name']}' applied successfully",
        "next_step": "clarification",
        "estimated_duration": template_data['estimated_duration'],
        "estimated_cost": template_data['estimated_cost']
    }
