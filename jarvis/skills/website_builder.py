"""Website Builder Skill - generates complete websites from requirements."""

import os
import time
import logging
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.getcwd(), "jarvis_output", "websites")


class WebsiteBuilderSkill(Skill):
    """Build complete websites from natural language requirements."""

    def __init__(self):
        super().__init__()
        self._name = "build_website"
        self._description = (
            "Generate a complete website from requirements. Creates HTML, CSS, JavaScript files. "
            "Can build landing pages, portfolios, dashboards, e-commerce sites, blogs, etc."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "site_type": {
                    "type": "string",
                    "description": "Type of website: 'landing_page', 'portfolio', 'dashboard', 'ecommerce', 'blog', 'saas', 'custom'"
                },
                "name": {
                    "type": "string",
                    "description": "Name/title of the website"
                },
                "requirements": {
                    "type": "string",
                    "description": "Detailed requirements: sections, features, colors, style, content"
                },
                "framework": {
                    "type": "string",
                    "description": "Optional: 'vanilla', 'react', 'vue', 'tailwind'. Default: vanilla HTML/CSS/JS with Tailwind"
                },
            },
            "required": ["site_type", "name", "requirements"],
        }

    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        is_valid, err = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(success=False, result=None, error_message=err,
                               execution_time_ms=int((time.time() - start) * 1000))

        site_type = kwargs["site_type"]
        name = kwargs["name"]
        requirements = kwargs["requirements"]
        framework = kwargs.get("framework", "tailwind")

        safe_name = name.lower().replace(" ", "_").replace("/", "_")
        site_dir = os.path.join(OUTPUT_DIR, safe_name)
        os.makedirs(site_dir, exist_ok=True)

        # Auto-open the output folder in File Explorer
        import subprocess
        subprocess.Popen(f'explorer "{os.path.abspath(site_dir)}"', shell=True)

        result = {
            "site_type": site_type,
            "name": name,
            "requirements": requirements,
            "framework": framework,
            "output_dir": os.path.abspath(site_dir),
            "files_to_create": [
                os.path.join(os.path.abspath(site_dir), "index.html"),
                os.path.join(os.path.abspath(site_dir), "style.css"),
                os.path.join(os.path.abspath(site_dir), "script.js"),
            ],
        }

        elapsed = int((time.time() - start) * 1000)
        logger.info(f"Website '{name}' ({site_type}) prepared at: {site_dir}")
        return SkillResult(success=True, result=result, execution_time_ms=elapsed)
