"""Developer Tools Skill — full-stack developer automation."""

import os
import subprocess
import time
import json
import logging
from pathlib import Path
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class DevToolsSkill(Skill):
    """
    Full-stack developer automation:
    - Run dev servers (npm, python, docker)
    - Git operations (status, commit, push, pull, branch)
    - Package management (npm install, pip install)
    - Run tests
    - Open project in VS Code
    - Check port usage
    - Read/tail logs
    - Generate boilerplate (component, API route, model)
    - Docker operations
    """

    def __init__(self):
        super().__init__()
        self._name = "dev_tools"
        self._description = (
            "Full-stack developer automation. "
            "Run servers, git operations, install packages, run tests, "
            "open projects in VS Code, check ports, manage Docker, "
            "generate boilerplate code, and more."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "Action: 'git_status', 'git_commit', 'git_push', 'git_pull', "
                        "'git_branch', 'git_log', 'git_diff', "
                        "'npm_install', 'npm_run', 'npm_build', 'npm_test', "
                        "'pip_install', 'run_command', "
                        "'open_project', 'list_projects', "
                        "'check_port', 'kill_port', "
                        "'docker_ps', 'docker_up', 'docker_down', 'docker_logs', "
                        "'read_log', 'create_component', 'create_api_route', "
                        "'create_model', 'scaffold_project'"
                    ),
                },
                "target": {
                    "type": "string",
                    "description": "Project path, package name, port number, branch name, commit message, etc.",
                },
                "extra": {
                    "type": "string",
                    "description": "Additional parameter (e.g. script name for npm_run, file content, framework name).",
                },
            },
            "required": ["action"],
        }
        # Default project directory
        self._projects_dir = os.path.expanduser(
            os.getenv("PROJECTS_DIR", os.path.join(os.path.expanduser("~"), "projects"))
        )

    def _run(self, cmd: str, cwd: str = None, timeout: int = 30) -> dict:
        """Run a shell command and return output."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=cwd or os.getcwd(), timeout=timeout
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Command timed out", "returncode": -1, "success": False}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}

    def execute(self, **kwargs) -> SkillResult:
        start = time.time()
        action = kwargs.get("action", "")
        target = kwargs.get("target", "")
        extra = kwargs.get("extra", "")

        try:
            handler = getattr(self, f"_do_{action}", None)
            if handler is None:
                return SkillResult(success=False, result=None,
                                   error_message=f"Unknown action: {action}",
                                   execution_time_ms=int((time.time()-start)*1000))
            return handler(target=target, extra=extra, start=start)
        except Exception as e:
            return SkillResult(success=False, result=None, error_message=str(e),
                               execution_time_ms=int((time.time()-start)*1000))

    # ── Git ───────────────────────────────────────────────────────────────────

    def _do_git_status(self, target="", **_):
        cwd = target or os.getcwd()
        r = self._run("git status --short", cwd=cwd)
        return SkillResult(success=r["success"],
                           result=r["stdout"] or "Working tree clean",
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    def _do_git_commit(self, target="", extra="", **_):
        msg = target or extra or "Auto-commit by JARVIS"
        cwd = os.getcwd()
        self._run("git add -A", cwd=cwd)
        r = self._run(f'git commit -m "{msg}"', cwd=cwd)
        return SkillResult(success=r["success"],
                           result=r["stdout"] or r["stderr"],
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    def _do_git_push(self, target="", **_):
        cwd = os.getcwd()
        branch = target or ""
        cmd = f"git push origin {branch}" if branch else "git push"
        r = self._run(cmd, cwd=cwd, timeout=60)
        return SkillResult(success=r["success"],
                           result=r["stdout"] or "Pushed successfully",
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    def _do_git_pull(self, target="", **_):
        r = self._run("git pull", cwd=os.getcwd(), timeout=60)
        return SkillResult(success=r["success"],
                           result=r["stdout"] or "Already up to date",
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    def _do_git_branch(self, target="", **_):
        if target:
            r = self._run(f"git checkout -b {target}", cwd=os.getcwd())
        else:
            r = self._run("git branch -a", cwd=os.getcwd())
        return SkillResult(success=r["success"],
                           result=r["stdout"],
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    def _do_git_log(self, target="", **_):
        n = target or "10"
        r = self._run(f"git log --oneline -{n}", cwd=os.getcwd())
        return SkillResult(success=r["success"], result=r["stdout"], execution_time_ms=0)

    def _do_git_diff(self, target="", **_):
        r = self._run("git diff --stat", cwd=os.getcwd())
        return SkillResult(success=r["success"], result=r["stdout"] or "No changes",
                           execution_time_ms=0)

    # ── npm ───────────────────────────────────────────────────────────────────

    def _do_npm_install(self, target="", **_):
        pkg = target or ""
        cmd = f"npm install {pkg}" if pkg else "npm install"
        r = self._run(cmd, cwd=os.getcwd(), timeout=120)
        return SkillResult(success=r["success"],
                           result=f"Installed {pkg}" if pkg else "Dependencies installed",
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    def _do_npm_run(self, target="", extra="", **_):
        script = target or extra or "dev"
        # Start in background
        subprocess.Popen(f"npm run {script}", shell=True, cwd=os.getcwd())
        return SkillResult(success=True, result=f"Started: npm run {script}", execution_time_ms=0)

    def _do_npm_build(self, **_):
        r = self._run("npm run build", cwd=os.getcwd(), timeout=180)
        return SkillResult(success=r["success"],
                           result=r["stdout"][-500:] if r["stdout"] else "Build complete",
                           error_message=r["stderr"][-300:] if not r["success"] else None,
                           execution_time_ms=0)

    def _do_npm_test(self, **_):
        r = self._run("npm test -- --watchAll=false", cwd=os.getcwd(), timeout=120)
        return SkillResult(success=r["success"],
                           result=r["stdout"][-500:],
                           error_message=r["stderr"][-300:] if not r["success"] else None,
                           execution_time_ms=0)

    # ── pip ───────────────────────────────────────────────────────────────────

    def _do_pip_install(self, target="", **_):
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="Specify package name", execution_time_ms=0)
        r = self._run(f"pip install {target}", timeout=120)
        return SkillResult(success=r["success"],
                           result=f"Installed {target}",
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    # ── Generic command ───────────────────────────────────────────────────────

    def _do_run_command(self, target="", **_):
        if not target:
            return SkillResult(success=False, result=None,
                               error_message="No command provided", execution_time_ms=0)
        r = self._run(target, timeout=60)
        return SkillResult(success=r["success"],
                           result=r["stdout"] or r["stderr"],
                           error_message=r["stderr"] if not r["success"] else None,
                           execution_time_ms=0)

    # ── Projects ──────────────────────────────────────────────────────────────

    def _do_open_project(self, target="", **_):
        path = target
        if not os.path.isabs(path):
            path = os.path.join(self._projects_dir, target)
        if not os.path.exists(path):
            # Try current dir
            path = os.path.join(os.getcwd(), target)
        subprocess.Popen(f'code "{path}"', shell=True)
        return SkillResult(success=True, result=f"Opened in VS Code: {path}", execution_time_ms=0)

    def _do_list_projects(self, **_):
        dirs = []
        for d in [self._projects_dir, os.path.expanduser("~/Desktop"),
                  os.path.expanduser("~/Documents")]:
            if os.path.exists(d):
                for item in os.listdir(d):
                    full = os.path.join(d, item)
                    if os.path.isdir(full) and not item.startswith("."):
                        dirs.append(full)
        return SkillResult(success=True, result={"projects": dirs[:20]}, execution_time_ms=0)

    # ── Ports ─────────────────────────────────────────────────────────────────

    def _do_check_port(self, target="", **_):
        port = target or "3000"
        r = self._run(f"netstat -ano | findstr :{port}")
        return SkillResult(success=True,
                           result=r["stdout"] or f"Port {port} is free",
                           execution_time_ms=0)

    def _do_kill_port(self, target="", **_):
        port = target or "3000"
        # Find PID using the port
        r = self._run(f'for /f "tokens=5" %a in (\'netstat -aon ^| findstr :{port}\') do taskkill /F /PID %a')
        return SkillResult(success=True,
                           result=f"Killed process on port {port}",
                           execution_time_ms=0)

    # ── Docker ────────────────────────────────────────────────────────────────

    def _do_docker_ps(self, **_):
        r = self._run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
        return SkillResult(success=r["success"],
                           result=r["stdout"] or "No containers running",
                           execution_time_ms=0)

    def _do_docker_up(self, target="", **_):
        cmd = "docker-compose up -d"
        if target:
            cmd += f" {target}"
        subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
        return SkillResult(success=True, result=f"Starting Docker services...", execution_time_ms=0)

    def _do_docker_down(self, **_):
        r = self._run("docker-compose down", timeout=60)
        return SkillResult(success=r["success"], result="Docker services stopped", execution_time_ms=0)

    def _do_docker_logs(self, target="", **_):
        service = target or ""
        cmd = f"docker-compose logs --tail=50 {service}".strip()
        r = self._run(cmd, timeout=10)
        return SkillResult(success=r["success"], result=r["stdout"][-800:], execution_time_ms=0)

    # ── Logs ──────────────────────────────────────────────────────────────────

    def _do_read_log(self, target="", **_):
        log_file = target
        if not os.path.exists(log_file):
            # Search common locations
            for loc in ["logs/app.log", "logs/error.log", "app.log", "server.log"]:
                if os.path.exists(loc):
                    log_file = loc
                    break
        if not os.path.exists(log_file):
            return SkillResult(success=False, result=None,
                               error_message=f"Log file not found: {target}", execution_time_ms=0)
        r = self._run(f'powershell -c "Get-Content \'{log_file}\' -Tail 30"')
        return SkillResult(success=True, result=r["stdout"], execution_time_ms=0)

    # ── Boilerplate generators ────────────────────────────────────────────────

    def _do_create_component(self, target="", extra="", **_):
        """Generate a React component."""
        name = target or "MyComponent"
        framework = extra or "react"
        out_dir = os.path.join("jarvis_output", "components")
        os.makedirs(out_dir, exist_ok=True)
        filepath = os.path.join(out_dir, f"{name}.tsx")

        content = f"""import React from 'react';

