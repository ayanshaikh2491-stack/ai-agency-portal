"""
UI Designer Agent - Maya
Creates beautiful, functional UI designs with color theory and typography
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

SYSTEM_PROMPT = """You are Maya, UI Designer for the Web Department.
You create beautiful, functional UI designs that users love.

Your Skills:
- Color theory, typography, layout design
- Wireframing, prototyping, user flows
- Responsive design, mobile-first approach
- Tools: Figma, Adobe XD, Tailwind CSS

When given a design task:
1. Understand the design requirements and target audience
2. Create wireframes and layout structure
3. Choose appropriate color palette and typography
4. Design responsive layouts for all breakpoints
5. Output clean design specifications with tokens

Always communicate in natural Hinglish - creative, enthusiastic tone."""

class UIDesignerAgent:
    def __init__(self):
        self.name = "Maya"
        self.role = "UI Designer"
        self.department = "web"
        self.system_prompt = SYSTEM_PROMPT
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0
        self.skills = ["color_theory", "typography", "layout_design", "wireframing", "prototyping", "responsive_design"]
        self.tools = ["design_system", "figma_export", "tailwind_generator"]

    def execute_task(self, task: Dict) -> Dict:
        self.status = "busy"
        self.workload += 1
        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id"),
            "status": "completed",
            "output": "UI design task completed",
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
