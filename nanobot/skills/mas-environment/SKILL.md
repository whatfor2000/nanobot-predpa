---
name: mas-environment
description: Build and configure the Multi-Agent System (MAS) environment. Use this to initialize the workspace with the required directory structure, role-specific prompts, and memory files for the Manager, Researcher, Engineer, and Critic agents.
---

# MAS Environment Setup

This skill automates the creation of the Multi-Agent System environment.

## What it does

- Creates role-specific directories in `workspace/`:
  - `workspace/manager/`
  - `workspace/researcher/`
  - `workspace/engineer/`
  - `workspace/critic/`
- Creates persistent memory directories: `workspace/<role>/memory/`
- Initializes `MEMORY.md` for each agent.
- Deploys system prompts (`AGENT.md`) from templates.

## Usage

### 1. Initialize Environment

Run the setup script to build the environment:

```bash
python nanobot/skills/mas-environment/scripts/setup_mas.py
```

### 2. Verify Setup

After running the script, check the `workspace` directory. You should see folders for each agent role, containing an `AGENT.md` file and a `memory` folder.

## Customization

To modify the default prompts, edit the template files in:
`nanobot/skills/mas-environment/assets/templates/`

Then re-run the setup script to apply changes to the workspace.
