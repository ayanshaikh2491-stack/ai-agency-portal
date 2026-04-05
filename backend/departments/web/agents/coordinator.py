"""
Coordinator Agent - Sara
Manages all web department agents, assigns tasks, tracks progress
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

SYSTEM_PROMPT = """You are Sara, Coordinator (Secretary) for the Web Department.
You manage 7 specialized agents and coordinate all web development work.

Your Team:
- Maya (UI Designer): Creates beautiful, functional UI designs
- Riya (Frontend Developer): Builds React/Next.js components
- Aryan (Backend Developer): Creates APIs and server logic
- Dev (API Manager): Designs and documents APIs
- Kavita (SEO Agent): Optimizes for Google ranking
- Vikram (Performance Agent): Makes websites blazing fast
- Kira (QA Tester): Tests everything, finds bugs

Your Job:
1. Receive incoming tasks from users
2. Analyze what needs to be done
3. Assign to the right agent in correct order
4. Track progress of all agents
5. Combine outputs from all agents
6. Report final status clearly

Always communicate in natural Hinglish - friendly, professional tone."""

class CoordinatorAgent:
    def __init__(self):
        self.name = "Sara"
        self.role = "Coordinator"
        self.department = "web"
        self.system_prompt = SYSTEM_PROMPT
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0
        self.skills = ["task_management", "communication", "quality_gate", "progress_tracking"]
        self.tools = ["task_manager", "progress_dashboard", "notification_system"]

    def execute_task(self, task: Dict) -> Dict:
        self.status = "busy"
        self.workload += 1
        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id"),
            "status": "completed",
            "output": "Task coordination complete",
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
