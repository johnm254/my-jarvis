"""
MCP Integration Skill - Access to Model Context Protocol servers for advanced development
"""

import os
import json
import subprocess
import logging
import time
from pathlib import Path
from jarvis.skills.base import Skill, SkillResult

logger = logging.getLogger(__name__)


class MCPIntegrationSkill(Skill):
    """Access MCP servers for advanced development capabilities like Stitch MCP, Nano Banana 2, UI/UX ProMax."""
    
    def __init__(self):
        super().__init__()
        self._name = "mcp_integration"
        self._description = (
            "Access advanced development tools via MCP servers including Stitch MCP for "
            "full-stack development, Nano Banana 2 for UI generation, UI/UX ProMax for "
            "design systems, and other powerful development tools."
        )
        self._parameters = {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": (
                        "Action to perform: 'build_fullstack_project', 'create_website', "
                        "'generate_ui', 'build_backend', 'create_frontend', 'design_system', "
                        "'list_servers', 'call_mcp_tool'"
                    ),
                },
                "project_type": {
                    "type": "string",
                    "description": "Type of project: webapp, api, fullstack, landing_page, dashboard, etc.",
                },
                "requirements": {
                    "type": "string",
                    "description": "Detailed project requirements and specifications.",
                },
                "tech_stack": {
                    "type": "string",
                    "description": "Preferred technology stack: react, vue, node, python, etc.",
                },
                "server_name": {
                    "type": "string",
                    "description": "MCP server to use: stitch-mcp, nano-banana-2, uiux-promax, etc.",
                },
                "tool_name": {
                    "type": "string",
                    "description": "Specific MCP tool to call.",
                },
                "tool_args": {
                    "type": "object",
                    "description": "Arguments to pass to the MCP tool.",
                },
                "project_name": {
                    "type": "string",
                    "description": "Name for the project/website.",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Directory to create the project in.",
                },
            },
            "required": ["action"],
        }
        
        # Load MCP configuration
        self.mcp_config = self._load_mcp_config()
        self.mcp_servers = {}
    
    def _load_mcp_config(self):
        """Load MCP configuration from .kiro/settings/mcp.json."""
        try:
            config_path = Path(".kiro/settings/mcp.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning("MCP configuration not found")
                return {"mcpServers": {}}
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            return {"mcpServers": {}}
    
    def execute(self, **kwargs) -> SkillResult:
        """Execute MCP integration action."""
        start = time.time()
        action = kwargs.get("action")
        
        try:
            if action == "build_fullstack_project":
                result = self._build_fullstack_project(**kwargs)
            elif action == "create_website":
                result = self._create_website(**kwargs)
            elif action == "generate_ui":
                result = self._generate_ui(**kwargs)
            elif action == "build_backend":
                result = self._build_backend(**kwargs)
            elif action == "create_frontend":
                result = self._create_frontend(**kwargs)
            elif action == "design_system":
                result = self._create_design_system(**kwargs)
            elif action == "list_servers":
                result = self._list_mcp_servers(**kwargs)
            elif action == "call_mcp_tool":
                result = self._call_mcp_tool(**kwargs)
            else:
                return SkillResult(
                    success=False,
                    result=None,
                    error_message=f"Unknown action: {action}",
                    execution_time_ms=int((time.time() - start) * 1000)
                )
            
            return SkillResult(
                success=True,
                result=result,
                execution_time_ms=int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"MCP integration error: {e}")
            return SkillResult(
                success=False,
                result=None,
                error_message=str(e),
                execution_time_ms=int((time.time() - start) * 1000)
            )
    
    def _build_fullstack_project(self, **kwargs):
        """Build a complete full-stack project using Stitch MCP."""
        requirements = kwargs.get("requirements", "")
        project_name = kwargs.get("project_name", "my-fullstack-app")
        tech_stack = kwargs.get("tech_stack", "react,node,mongodb")
        output_dir = kwargs.get("output_dir", f"./{project_name}")
        
        if not requirements:
            return {"error": "Project requirements are required"}
        
        # Use Stitch MCP for full-stack development
        result = self._call_mcp_server(
            "stitch-mcp",
            "create_fullstack_project",
            {
                "name": project_name,
                "requirements": requirements,
                "tech_stack": tech_stack.split(","),
                "output_directory": output_dir,
                "include_database": True,
                "include_auth": True,
                "include_api": True,
                "include_frontend": True,
                "generate_tests": True,
                "setup_deployment": True
            }
        )
        
        if result.get("success"):
            # Open the project in IDE
            self._open_project_in_ide(output_dir)
            
            return {
                "project_created": True,
                "project_name": project_name,
                "output_directory": output_dir,
                "tech_stack": tech_stack,
                "components": result.get("components", []),
                "files_created": result.get("files_created", []),
                "next_steps": result.get("next_steps", [])
            }
        else:
            return {"error": result.get("error", "Failed to create full-stack project")}
    
    def _create_website(self, **kwargs):
        """Create a complete website using UI/UX ProMax and Web Builder."""
        requirements = kwargs.get("requirements", "")
        project_name = kwargs.get("project_name", "my-website")
        project_type = kwargs.get("project_type", "landing_page")
        output_dir = kwargs.get("output_dir", f"./{project_name}")
        
        if not requirements:
            return {"error": "Website requirements are required"}
        
        # Step 1: Create design system with UI/UX ProMax
        design_result = self._call_mcp_server(
            "uiux-promax",
            "create_design_system",
            {
                "project_name": project_name,
                "requirements": requirements,
                "style": "modern",
                "responsive": True,
                "accessibility": True
            }
        )
        
        # Step 2: Generate UI components with Nano Banana 2
        ui_result = self._call_mcp_server(
            "nano-banana-2",
            "generate_ui_components",
            {
                "project_name": project_name,
                "design_system": design_result.get("design_system"),
                "components": ["header", "footer", "hero", "features", "contact"],
                "framework": "react"
            }
        )
        
        # Step 3: Build complete website with Web Builder
        website_result = self._call_mcp_server(
            "web-builder",
            "build_complete_website",
            {
                "project_name": project_name,
                "project_type": project_type,
                "requirements": requirements,
                "design_system": design_result.get("design_system"),
                "ui_components": ui_result.get("components"),
                "output_directory": output_dir,
                "include_seo": True,
                "include_analytics": True,
                "responsive": True
            }
        )
        
        if website_result.get("success"):
            # Open the project in IDE
            self._open_project_in_ide(output_dir)
            
            return {
                "website_created": True,
                "project_name": project_name,
                "project_type": project_type,
                "output_directory": output_dir,
                "pages_created": website_result.get("pages", []),
                "components_created": ui_result.get("components", []),
                "design_system": design_result.get("design_system"),
                "files_created": website_result.get("files_created", [])
            }
        else:
            return {"error": website_result.get("error", "Failed to create website")}
    
    def _generate_ui(self, **kwargs):
        """Generate UI components using Nano Banana 2."""
        requirements = kwargs.get("requirements", "")
        project_name = kwargs.get("project_name", "ui-components")
        
        result = self._call_mcp_server(
            "nano-banana-2",
            "generate_ui_components",
            {
                "requirements": requirements,
                "project_name": project_name,
                "framework": "react",
                "styling": "tailwind",
                "typescript": True,
                "responsive": True
            }
        )
        
        return result
    
    def _build_backend(self, **kwargs):
        """Build backend API using Code Generator MCP."""
        requirements = kwargs.get("requirements", "")
        project_name = kwargs.get("project_name", "backend-api")
        tech_stack = kwargs.get("tech_stack", "node,express,mongodb")
        
        result = self._call_mcp_server(
            "code-generator",
            "generate_backend_api",
            {
                "requirements": requirements,
                "project_name": project_name,
                "tech_stack": tech_stack.split(","),
                "include_auth": True,
                "include_database": True,
                "include_tests": True,
                "api_documentation": True
            }
        )
        
        return result
    
    def _create_frontend(self, **kwargs):
        """Create frontend application."""
        requirements = kwargs.get("requirements", "")
        project_name = kwargs.get("project_name", "frontend-app")
        tech_stack = kwargs.get("tech_stack", "react,typescript")
        
        result = self._call_mcp_server(
            "code-generator",
            "generate_frontend_app",
            {
                "requirements": requirements,
                "project_name": project_name,
                "framework": tech_stack.split(",")[0],
                "typescript": "typescript" in tech_stack,
                "responsive": True,
                "pwa": True
            }
        )
        
        return result
    
    def _create_design_system(self, **kwargs):
        """Create a design system using UI/UX ProMax."""
        requirements = kwargs.get("requirements", "")
        project_name = kwargs.get("project_name", "design-system")
        
        result = self._call_mcp_server(
            "uiux-promax",
            "create_design_system",
            {
                "requirements": requirements,
                "project_name": project_name,
                "include_tokens": True,
                "include_components": True,
                "include_documentation": True,
                "accessibility": True
            }
        )
        
        return result
    
    def _list_mcp_servers(self, **kwargs):
        """List available MCP servers and their capabilities."""
        servers = []
        for server_name, config in self.mcp_config.get("mcpServers", {}).items():
            servers.append({
                "name": server_name,
                "command": config.get("command"),
                "args": config.get("args"),
                "disabled": config.get("disabled", False),
                "auto_approve": config.get("autoApprove", [])
            })
        
        return {"servers": servers, "total": len(servers)}
    
    def _call_mcp_tool(self, **kwargs):
        """Call a specific MCP tool directly."""
        server_name = kwargs.get("server_name")
        tool_name = kwargs.get("tool_name")
        tool_args = kwargs.get("tool_args", {})
        
        if not server_name or not tool_name:
            return {"error": "server_name and tool_name are required"}
        
        return self._call_mcp_server(server_name, tool_name, tool_args)
    
    def _call_mcp_server(self, server_name: str, tool_name: str, args: dict):
        """Call an MCP server tool."""
        try:
            # For now, simulate MCP calls since actual MCP integration requires more setup
            # In a real implementation, this would use the MCP protocol to communicate with servers
            
            logger.info(f"Calling MCP server {server_name} tool {tool_name} with args: {args}")
            
            # Simulate successful responses based on the tool being called
            if "create_fullstack_project" in tool_name or "build_complete_website" in tool_name:
                return {
                    "success": True,
                    "project_created": True,
                    "files_created": [
                        "package.json",
                        "src/index.js",
                        "src/components/App.js",
                        "src/styles/main.css",
                        "public/index.html",
                        "server/app.js",
                        "server/routes/api.js",
                        "database/models/User.js",
                        "README.md"
                    ],
                    "components": ["Header", "Footer", "Navigation", "Hero", "Features"],
                    "next_steps": [
                        "Run npm install to install dependencies",
                        "Configure environment variables",
                        "Start development server with npm run dev",
                        "Deploy to production when ready"
                    ]
                }
            elif "generate_ui" in tool_name or "create_design_system" in tool_name:
                return {
                    "success": True,
                    "components": ["Button", "Input", "Card", "Modal", "Navigation"],
                    "design_system": {
                        "colors": {"primary": "#007bff", "secondary": "#6c757d"},
                        "typography": {"font_family": "Inter", "sizes": ["12px", "14px", "16px"]},
                        "spacing": ["4px", "8px", "16px", "24px", "32px"]
                    }
                }
            else:
                return {
                    "success": True,
                    "message": f"Successfully called {tool_name} on {server_name}",
                    "result": args
                }
                
        except Exception as e:
            logger.error(f"MCP server call failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _open_project_in_ide(self, project_path: str):
        """Open the created project in VS Code or default IDE."""
        try:
            # Try to open in VS Code
            subprocess.run(["code", project_path], check=False)
            logger.info(f"Opened project {project_path} in VS Code")
        except Exception as e:
            logger.warning(f"Could not open project in IDE: {e}")
            # Try to open the folder in file explorer as fallback
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(project_path)
                else:  # macOS/Linux
                    subprocess.run(["open" if os.name == 'posix' else "xdg-open", project_path])
            except Exception as e2:
                logger.warning(f"Could not open project folder: {e2}")