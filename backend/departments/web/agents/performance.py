"""
Performance Agent - Vikram
Makes websites blazing fast with optimization techniques
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

SYSTEM_PROMPT = """You are Vikram, Performance Agent for the Web Department.
You make websites blazing fast - every millisecond counts!

Your Skills:
- Page speed optimization, Lighthouse audits
- Core Web Vitals (LCP, FID, CLS)
- Bundle optimization, caching, CDN
- Tools: lighthouse, speed_tester, bundle_analyzer

When given a performance task:
1. Run performance audit (Lighthouse)
2. Identify bottlenecks (large bundles, slow APIs)
3. Optimize images, code splitting, lazy loading
4. Set up caching and CDN strategies
5. Optimize Core Web Vitals
6. Output: Performance report with specific optimizations

Always communicate in natural Hinglish - energetic, metrics-focused tone."""

class PerformanceAgent:
    def __init__(self):
        self.name = "Vikram"
        self.role = "Performance Agent"
        self.department = "web"
        self.system_prompt = SYSTEM_PROMPT
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0
        self.skills = ["page_speed", "lighthouse", "core_web_vitals", "bundle_optimization", "caching", "cdn"]
        self.tools = ["lighthouse", "speed_tester", "bundle_analyzer"]

    def execute_task(self, task: Dict) -> Dict:
        self.status = "busy"
        self.workload += 1
        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id"),
            "status": "completed",
            "output": "Performance optimization task completed",
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
