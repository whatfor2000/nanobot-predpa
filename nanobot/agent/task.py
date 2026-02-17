
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: str = "todo"  # todo, in_progress, review, done
    assignee: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class TaskBoard:
    def __init__(self, workspace: Path):
        self.file_path = workspace / "tasks.json"
        self._tasks: Dict[str, Task] = {}
        self._load()

    def _load(self):
        if not self.file_path.exists():
            return
        
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            for item in data:
                task = Task(**item)
                self._tasks[task.id] = task
        except Exception as e:
            print(f"Error loading tasks: {e}")

    def _save(self):
        data = [asdict(t) for t in self._tasks.values()]
        self.file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def create_task(self, title: str, description: str, assignee: Optional[str] = None) -> Task:
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            id=task_id,
            title=title,
            description=description,
            assignee=assignee
        )
        self._tasks[task_id] = task
        self._save()
        return task

    def update_task(self, task_id: str, status: Optional[str] = None, assignee: Optional[str] = None, description: Optional[str] = None) -> Optional[Task]:
        if task_id not in self._tasks:
            return None
        
        task = self._tasks[task_id]
        if status:
            task.status = status
        if assignee:
            task.assignee = assignee
        if description:
            task.description = description
            
        task.updated_at = datetime.now().isoformat()
        self._save()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self, status: Optional[str] = None, assignee: Optional[str] = None) -> List[Task]:
        tasks = list(self._tasks.values())
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        if assignee:
            tasks = [t for t in tasks if t.assignee == assignee]
            
        return tasks
