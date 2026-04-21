"""Skill 3 — Code Generation & Execution

Agentic code generation with iterative testing and auto-fixing.
Generates code file by file, runs tests, lints, and fixes errors until tests pass.
"""

import os
import json
import time
import subprocess
import logging
from typing import Any, Dict, Optional, List
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class CodeGeneratorSkill(Skill):
    """
    Code generation & execution skill with agentic loops.
    
    Features:
    - Generate code file by file from architecture plan
    - Run tests (Jest/Pytest)
    - Lint code (ESLint/Ruff)
    - Auto-fix errors
    - Iterate until tests pass
    """
    
    def __init__(self):
        super().__init__()
        self._name = "code_generator"
        self._description = (
            "Agentic code generation with iterative testing. "
            "Generates code, runs tests, lints, auto-fixes errors, "
            "and iterates until tests pass."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action: 'generate' to create code, 'test' to run tests, 'lint' to check code, 'fix' to auto-fix, 'iterate' for full loop",
                    "enum": ["generate", "test", "lint", "fix", "iterate"]
                },
                "plan_path": {
                    "type": "string",
                    "description": "Path to PLAN.md or architecture directory"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for generated code"
                },
                "max_iterations": {
                    "type": "integer",
                    "description": "Maximum iterations for auto-fix loop (default: 5)"
                }
            },
            "required": ["action"]
        }
        
        self._llm_api_key = os.getenv("LLM_API_KEY")
    
    def _run_command(self, cmd: str, cwd: str = None, timeout: int = 60) -> Dict[str, Any]:
        """Run shell command and return result."""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=cwd or os.getcwd(), timeout=timeout
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": "Timeout", "returncode": -1, "success": False}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "returncode": -1, "success": False}
    
    def _detect_stack(self, plan_path: str) -> Dict[str, Any]:
        """Detect tech stack from plan."""
        try:
            with open(plan_path, 'r') as f:
                content = f.read().lower()
            
            stack_info = {
                "language": "javascript",
                "framework": "react",
                "test_framework": "jest",
                "linter": "eslint"
            }
            
            if "python" in content or "django" in content or "fastapi" in content:
                stack_info["language"] = "python"
                stack_info["test_framework"] = "pytest"
                stack_info["linter"] = "ruff"
            
            if "typescript" in content:
                stack_info["language"] = "typescript"
            
            return stack_info
        except:
            return {
                "language": "javascript",
                "framework": "react",
                "test_framework": "jest",
                "linter": "eslint"
            }
    
    def _generate_code(self, plan_path: str, output_dir: str) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Generate code from plan using Claude."""
        if not self._llm_api_key:
            return False, {}, "LLM_API_KEY not configured"
        
        # Load plan
        try:
            with open(plan_path, 'r') as f:
                plan_content = f.read()
        except FileNotFoundError:
            return False, {}, f"Plan file not found: {plan_path}"
        
        # Detect stack
        stack = self._detect_stack(plan_path)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # TODO: Call Claude API to generate code file by file
        # For now, create a minimal scaffold
        
        files_created = []
        
        if stack["language"] == "python":
            # Python/FastAPI scaffold
            main_py = os.path.join(output_dir, "main.py")
            with open(main_py, 'w') as f:
                f.write("""from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}
""")
            files_created.append("main.py")
            
            # Test file
            test_py = os.path.join(output_dir, "test_main.py")
            with open(test_py, 'w') as f:
                f.write("""from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
""")
            files_created.append("test_main.py")
            
            # Requirements
            req_txt = os.path.join(output_dir, "requirements.txt")
            with open(req_txt, 'w') as f:
                f.write("fastapi\nuvicorn\npytest\nhttpx\n")
            files_created.append("requirements.txt")
        
        else:
            # JavaScript/TypeScript scaffold
            index_js = os.path.join(output_dir, "index.js")
            with open(index_js, 'w') as f:
                f.write("""const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ message: 'Hello World' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

module.exports = app;
""")
            files_created.append("index.js")
            
            # Test file
            test_js = os.path.join(output_dir, "index.test.js")
            with open(test_js, 'w') as f:
                f.write("""const request = require('supertest');
const app = require('./index');

