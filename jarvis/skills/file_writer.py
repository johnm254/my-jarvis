"""File Writer Skill - saves content to disk."""

import os
import time
import logging
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class FileWriterSkill(Skill):
    """Write content to files on disk."""

    def __init__(self):
        super().__init__()
        self._name = "write_file"
        self._description = "Save content to a file on disk. Use after generating code, plans, or website files."
        self._parameters = {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Full path where the file should be saved"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                },
                "mode": {
                    "type": "string",
                    "description": "Write mode: 'write' (overwrite) or 'append'. Default: write"
                },
            },
            "required": ["filepath", "content"],
        }

    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        is_valid, err = self.validate_parameters(**kwargs)
        if not is_valid:
            return SkillResult(success=False, result=None, error_message=err,
                               execution_time_ms=int((time.time() - start) * 1000))

        filepath = kwargs["filepath"]
        content = kwargs["content"]
        mode = kwargs.get("mode", "write")

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

            write_mode = "a" if mode == "append" else "w"
            with open(filepath, write_mode, encoding="utf-8") as f:
                f.write(content)

            size = os.path.getsize(filepath)
            elapsed = int((time.time() - start) * 1000)
            logger.info(f"File written: {filepath} ({size} bytes)")

            # Auto-open in VS Code if available, else default app
            abs_path = os.path.abspath(filepath)
            try:
                import subprocess
                # Try VS Code first
                result = subprocess.run(
                    ["code", abs_path],
                    capture_output=True, timeout=3
                )
                if result.returncode != 0:
                    raise FileNotFoundError
                logger.info(f"Opened in VS Code: {abs_path}")
            except (FileNotFoundError, Exception):
                try:
                    import subprocess
                    subprocess.Popen(f'start "" "{abs_path}"', shell=True)
                except Exception:
                    pass

            return SkillResult(
                success=True,
                result={
                    "filepath": abs_path,
                    "size_bytes": size,
                    "lines": content.count("\n") + 1,
                    "message": f"File saved: {abs_path}",
                },
                execution_time_ms=elapsed,
            )
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            logger.error(f"Failed to write file {filepath}: {e}")
            return SkillResult(success=False, result=None,
                               error_message=f"Failed to write file: {e}",
                               execution_time_ms=elapsed)