interface {name}Props {{
  // Add your props here
}}

const {name}: React.FC<{name}Props> = (props) => {{
  return (
    <div className="{name.lower()}-container">
      <h1>{name}</h1>
    </div>
  );
}};

export default {name};
"""
        with open(filepath, "w") as f:
            f.write(content)
        subprocess.Popen(f'code "{os.path.abspath(filepath)}"', shell=True)
        return SkillResult(success=True,
                           result={"file": os.path.abspath(filepath), "component": name},
                           execution_time_ms=0)

    def _do_create_api_route(self, target="", extra="", **_):
        """Generate an API route (Express/FastAPI)."""
        name = target or "users"
        framework = extra or "express"
        out_dir = os.path.join("jarvis_output", "routes")
        os.makedirs(out_dir, exist_ok=True)

        if "fast" in framework.lower() or "python" in framework.lower():
            filepath = os.path.join(out_dir, f"{name}.py")
            content = f"""from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/{name}", tags=["{name}"])


class {name.capitalize()}Base(BaseModel):
    # Add your fields here
    name: str


class {name.capitalize()}Create({name.capitalize()}Base):
    pass


class {name.capitalize()}Response({name.capitalize()}Base):
    id: int

    class Config:
        from_attributes = True


@router.get("/", response_model=List[{name.capitalize()}Response])
async def get_{name}():
    return []


