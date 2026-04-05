"""
Backend Developer Agent - Aryan
Builds robust server-side logic with Python/FastAPI
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

SYSTEM_PROMPT = """You are Aryan, Backend Developer for the Web Department.
You build robust, scalable server-side applications.

Your Skills:
- Python, FastAPI, Node.js
- Database design (SQL, NoSQL)
- Authentication, authorization
- Server architecture, caching
- Tools: code_generator, file_writer, database_builder

When given a backend task:
1. Understand data and API requirements
2. Design database schema
3. Create API routes and handlers
4. Add authentication/authorization
5. Implement business logic
6. Output working FastAPI/Node.js backend code

Always communicate in natural Hinglish - professional, solution-oriented tone."""

class BackendAgent:
    def __init__(self):
        self.name = "Aryan"
        self.role = "Backend Developer"
        self.department = "web"
        self.system_prompt = SYSTEM_PROMPT
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0
        self.skills = ["python", "fastapi", "nodejs", "sql", "database_design", "authentication"]
        self.tools = ["code_generator", "file_writer", "database_builder"]

    def execute_task(self, task: Dict) -> Dict:
        self.status = "busy"
        self.workload += 1
        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id"),
            "status": "completed",
            "output": "Backend development task completed",
            "completed_at": datetime.utcnow().isoformat()
        }
        self.task_history.append(result)
        self.workload -= 1
        self.status = "active"
        return result

    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "status": self.status,
            "workload": self.workload,
            "tasks_completed": len(self.task_history),
            "skills": self.skills,
            "tools": self.tools,
            "system_prompt": self.system_prompt
        }
