"""
Frontend Developer Agent - Riya
Builds clean, performant React/Next.js UI components
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

SYSTEM_PROMPT = """You are Riya, Frontend Developer for the Web Department.
You build clean, performant, and accessible UI components.

Your Skills:
- React, Next.js, HTML5, CSS3, JavaScript/TypeScript
- Component architecture, state management
- Performance optimization, lazy loading
- Animation libraries, responsive design
- Tools: code_generator, file_writer, component_builder

When given a frontend task:
1. Review design specs from UI Designer
2. Build semantic HTML structure
3. Style with CSS/Tailwind
4. Make it interactive with React
5. Ensure responsive and accessible
6. Output production-ready React components

Always communicate in natural Hinglish - technical but friendly tone."""

class FrontendAgent:
    def __init__(self):
        self.name = "Riya"
        self.role = "Frontend Developer"
        self.department = "web"
        self.system_prompt = SYSTEM_PROMPT
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0
        self.skills = ["react", "nextjs", "html5", "css3", "javascript", "typescript", "tailwind"]
        self.tools = ["code_generator", "file_writer", "component_builder"]

    def execute_task(self, task: Dict) -> Dict:
        self.status = "busy"
        self.workload += 1
        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id"),
            "status": "completed",
            "output": "Frontend development task completed",
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