@router.get("/{{id}}", response_model={name.capitalize()}Response)
async def get_{name[:-1] if name.endswith('s') else name}(id: int):
    raise HTTPException(status_code=404, detail="Not found")


@router.post("/", response_model={name.capitalize()}Response)
async def create_{name[:-1] if name.endswith('s') else name}(data: {name.capitalize()}Create):
    pass


@router.put("/{{id}}", response_model={name.capitalize()}Response)
async def update_{name[:-1] if name.endswith('s') else name}(id: int, data: {name.capitalize()}Create):
    pass


@router.delete("/{{id}}")
async def delete_{name[:-1] if name.endswith('s') else name}(id: int):
    return {{"message": "Deleted"}}
"""
        else:
            filepath = os.path.join(out_dir, f"{name}.js")
            content = f"""const express = require('express');
const router = express.Router();

// GET all {name}
router.get('/', async (req, res) => {{
  try {{
    res.json([]);
  }} catch (err) {{
    res.status(500).json({{ error: err.message }});
  }}
}});

// GET single {name[:-1] if name.endswith('s') else name}
router.get('/:id', async (req, res) => {{
  try {{
    res.json({{}});
  }} catch (err) {{
    res.status(404).json({{ error: 'Not found' }});
  }}
}});

// POST create
router.post('/', async (req, res) => {{
  try {{
    res.status(201).json(req.body);
  }} catch (err) {{
    res.status(400).json({{ error: err.message }});
  }}
}});

