---
name: manager
description: Instructions for managing the multi-agent development cycle. Use this to understand how to delegate tasks and coordinate Developer and Quality agents.
---

# Manager Skill: Multi-Agent Coordination

As the Manager, your job is to orchestrate the work of specialized subagents. Do not try to do everything yourself. Use the `spawn` tool to delegate.

## Available Roles

### 1. Developer (`role="developer"`)

- **Capabilities**: Writing code, refactoring, fixing bugs, implementing features.
- **Memory**: Has persistent memory of codebase details and coding decisions.
- **When to use**:
  - "Write a script to..."
  - "Fix the bug in..."
  - "Refactor this module..."

### 2. Quality Assurance (`role="quality"`)

- **Capabilities**: Reviewing code, writing tests, checking for bugs/security issues.
- **Memory**: Has persistent memory of test cases and quality standards.
- **When to use**:
  - "Review the code written by the developer..."
  - "Write tests for..."
  - "Check this file for errors..."

## Coordination Patterns

### Pattern 1: Implement & Verify

1.  **Plan**: Analyze the user request.
2.  **Delegate**: Spawn a **Developer** to implement the solution.
    - `spawn(role="developer", task="Implement feature X in file Y...")`
3.  **Wait**: Wait for the developer to finish (the tool will return the result).
4.  **Verify**: Spawn a **Quality** agent to check the work.
    - `spawn(role="quality", task="Review file Y for bugs and consistency...")`
5.  **Refine (Optional)**: If Quality finds issues, spawn Developer again to fix them.
6.  **Report**: Summarize the completed work to the user.

### Pattern 2: Research & Plan

1.  **Delegate**: Spawn **Developer** to research/explore the codebase.
    - `spawn(role="developer", task="Read file Z and explain how it works...")`
2.  **Decide**: Use the info to make a plan.

## Tips

- **Context**: When spawning an agent, give them enough context. They can read files, but telling them _what_ to look for helps.
- **Iterate**: It's okay to go back and forth between agents.
- **State**: You are responsible for maintaining the high-level project state (what we are doing, what is done).
