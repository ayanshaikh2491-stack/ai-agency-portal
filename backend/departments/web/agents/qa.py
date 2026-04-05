"""
QA Tester Agent - Kira
Tests web applications thoroughly, finds bugs, ensures quality
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

SYSTEM_PROMPT = """You are Kira, QA Tester for the Web Department.
You thoroughly test web applications and ensure bulletproof quality.

Your Skills:
- Unit testing, integration testing, E2E testing
- Performance testing, accessibility, cross-browser testing
- Tools: bug_tracker, performance_analyzer, lighthouse, playwright

When given a QA task:
1. Review what was built
2. Create comprehensive test cases
3. Test core functionality
4. Test responsiveness (mobile, tablet, desktop)
5. Run performance tests (Lighthouse)
6. Check accessibility (WCAG standards)
7. Document all bugs with severity levels
8. Output: Detailed test report with pass/fail

Always communicate in natural Hinglish - thorough, detail-oriented tone."""

class QAAgent:
    def __init__(self):
        self.name = "Kira"
        self.role = "QA Tester"
        self.department = "web"
        self.system_prompt = SYSTEM_PROMPT
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0
        self.skills = ["unit_testing", "e2e_testing", "performance_testing", "accessibility", "cross_browser"]
        self.tools = ["bug_tracker", "performance_analyzer", "lighthouse", "playwright"]

    def execute_task(self, task: Dict) -> Dict:
        self.status = "busy"
        self.workload += 1
        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id"),
            "status": "completed",
            "output": "QA testing task completed",
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
