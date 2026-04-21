"""Skill 2 — Project Design & Architecture

Generates project architecture from JSON spec:
- Folder structure
- ERD (Entity Relationship Diagram)
- API contract (OpenAPI)
- Component diagram
- PLAN.md file
"""

import os
import json
import time
import logging
from typing import Any, Dict, Optional
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class ProjectArchitectSkill(Skill):
    """
    Project design & architecture generation skill.
    
    Takes a JSON spec and generates:
    - Folder structure
    - ERD (Mermaid format)
    - API contract (OpenAPI spec)
    - Component diagram (Mermaid)
    - PLAN.md blueprint file
    """
    
    def __init__(self):
        super().__init__()
        self._name = "project_architect"
        self._description = (
            "Generate project architecture from JSON spec. "
            "Creates folder structure, ERD, API contract (OpenAPI), "
            "component diagram (Mermaid), and PLAN.md file."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "spec_path": {
                    "type": "string",
                    "description": "Path to JSON spec file (from email_intake skill)"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for generated architecture (default: jarvis_output/architecture)"
                }
            },
            "required": ["spec_path"]
        }
        
        self._llm_api_key = os.getenv("LLM_API_KEY")
    
    def _load_spec(self, spec_path: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Load project spec from JSON file."""
        try:
            with open(spec_path, 'r') as f:
                spec = json.load(f)
            return True, spec, None
        except FileNotFoundError:
            return False, {}, f"Spec file not found: {spec_path}"
        except json.JSONDecodeError as e:
            return False, {}, f"Invalid JSON in spec file: {e}"
    
    def _generate_folder_structure(self, spec: Dict[str, Any]) -> str:
        """Generate folder structure based on stack."""
        stack = spec.get("stack", [])
        project_name = spec.get("project_name", "project")
        
        # Detect framework
        is_react = any("react" in s.lower() for s in stack)
        is_next = any("next" in s.lower() for s in stack)
        is_node = any("node" in s.lower() or "express" in s.lower() for s in stack)
        is_python = any("python" in s.lower() or "django" in s.lower() or "fast" in s.lower() for s in stack)
        
        if is_next:
            structure = f"""{project_name}/
├── app/
│   ├── api/
│   ├── components/
│   ├── layout.tsx
│   └── page.tsx
├── public/
├── lib/
├── types/
├── .env.local
├── package.json
└── tsconfig.json"""
        elif is_react:
            structure = f"""{project_name}/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── utils/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
└── vite.config.ts"""
        elif is_python:
            structure = f"""{project_name}/
├── app/
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── main.py
│   └── config.py
├── tests/
├── requirements.txt
└── .env"""
        elif is_node:
            structure = f"""{project_name}/
├── src/
│   ├── routes/
│   ├── controllers/
│   ├── models/
│   ├── middleware/
│   └── server.js
├── tests/
├── package.json
└── .env"""
        else:
            structure = f"""{project_name}/
├── src/
├── tests/
├── docs/
└── README.md"""
        
        return structure
    
    def _generate_erd(self, spec: Dict[str, Any]) -> str:
        """Generate Entity Relationship Diagram in Mermaid format."""
        features = spec.get("features", [])
        
        # Basic ERD template
        erd = """erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    POST ||--o{ COMMENT : has
    
    USER {
        int id PK
        string email UK
        string name
        datetime created_at
    }
    
    POST {
        int id PK
        int user_id FK
        string title
        text content
        datetime created_at
    }
    
    COMMENT {
        int id PK
        int user_id FK
        int post_id FK
        text content
        datetime created_at
    }
"""
        return erd
    
    def _generate_api_contract(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OpenAPI specification."""
        project_name = spec.get("project_name", "API")
        
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{project_name} API",
                "version": "1.0.0",
                "description": f"API for {project_name}"
            },
            "servers": [
                {"url": "http://localhost:3000/api", "description": "Development"}
            ],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "List users",
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/User"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "summary": "Create user",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/UserCreate"}
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "Created"}
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "email": {"type": "string"},
                            "name": {"type": "string"},
                            "created_at": {"type": "string", "format": "date-time"}
                        }
                    },
                    "UserCreate": {
                        "type": "object",
                        "required": ["email", "name"],
                        "properties": {
                            "email": {"type": "string"},
                            "name": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        return openapi_spec
    
    def _generate_component_diagram(self, spec: Dict[str, Any]) -> str:
        """Generate component diagram in Mermaid format."""
        diagram = """graph TB
    Client[Client/Browser]
    API[API Server]
    Auth[Auth Service]
    DB[(Database)]
    Cache[(Redis Cache)]
    
    Client -->|HTTP/REST| API
    API --> Auth
    API --> DB
    API --> Cache
    Auth --> DB
"""
        return diagram
    
    def _generate_plan(self, spec: Dict[str, Any]) -> str:
        """Generate PLAN.md file."""
        project_name = spec.get("project_name", "Project")
        stack = spec.get("stack", [])
        features = spec.get("features", [])
        deadline = spec.get("deadline", "TBD")
        
        plan = f"""# {project_name} - Implementation Plan

## Project Overview
**Deadline:** {deadline}
**Stack:** {', '.join(stack)}

## Features
{chr(10).join(f'{i+1}. {feat}' for i, feat in enumerate(features))}

## Architecture

### Tech Stack
{chr(10).join(f'- {tech}' for tech in stack)}

### Folder Structure
See `folder_structure.txt`

### Database Schema
See `erd.mmd` (Mermaid ERD)

### API Design
See `openapi.json` (OpenAPI 3.0 spec)

### Component Architecture
See `components.mmd` (Mermaid diagram)

## Implementation Phases

### Phase 1: Setup & Scaffolding
- [ ] Initialize project with chosen framework
- [ ] Set up database and migrations
- [ ] Configure environment variables
- [ ] Set up linting and formatting

### Phase 2: Core Features
{chr(10).join(f'- [ ] {feat}' for feat in features)}

### Phase 3: Testing & QA
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Manual QA testing
- [ ] Fix bugs

### Phase 4: Deployment
- [ ] Set up CI/CD pipeline
- [ ] Deploy to staging
- [ ] Deploy to production
- [ ] Monitor and optimize

## Next Steps
1. Review this plan
2. Run code_generator skill to implement
3. Run tests and iterate
4. Deploy via github_automation skill
"""
        return plan
    
    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        
        # Validate parameters
        is_valid, error_msg = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(
                success=False,
                result=None,
                error_message=error_msg,
                execution_time_ms=int((time.time() - start) * 1000)
            )
        
        spec_path = kwargs.get("spec_path")
        output_dir = kwargs.get("output_dir", "jarvis_output/architecture")
        
        # Load spec
        success, spec, error = self._load_spec(spec_path)
        if not success:
            return SkillResult(
                success=False,
                result=None,
                error_message=error,
                execution_time_ms=int((time.time() - start) * 1000)
            )
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate all artifacts
        try:
            folder_structure = self._generate_folder_structure(spec)
            erd = self._generate_erd(spec)
            api_contract = self._generate_api_contract(spec)
            component_diagram = self._generate_component_diagram(spec)
            plan = self._generate_plan(spec)
            
            # Write files
            with open(os.path.join(output_dir, "folder_structure.txt"), 'w', encoding='utf-8') as f:
                f.write(folder_structure)
            
            with open(os.path.join(output_dir, "erd.mmd"), 'w', encoding='utf-8') as f:
                f.write(erd)
            
            with open(os.path.join(output_dir, "openapi.json"), 'w', encoding='utf-8') as f:
                json.dump(api_contract, f, indent=2)
            
            with open(os.path.join(output_dir, "components.mmd"), 'w', encoding='utf-8') as f:
                f.write(component_diagram)
            
            with open(os.path.join(output_dir, "PLAN.md"), 'w', encoding='utf-8') as f:
                f.write(plan)
            
            result = {
                "output_dir": os.path.abspath(output_dir),
                "files_created": [
                    "folder_structure.txt",
                    "erd.mmd",
                    "openapi.json",
                    "components.mmd",
                    "PLAN.md"
                ],
                "project_name": spec.get("project_name"),
                "stack": spec.get("stack")
            }
            
            return SkillResult(
                success=True,
                result=result,
                error_message=None,
                execution_time_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Error generating architecture: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
