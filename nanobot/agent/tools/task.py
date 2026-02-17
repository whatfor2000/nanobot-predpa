
from pathlib import Path
from typing import Optional

from nanobot.agent.task import TaskBoard

class TaskTool:
    """Tool for agents to manage shared tasks."""
    
    def __init__(self, task_board: TaskBoard):
        self.task_board = task_board
        self.name = "task"
        self.description = "Manage tasks for agent cooperation. Create, update, and list tasks."
        
    def get_definition(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "update", "list", "get"],
                            "description": "Action to perform: create a new task, update an existing task, list tasks, or get a specific task."
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Task ID (required for update and get actions)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Task title (required for create)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description (required for create, optional for update)"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Agent role to assign the task to (e.g., 'engineer', 'researcher')"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["todo", "in_progress", "review", "done"],
                            "description": "Task status (optional for update)"
                        },
                        "filter_status": {
                            "type": "string",
                            "enum": ["todo", "in_progress", "review", "done"],
                            "description": "Filter tasks by status (for list action)"
                        },
                        "filter_assignee": {
                            "type": "string",
                            "description": "Filter tasks by assignee (for list action)"
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    async def execute(self, **kwargs) -> str:
        action = kwargs.get("action")
        
        if action == "create":
            title = kwargs.get("title")
            description = kwargs.get("description")
            assignee = kwargs.get("assignee")
            
            if not title or not description:
                return "Error: 'title' and 'description' are required for create action."
            
            task = self.task_board.create_task(title, description, assignee)
            return f"Task created: {task.id} - {task.title} (assigned to: {task.assignee or 'unassigned'})"
        
        elif action == "update":
            task_id = kwargs.get("task_id")
            if not task_id:
                return "Error: 'task_id' is required for update action."
            
            status = kwargs.get("status")
            assignee = kwargs.get("assignee")
            description = kwargs.get("description")
            
            task = self.task_board.update_task(task_id, status, assignee, description)
            if not task:
                return f"Error: Task {task_id} not found."
            
            return f"Task updated: {task.id} - {task.title} (status: {task.status}, assignee: {task.assignee or 'unassigned'})"
        
        elif action == "list":
            filter_status = kwargs.get("filter_status")
            filter_assignee = kwargs.get("filter_assignee")
            
            tasks = self.task_board.list_tasks(filter_status, filter_assignee)
            
            if not tasks:
                return "No tasks found."
            
            result = []
            for task in tasks:
                result.append(f"- [{task.status}] {task.id}: {task.title} (assignee: {task.assignee or 'unassigned'})")
            
            return "\n".join(result)
        
        elif action == "get":
            task_id = kwargs.get("task_id")
            if not task_id:
                return "Error: 'task_id' is required for get action."
            
            task = self.task_board.get_task(task_id)
            if not task:
                return f"Error: Task {task_id} not found."
            
            return f"""Task: {task.id}
Title: {task.title}
Description: {task.description}
Status: {task.status}
Assignee: {task.assignee or 'unassigned'}
Created: {task.created_at}
Updated: {task.updated_at}"""
        
        else:
            return f"Error: Unknown action '{action}'"
