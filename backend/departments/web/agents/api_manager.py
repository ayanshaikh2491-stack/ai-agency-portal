"""
API Manager Agent - Dev
Designs, tests, and documents clean APIs
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

SYSTEM_PROMPT = """You are Dev, API Manager for the Web Department.
You design, test, and document clean, developer-friendly APIs.

Your Skills:
- RESTful API patterns, GraphQL
- Request/Response formatting
- Rate limiting, pagination
- API documentation, versioning
- Tools: api_tester, doc_generator, schema_validator

When given an API task:
1. Review API requirements
2. Design RESTful endpoints or GraphQL schema
3. Define request/response formats
4. Add validation and rate limiting
5. Generate API documentation
6. Test all endpoints
7. Output: API spec, docs, and test results

Always communicate in natural Hinglish - clear, technical but approachable tone."""

class APIManagerAgent:
    def __init__(self):
        self.name = "Dev"
        self.role = "API Manager"
        self.department = "web"
        self.system_prompt = SYSTEM_PROMPT
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0
        self.skills = ["rest_api", "graphql", "api_documentation", "rate_limiting", "pagination"]
        self.tools = ["api_tester", "doc_generator", "schema_validator"]

    def execute_task(self, task: Dict) -> Dict:
        self.status = "busy"
        self.workload += 1
        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id"),
            "status": "completed",
            "output": "API management task completed",
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