describe('API Tests', () => {
  test('GET / returns hello world', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body.message).toBe('Hello World');
  });

  test('GET /health returns ok', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
  });
});
""")
            files_created.append("index.test.js")
            
            # Package.json
            pkg_json = os.path.join(output_dir, "package.json")
            with open(pkg_json, 'w') as f:
                json.dump({
                    "name": "generated-project",
                    "version": "1.0.0",
                    "scripts": {
                        "test": "jest",
                        "lint": "eslint ."
                    },
                    "dependencies": {
                        "express": "^4.18.0"
                    },
                    "devDependencies": {
                        "jest": "^29.0.0",
                        "supertest": "^6.3.0",
                        "eslint": "^8.0.0"
                    }
                }, f, indent=2)
            files_created.append("package.json")
        
        return True, {
            "files_created": files_created,
            "output_dir": os.path.abspath(output_dir),
            "stack": stack
        }, None
    
    def _run_tests(self, output_dir: str, stack: Dict[str, Any]) -> tuple[bool, str, Optional[str]]:
        """Run tests in the generated code."""
        if stack["language"] == "python":
            # Install dependencies first
            self._run_command("pip install -r requirements.txt", cwd=output_dir, timeout=120)
            # Run pytest
            result = self._run_command("pytest -v", cwd=output_dir)
        else:
            # Install dependencies
            self._run_command("npm install", cwd=output_dir, timeout=120)
            # Run jest
            result = self._run_command("npm test -- --passWithNoTests", cwd=output_dir)
        
        output = result["stdout"] + "\n" + result["stderr"]
        
        if result["success"]:
            return True, output, None
        else:
            return False, output, "Tests failed"
    
    def _run_lint(self, output_dir: str, stack: Dict[str, Any]) -> tuple[bool, str, Optional[str]]:
        """Run linter on generated code."""
        if stack["language"] == "python":
            result = self._run_command("ruff check .", cwd=output_dir)
        else:
            result = self._run_command("npx eslint .", cwd=output_dir)
        
        output = result["stdout"] + "\n" + result["stderr"]
        
        if result["success"]:
            return True, output, None
        else:
            return False, output, "Linting issues found"
    
    def _auto_fix(self, output_dir: str, stack: Dict[str, Any], errors: str) -> tuple[bool, str, Optional[str]]:
        """Auto-fix errors using Claude."""
        # TODO: Use Claude to analyze errors and fix code
        # For now, try auto-fix commands
        
        if stack["language"] == "python":
            result = self._run_command("ruff check --fix .", cwd=output_dir)
        else:
            result = self._run_command("npx eslint . --fix", cwd=output_dir)
        
        return result["success"], result["stdout"], None
    
    def _iterate(self, plan_path: str, output_dir: str, max_iterations: int) -> tuple[bool, Dict[str, Any], Optional[str]]:
        """Full iteration loop: generate -> test -> lint -> fix -> repeat."""
        # Generate initial code
        success, gen_result, error = self._generate_code(plan_path, output_dir)
        if not success:
            return False, {}, error
        
        stack = gen_result["stack"]
        iteration = 0
        test_passed = False
        
        while iteration < max_iterations and not test_passed:
            iteration += 1
            logger.info(f"Iteration {iteration}/{max_iterations}")
            
            # Run tests
            test_success, test_output, _ = self._run_tests(output_dir, stack)
            
            if test_success:
                test_passed = True
                break
            
            # Run lint
            lint_success, lint_output, _ = self._run_lint(output_dir, stack)
            
            # Auto-fix
            errors = test_output + "\n" + lint_output
            fix_success, fix_output, _ = self._auto_fix(output_dir, stack, errors)
            
            if not fix_success:
                logger.warning(f"Auto-fix failed on iteration {iteration}")
        
        return True, {
            "iterations": iteration,
            "test_passed": test_passed,
            "output_dir": os.path.abspath(output_dir),
            "files_created": gen_result["files_created"]
        }, None if test_passed else "Tests did not pass after max iterations"
    
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
        
        action = kwargs.get("action")
        plan_path = kwargs.get("plan_path", "jarvis_output/architecture/PLAN.md")
        output_dir = kwargs.get("output_dir", "jarvis_output/generated_code")
        max_iterations = kwargs.get("max_iterations", 5)
        
        if action == "generate":
            success, result, error = self._generate_code(plan_path, output_dir)
        elif action == "test":
            stack = self._detect_stack(plan_path)
            success, output, error = self._run_tests(output_dir, stack)
            result = {"test_output": output}
        elif action == "lint":
            stack = self._detect_stack(plan_path)
            success, output, error = self._run_lint(output_dir, stack)
            result = {"lint_output": output}
        elif action == "fix":
            stack = self._detect_stack(plan_path)
            success, output, error = self._auto_fix(output_dir, stack, "")
            result = {"fix_output": output}
        elif action == "iterate":
            success, result, error = self._iterate(plan_path, output_dir, max_iterations)
        else:
            return SkillResult(
                success=False,
                result=None,
                error_message=f"Unknown action: {action}",
                execution_time_ms=int((time.time() - start) * 1000)
            )
        
        return SkillResult(
            success=success,
            result=result,
            error_message=error,
            execution_time_ms=int((time.time() - start) * 1000)
        )
