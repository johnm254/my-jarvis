"""Project Planner Skill - creates plans, schemas, architecture docs."""

import os
import time
import json
import logging
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.getcwd(), "jarvis_output", "plans")


class ProjectPlannerSkill(Skill):
    """Create project plans, database schemas, API designs, and architecture docs."""

    def __init__(self):
        super().__init__()
        self._name = "create_plan"
        self._description = (
            "Create project plans, database schemas, API designs, system architecture, "
            "roadmaps, and technical specifications. Saves output as files."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Type of plan: 'project_plan', 'database_schema', 'api_design', 'architecture', 'roadmap', 'requirements'"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the project or system"
                },
                "description": {
                    "type": "string",
                    "description": "What the project/system does and any requirements"
                },
                "tech_stack": {
                    "type": "string",
                    "description": "Optional: preferred technologies (e.g., 'React, Node.js, PostgreSQL')"
                },
            },
            "required": ["type", "name", "description"],
        }

    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        is_valid, err = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(success=False, result=None, error_message=err,
                               execution_time_ms=int((time.time() - start) * 1000))

        plan_type = kwargs["type"]
        name = kwargs["name"]
        description = kwargs["description"]
        tech_stack = kwargs.get("tech_stack", "")

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # Determine output filename
        safe_name = name.lower().replace(" ", "_").replace("/", "_")
        ext_map = {
            "database_schema": ".sql",
            "api_design": ".md",
            "architecture": ".md",
            "project_plan": ".md",
            "roadmap": ".md",
            "requirements": ".md",
        }
        ext = ext_map.get(plan_type, ".md")
        filename = f"{safe_name}_{plan_type}{ext}"
        filepath = os.path.join(OUTPUT_DIR, filename)

        result = {
            "plan_type": plan_type,
            "name": name,
            "description": description,
            "tech_stack": tech_stack,
            "output_file": filepath,
            "output_dir": OUTPUT_DIR,
        }

        elapsed = int((time.time() - start) * 1000)
        logger.info(f"Plan '{plan_type}' for '{name}' prepared, output: {filepath}")
        return SkillResult(success=True, result=result, execution_time_ms=elapsed)
