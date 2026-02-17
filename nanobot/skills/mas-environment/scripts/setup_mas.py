
import os
import shutil
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_DIR / "assets" / "templates"
REPO_ROOT = SKILL_DIR.parents[2] # nanobot/skills/mas-environment -> nanobot/skills -> nanobot -> root
WORKSPACE_DIR = REPO_ROOT / "workspace"

ROLES = ["manager", "researcher", "engineer", "critic"]

def setup_environment():
    print(f"Setting up MAS environment in {WORKSPACE_DIR}...")
    
    if not WORKSPACE_DIR.exists():
        WORKSPACE_DIR.mkdir(parents=True)
        print(f"Created workspace directory: {WORKSPACE_DIR}")

    for role in ROLES:
        role_dir = WORKSPACE_DIR / role
        memory_dir = role_dir / "memory"
        
        # 1. Create Directories
        if not role_dir.exists():
            role_dir.mkdir(parents=True)
            print(f"Created directory: {role_dir}")
            
        if not memory_dir.exists():
            memory_dir.mkdir(parents=True)
            print(f"Created memory directory: {memory_dir}")

        # 2. Create MEMORY.md
        memory_file = memory_dir / "MEMORY.md"
        if not memory_file.exists():
            memory_file.write_text(f"# Long-term Memory for {role.capitalize()}\n\nStore important facts here.\n", encoding="utf-8")
            print(f"Created memory file: {memory_file}")
            
        # 3. Create AGENT.md from Template
        template_file = ASSETS_DIR / f"{role}.md"
        agent_file = role_dir / "AGENT.md"
        
        if template_file.exists():
            content = template_file.read_text(encoding="utf-8")
            agent_file.write_text(content, encoding="utf-8")
            print(f"Created/Updated AGENT.md for {role}")
        else:
            print(f"Warning: Template not found for {role} at {template_file}")

    print("\nMAS Environment Setup Complete!")

if __name__ == "__main__":
    setup_environment()