// PUT update
router.put('/:id', async (req, res) => {{
  try {{
    res.json(req.body);
  }} catch (err) {{
    res.status(400).json({{ error: err.message }});
  }}
}});

// DELETE
router.delete('/:id', async (req, res) => {{
  try {{
    res.json({{ message: 'Deleted' }});
  }} catch (err) {{
    res.status(400).json({{ error: err.message }});
  }}
}});

module.exports = router;
"""
        with open(filepath, "w") as f:
            f.write(content)
        subprocess.Popen(f'code "{os.path.abspath(filepath)}"', shell=True)
        return SkillResult(success=True,
                           result={"file": os.path.abspath(filepath), "route": f"/{name}"},
                           execution_time_ms=0)

    def _do_create_model(self, target="", extra="", **_):
        """Generate a database model."""
        name = target or "User"
        framework = extra or "prisma"
        out_dir = os.path.join("jarvis_output", "models")
        os.makedirs(out_dir, exist_ok=True)

        if "prisma" in framework.lower():
            filepath = os.path.join(out_dir, f"{name.lower()}.prisma")
            content = f"""model {name} {{
  id        Int      @id @default(autoincrement())
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  // Add your fields here
  name      String
  email     String   @unique
}}
"""
        elif "mongo" in framework.lower() or "mongoose" in framework.lower():
            filepath = os.path.join(out_dir, f"{name.lower()}.model.js")
            content = f"""const mongoose = require('mongoose');

const {name}Schema = new mongoose.Schema({{
  name: {{ type: String, required: true }},
  email: {{ type: String, required: true, unique: true }},
  // Add your fields here
}}, {{ timestamps: true }});

module.exports = mongoose.model('{name}', {name}Schema);
"""
        else:
            filepath = os.path.join(out_dir, f"{name.lower()}.py")
            content = f"""from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class {name}(Base):
    __tablename__ = "{name.lower()}s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
"""
        with open(filepath, "w") as f:
            f.write(content)
        subprocess.Popen(f'code "{os.path.abspath(filepath)}"', shell=True)
        return SkillResult(success=True,
                           result={"file": os.path.abspath(filepath), "model": name},
                           execution_time_ms=0)

    def _do_scaffold_project(self, target="", extra="", **_):
        """Scaffold a new project."""
        name = target or "my-app"
        framework = extra or "nextjs"
        out_dir = os.path.join(os.getcwd(), "jarvis_output", "projects")
        os.makedirs(out_dir, exist_ok=True)

        cmd_map = {
            "nextjs": f"npx create-next-app@latest {name} --typescript --tailwind --app",
            "react": f"npx create-react-app {name} --template typescript",
            "vite": f"npm create vite@latest {name} -- --template react-ts",
            "express": f"npx express-generator {name}",
            "fastapi": None,  # handled below
            "django": f"django-admin startproject {name}",
        }

        if "fast" in framework.lower():
            project_dir = os.path.join(out_dir, name)
            os.makedirs(project_dir, exist_ok=True)
            # Create FastAPI boilerplate
            files = {
                "main.py": f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="{name}")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {{"message": "Welcome to {name}"}}
""",
                "requirements.txt": "fastapi\nuvicorn\npython-dotenv\nsqlalchemy\n",
                ".env": "DATABASE_URL=sqlite:///./app.db\nSECRET_KEY=change-me\n",
            }
            for fname, content in files.items():
                with open(os.path.join(project_dir, fname), "w") as f:
                    f.write(content)
            subprocess.Popen(f'code "{project_dir}"', shell=True)
            return SkillResult(success=True,
                               result={"project": project_dir, "framework": "FastAPI"},
                               execution_time_ms=0)

        cmd = cmd_map.get(framework.lower(), f"npx create-next-app@latest {name}")
        subprocess.Popen(f"start cmd /k {cmd}", shell=True, cwd=out_dir)
        return SkillResult(success=True,
                           result={"message": f"Scaffolding {framework} project '{name}'...",
                                   "directory": out_dir},
                           execution_time_ms=0)
