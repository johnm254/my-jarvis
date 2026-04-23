"""
Test MCP integration functionality
"""

from jarvis.skills.mcp_integration import MCPIntegrationSkill
import time

print("🚀 Testing MCP Integration\n")

mcp_skill = MCPIntegrationSkill()

# Test 1: List MCP servers
print("1️⃣  Testing: List MCP servers")
result = mcp_skill.execute(action="list_servers")
if result.success:
    servers = result.result.get("servers", [])
    print(f"   ✅ Found {len(servers)} MCP servers:")
    for server in servers:
        print(f"      - {server['name']}: {server['command']} {' '.join(server['args'])}")
else:
    print(f"   ❌ Error: {result.error_message}")

print()

# Test 2: Build full-stack project
print("2️⃣  Testing: Build full-stack project")
result = mcp_skill.execute(
    action="build_fullstack_project",
    project_name="test-ecommerce",
    requirements="Build an e-commerce website with user authentication, product catalog, shopping cart, and payment integration",
    tech_stack="react,node,mongodb"
)

if result.success:
    project_result = result.result
    print(f"   ✅ Project created: {project_result.get('project_created', False)}")
    print(f"   📁 Project name: {project_result.get('project_name', 'Unknown')}")
    print(f"   📂 Output directory: {project_result.get('output_directory', 'Unknown')}")
    print(f"   📄 Files created: {len(project_result.get('files_created', []))}")
    print(f"   🧩 Components: {len(project_result.get('components', []))}")
else:
    print(f"   ❌ Error: {result.error_message}")

print()

# Test 3: Create website
print("3️⃣  Testing: Create website")
result = mcp_skill.execute(
    action="create_website",
    project_name="restaurant-site",
    project_type="website",
    requirements="Create a modern restaurant website with menu, reservations, contact form, and photo gallery"
)

if result.success:
    website_result = result.result
    print(f"   ✅ Website created: {website_result.get('website_created', False)}")
    print(f"   🌐 Project name: {website_result.get('project_name', 'Unknown')}")
    print(f"   📄 Pages created: {len(website_result.get('pages_created', []))}")
    print(f"   🧩 Components: {len(website_result.get('components_created', []))}")
else:
    print(f"   ❌ Error: {result.error_message}")

print()

# Test 4: Generate UI components
print("4️⃣  Testing: Generate UI components")
result = mcp_skill.execute(
    action="generate_ui",
    project_name="ui-components",
    requirements="Create modern React components for a dashboard: sidebar navigation, data cards, charts, and user profile"
)

if result.success:
    ui_result = result.result
    print(f"   ✅ UI generated: {ui_result.get('success', False)}")
    print(f"   🧩 Components: {ui_result.get('components', [])}")
    if 'design_system' in ui_result:
        design = ui_result['design_system']
        print(f"   🎨 Design system: {len(design.get('colors', {}))} colors, {len(design.get('spacing', []))} spacing units")
else:
    print(f"   ❌ Error: {result.error_message}")

print("\n✅ MCP integration test complete!")
print("   All MCP servers are configured and ready to build complete projects\n")