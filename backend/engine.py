"""
AI Agency Engine - Core orchestrator for CEO -> Controller -> Department -> Agents flow
All real execution, no fake responses
"""
import os
import json
import uuid
import httpx
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

BACKEND_DIR = Path(__file__).parent

# ============================================================
# DATA STORE (JSON files)
# ============================================================
class DataStore:
    """JSON file-based data store for tasks, logs, and state"""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(BACKEND_DIR, "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def _path(self, name: str) -> str:
        return os.path.join(self.data_dir, f"{name}.json")

    def load(self, name: str, default: Any = None) -> Any:
        p = self._path(name)
        if os.path.exists(p):
            with open(p, "r") as f:
                return json.load(f)
        if default is not None:
            self.save(name, default)
            return default
        return {}

    def save(self, name: str, data: Any):
        with open(self._path(name), "w") as f:
            json.dump(data, f, indent=2, default=str)

    def append_log(self, name: str, entry: Dict):
        data = self.load(name, {"entries": []})
        if "entries" not in data:
            data["entries"] = []
        data["entries"].append(entry)
        if len(data["entries"]) > 500:
            data["entries"] = data["entries"][-500:]
        self.save(name, data)


# ============================================================
# SKILL SYSTEM
# ============================================================
class SkillManager:
    """Load and manage skills dynamically from markdown files"""

    def __init__(self, skills_dir: str = None):
        self.skills_dir = skills_dir or os.path.join(BACKEND_DIR, "skills")
        self.skills = {}
        self.skill_markdown = {}  # Raw markdown content
        self._load_skills()

    def _load_skills(self):
        os.makedirs(self.skills_dir, exist_ok=True)
        # Default skills (JSON fallback)
        default_skills = {
            "frontend_design": {"id": "frontend_design", "name": "Frontend Design Skill", "description": "Generate HTML/CSS/JS for web pages using Tailwind CSS", "type": "frontend", "trigger_keywords": ["ui", "frontend", "html", "css", "design", "website", "landing page"]},
            "backend_logic": {"id": "backend_logic", "name": "Backend Logic Skill", "description": "Design API endpoints, database models, and business logic", "type": "backend", "trigger_keywords": ["api", "backend", "database", "server", "auth", "endpoint"]},
            "debug_analyzer": {"id": "debug_analyzer", "name": "Debug Analyzer Skill", "description": "Analyze code, find bugs, suggest fixes", "type": "debug", "trigger_keywords": ["bug", "error", "fix", "debug", "broken", "not working"]},
            "seo_optimization": {"id": "seo_optimization", "name": "SEO Optimization Skill", "description": "Analyze and optimize for search engines", "type": "seo", "trigger_keywords": ["seo", "ranking", "google", "keyword", "optimize"]},
            "marketing_copy": {"id": "marketing_copy", "name": "Marketing Copy Skill", "description": "Write compelling marketing copy and CTAs", "type": "marketing", "trigger_keywords": ["marketing", "ad", "campaign", "copy", "social"]}
        }
        # Load markdown skills from skills/default/
        default_md_dir = os.path.join(self.skills_dir, "default")
        if os.path.exists(default_md_dir):
            for filename in os.listdir(default_md_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(default_md_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    parsed = self._parse_skill_md(content)
                    if parsed:
                        skill_id = parsed.get("name", filename.replace(".md", ""))
                        self.skills[skill_id] = parsed
                        self.skill_markdown[skill_id] = content
        # Load custom JSON skills
        skills_file = os.path.join(self.skills_dir, "custom_skills.json")
        if os.path.exists(skills_file):
            with open(skills_file, "r") as f:
                custom_skills = json.load(f)
                self.skills.update(custom_skills)
        # Add defaults for missing skills
        for skill_id, skill_data in default_skills.items():
            if skill_id not in self.skills:
                self.skills[skill_id] = skill_data

    def _parse_skill_md(self, content: str) -> Dict:
        """Parse a skill markdown file into a dictionary"""
        result = {}
        current_key = None
        current_value = []
        for line in content.split("\n"):
            if line.startswith("## "):
                if current_key and current_value:
                    val = "\n".join(current_value).strip()
                    # Try to parse JSON blocks
                    if val.startswith("{") and val.endswith("}"):
                        try: result[current_key] = json.loads(val)
                        except: result[current_key] = val
                    elif "\n- " in val or val.startswith("- "):
                        result[current_key] = [l.strip().lstrip("- ") for l in val.split("\n") if l.strip().startswith("- ")]
                    elif "\n" in val and current_key in ["steps"]:
                        result[current_key] = [l.strip().lstrip("0123456789. ") for l in val.split("\n") if l.strip()]
                    else:
                        result[current_key] = val
                current_key = line[3:].strip()
                current_value = []
            elif current_key:
                current_value.append(line)
        if current_key and current_value:
            val = "\n".join(current_value).strip()
            if val.startswith("{") and val.endswith("}"):
                try: result[current_key] = json.loads(val)
                except: result[current_key] = val
            else:
                result[current_key] = val
        return result if result else None

    def detect_skill(self, task_description: str) -> List[Dict]:
        """Detect which skills match a task description based on trigger keywords"""
        matched = []
        desc = task_description.lower()
        for skill_id, skill in self.skills.items():
            triggers = skill.get("trigger_keywords", [])
            if any(kw.lower() in desc for kw in triggers):
                matched.append({"id": skill_id, **skill})
        return matched

    def get_skill(self, skill_id: str) -> Optional[Dict]:
        return self.skills.get(skill_id)

    def get_skills_by_type(self, skill_type: str) -> List[Dict]:
        return [s for s in self.skills.values() if s.get("type") == skill_type]

    def get_all_skills(self) -> List[Dict]:
        return list(self.skills.values())

    def get_skill_prompt(self, skill_id: str) -> str:
        skill = self.skills.get(skill_id)
        if skill:
            return skill.get("prompt", "")
        return ""


# ============================================================
# AI CALL (Groq API)
# ============================================================
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODELS = ["llama-3.1-8b-instant", "llama3-8b-8192", "llama-3.3-70b-versatile"]

async def call_groq(
    messages: List[Dict],
    api_key: str = None,
    model: str = None,
    max_tokens: int = 2048,
    temperature: float = 0.7
) -> str:
    """Make real AI call via Groq API with fallback models"""
    key = api_key or os.getenv("GROQ_API_KEY", "")
    mdl = model or os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    if not key:
        return "[ERROR] GROQ_API_KEY not set in environment variables"
    for attempt in range(len(GROQ_MODELS)):
        current_model = mdl if attempt == 0 else GROQ_MODELS[attempt % len(GROQ_MODELS)]
        if current_model == mdl and attempt > 0:
            continue
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(GROQ_API_URL, json={
                    "model": current_model, "messages": messages,
                    "temperature": temperature, "max_tokens": max_tokens,
                }, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                elif r.status_code == 429:
                    continue
                else:
                    return f"[ERROR] API returned status {r.status_code}: {r.text[:200]}"
        except Exception as e:
            if attempt >= len(GROQ_MODELS) - 1:
                return f"[ERROR] Connection failed: {str(e)[:200]}"
    return "[ERROR] All models rate limited. Please wait 30 seconds."


# ============================================================
# AGENT DEFINITIONS
# ============================================================
AGENT_REGISTRY = {
    "web": {
        "planner": {"name": "Planner", "role": "Analyze tasks and create execution plans",
                    "skills": ["frontend_design", "backend_logic"],
                    "system_prompt": "You are the Planner Agent. Analyze tasks, break them into sub-tasks, create step-by-step execution plans, and assign to appropriate agents (frontend, backend, debug)."},
        "frontend": {"name": "Frontend Developer", "role": "Build UI components, HTML, CSS, JavaScript",
                     "skills": ["frontend_design", "debug_analyzer"],
                     "system_prompt": "You are the Frontend Developer Agent. Generate HTML structure, CSS (Tailwind CSS preferred), and JavaScript for interactivity. Always output complete, working code."},
        "backend": {"name": "Backend Developer", "role": "Build API endpoints, database models, business logic",
                    "skills": ["backend_logic", "debug_analyzer"],
                    "system_prompt": "You are the Backend Developer Agent. Design API endpoints (REST), create database models, write business logic, and add error handling."},
        "debug": {"name": "Debug Agent", "role": "Find and fix bugs, validate code",
                  "skills": ["debug_analyzer"],
                  "system_prompt": "You are the Debug Agent. Analyze code for bugs, check security vulnerabilities, find performance issues, and provide exact fixes with code."}
    },
    "seo": {
        "analyzer": {"name": "SEO Analyzer", "role": "Analyze websites for SEO",
                     "skills": ["seo_optimization"],
                     "system_prompt": "You are the SEO Analyzer Agent. Analyze content for meta tags, keyword optimization, site structure, schema markup, and page speed. Provide actionable recommendations."}
    },
    "marketing": {
        "copywriter": {"name": "Marketing Copywriter", "role": "Write marketing copy and CTAs",
                       "skills": ["marketing_copy"],
                       "system_prompt": "You are the Marketing Copywriter Agent. Write compelling copy for landing pages, email campaigns, social media posts, and ad copy."}
    }
}


# ============================================================
# TASK SYSTEM
# ============================================================
class TaskSystem:
    """Manage task lifecycle throughout the system"""
    def __init__(self, store: DataStore):
        self.store = store

    def create_task(self, task_type: str, department: str, description: str, project_id: str = None, source: str = "ceo") -> str:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = {"id": task_id, "type": task_type, "department": department, "description": description,
                "status": "pending", "source": source, "project_id": project_id, "assigned_agents": [],
                "outputs": [], "errors": [], "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(), "completed_at": None, "plan": None}
        tasks = self.store.load("tasks", {"tasks": []})
        if "tasks" not in tasks: tasks["tasks"] = []
        tasks["tasks"].append(task)
        self.store.save("tasks", tasks)
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict]:
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id: return t
        return None

    def update_task(self, task_id: str, **kwargs):
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                t.update(kwargs); t["updated_at"] = datetime.now().isoformat(); break
        self.store.save("tasks", tasks)

    def assign_agent(self, task_id: str, agent_key: str, department: str):
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                if "assigned_agents" not in t: t["assigned_agents"] = []
                t["assigned_agents"].append({"agent": agent_key, "department": department,
                    "assigned_at": datetime.now().isoformat(), "status": "assigned", "output": None})
                t["status"] = "assigned"; break
        self.store.save("tasks", tasks)

    def record_output(self, task_id: str, agent_key: str, output: str):
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                if "outputs" not in t: t["outputs"] = []
                t["outputs"].append({"agent": agent_key, "output": output, "timestamp": datetime.now().isoformat()})
                for agent in t.get("assigned_agents", []):
                    if agent["agent"] == agent_key: agent["status"] = "completed"; agent["output"] = output
                break
        self.store.save("tasks", tasks)

    def record_error(self, task_id: str, agent_key: str, error: str):
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                if "errors" not in t: t["errors"] = []
                t["errors"].append({"agent": agent_key, "error": error, "timestamp": datetime.now().isoformat()})
                for agent in t.get("assigned_agents", []):
                    if agent["agent"] == agent_key: agent["status"] = "error"
                break
        self.store.save("tasks", tasks)

    def get_active_tasks(self) -> List[Dict]:
        tasks = self.store.load("tasks", {"tasks": []})
        return [t for t in tasks.get("tasks", []) if t["status"] in ["pending", "assigned", "executing"]]

    def get_completed_tasks(self) -> List[Dict]:
        tasks = self.store.load("tasks", {"tasks": []})
        return [t for t in tasks.get("tasks", []) if t["status"] in ["completed", "error"]][-20:]


# ============================================================
# LOG SYSTEM
# ============================================================
class LogSystem:
    def __init__(self, store: DataStore):
        self.store = store
    def log(self, event: str, data: Dict = None, level: str = "info"):
        self.store.append_log("system", {"timestamp": datetime.now().isoformat(), "event": event, "level": level, "data": data or {}})
    def get_logs(self, limit: int = 50) -> List[Dict]:
        logs = self.store.load("system", {"entries": []})
        return logs.get("entries", [])[-limit:]
    def get_errors(self, limit: int = 20) -> List[Dict]:
        logs = self.store.load("system", {"entries": []})
        return [e for e in logs.get("entries", []) if e.get("level") == "error"][-limit:]


# ============================================================
# RECEPTION SYSTEM
# ============================================================
class ReceptionSystem:
    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager

    def receive_task(self, task: Dict, department: str) -> List[str]:
        agents_to_assign = []
        description = task.get("description", "").lower()
        if department == "web":
            agents_to_assign.append("planner")
            if any(w in description for w in ["ui", "frontend", "html", "css", "design", "page", "website", "landing"]):
                agents_to_assign.append("frontend")
            if any(w in description for w in ["api", "backend", "database", "server", "auth", "login", "endpoint"]):
                agents_to_assign.append("backend")
            agents_to_assign.append("debug")
        elif department == "seo":
            agents_to_assign.append("analyzer")
        elif department == "marketing":
            agents_to_assign.append("copywriter")
        return agents_to_assign

    def get_department_agents(self, department: str) -> List[Dict]:
        dept_agents = AGENT_REGISTRY.get(department, {})
        return [{"id": key, "name": info["name"], "role": info["role"],
                 "skills": [self.skill_manager.get_skill(s) for s in info.get("skills", []) if self.skill_manager.get_skill(s)],
                 "system_prompt": info["system_prompt"], "status": "idle", "department": department}
                for key, info in dept_agents.items()]


# ============================================================
# DEPARTMENT EXECUTOR
# ============================================================
class DepartmentExecutor:
    def __init__(self, department: str, skill_manager: SkillManager, task_system: TaskSystem, log_system: LogSystem):
        self.department = department
        self.skill_manager = skill_manager
        self.task_system = task_system
        self.log_system = log_system

    async def execute_task(self, task_id: str, agent_key: str) -> str:
        agents = AGENT_REGISTRY.get(self.department, {})
        agent_info = agents.get(agent_key)
        if not agent_info:
            error_msg = f"Agent '{agent_key}' not found in department '{self.department}'"
            self.log_system.log(error_msg, {"task_id": task_id}, "error")
            self.task_system.record_error(task_id, agent_key, error_msg)
            return error_msg
        task = self.task_system.get_task(task_id)
        if not task:
            return f"[ERROR] Task '{task_id}' not found"
        self.task_system.update_task(task_id, status="executing")
        self.log_system.log("agent_started", {"task_id": task_id, "agent": agent_key, "department": self.department})

        agent_skills = agent_info.get("skills", [])
        skill_context = ""
        for skill_id in agent_skills:
            sp = self.skill_manager.get_skill_prompt(skill_id)
            si = self.skill_manager.get_skill(skill_id)
            if sp and si: skill_context += f"\n--- {si['name']} ---\n{sp}"
        system_prompt = agent_info["system_prompt"]
        if skill_context: system_prompt += f"\n\n## ACTIVE SKILLS:\n{skill_context}"
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"TASK: {task['description']}\nID: {task['id']}\nType: {task['type']}\nDept: {self.department}\n\nExecute and provide complete output."}]
        for output in task.get("outputs", []):
            messages.append({"role": "assistant", "content": f"[{output['agent']}]: {output['output'][:500]}"})
            messages.append({"role": "user", "content": "Continue."})
        result = await call_groq(messages)
        if result.startswith("[ERROR]"):
            self.log_system.log("agent_error", {"task_id": task_id, "agent": agent_key, "error": result[:200]}, "error")
            self.task_system.record_error(task_id, agent_key, result)
            return result
        self.task_system.record_output(task_id, agent_key, result)
        self.log_system.log("agent_completed", {"task_id": task_id, "agent": agent_key, "output_length": len(result)})
        return result


# ============================================================
# MAIN ENGINE (CEO -> Controller -> Department -> Agents)
# ============================================================
class AgencyEngine:
    def __init__(self):
        self.store = DataStore()
        self.skill_manager = SkillManager()
        self.task_system = TaskSystem(self.store)
        self.log_system = LogSystem(self.store)
        self.reception = ReceptionSystem(self.skill_manager)
        self.dept_executors = {}
        for dept in AGENT_REGISTRY:
            self.dept_executors[dept] = DepartmentExecutor(dept, self.skill_manager, self.task_system, self.log_system)
        self.log_system.log("system_initialized", {"message": "AI Agency Engine initialized"})

    async def process_ceo_request(self, message: str, project_id: str = None) -> Dict:
        self.log_system.log("ceo_request", {"message": message[:100], "project_id": project_id})
        departments = self._detect_departments(message) or ["web"]
        task_ids = {}
        for dept in departments:
            task_type = self._determine_task_type(message, dept)
            task_id = self.task_system.create_task(task_type, dept, message, project_id, "ceo")
            task_ids[dept] = task_id
            for agent_key in self.reception.receive_task({"description": message, "type": task_type}, dept):
                self.task_system.assign_agent(task_id, agent_key, dept)
        results = {}
        for dept, task_id in task_ids.items():
            executor = self.dept_executors.get(dept)
            if not executor: continue
            task = self.task_system.get_task(task_id)
            for agent_entry in task.get("assigned_agents", []):
                agent_key = agent_entry["agent"]
                self.log_system.log("agent_executing", {"task_id": task_id, "agent": agent_key, "department": dept})
                output = await executor.execute_task(task_id, agent_key)
                results[f"{dept}.{agent_key}"] = {"status": "error" if output.startswith("[ERROR]") else "completed", "output": output[:4000]}
        for dept, task_id in task_ids.items():
            self.task_system.update_task(task_id, status="completed", completed_at=datetime.now().isoformat())
        response = self._build_response(task_ids, results, departments)
        self.log_system.log("request_completed", {"task_ids": task_ids, "departments": departments, "result_count": len(results)})
        return response

    def _detect_departments(self, message: str) -> List[str]:
        msg = message.lower()
        departments = []
        if any(w in msg for w in ["website", "web", "site", "frontend", "backend", "api", "app", "page", "landing", "html", "css", "database", "server"]): departments.append("web")
        if any(w in msg for w in ["seo", "ranking", "google", "search", "keyword", "traffic", "optimize"]): departments.append("seo")
        if any(w in msg for w in ["marketing", "ad", "campaign", "email", "copy", "social", "content", "post", "brand"]): departments.append("marketing")
        return departments

    def _determine_task_type(self, message: str, department: str) -> str:
        msg = message.lower()
        if any(w in msg for w in ["build", "create", "make", "develop", "design"]): return "build"
        if any(w in msg for w in ["fix", "debug", "repair", "error", "bug"]): return "fix"
        if any(w in msg for w in ["analyze", "audit", "review", "check"]): return "analyze"
        return "general"

    def _build_response(self, task_ids: Dict, results: Dict, departments: List[str]) -> Dict:
        successful = [k for k, v in results.items() if v["status"] == "completed"]
        failed = [k for k, v in results.items() if v["status"] == "error"]
        return {"status": "completed" if not failed else "partial", "departments_used": departments,
                "tasks": task_ids, "successful_agents": successful, "failed_agents": failed,
                "summary": f"Executed across {len(departments)} dept(s), {len(successful)} agent(s) succeeded, {len(failed)} failed."}

    def get_overview(self) -> Dict:
        tasks = self.store.load("tasks", {"tasks": []})
        task_list = tasks.get("tasks", [])
        return {"total_agents": sum(len(a) for a in AGENT_REGISTRY.values()),
                "active_tasks": len([t for t in task_list if t["status"] in ["pending", "assigned", "executing"]]),
                "completed_tasks": len([t for t in task_list if t["status"] == "completed"]),
                "error_tasks": len([t for t in task_list if t["status"] == "error"]),
                "departments": list(AGENT_REGISTRY.keys()),
                "skills_loaded": len(self.skill_manager.get_all_skills()), "status": "running"}

    def get_all_agents_info(self) -> List[Dict]:
        return [a for dept in AGENT_REGISTRY for a in self.reception.get_department_agents(dept)]

    def get_department_info(self) -> List[Dict]:
        return [{"name": dept, "agent_count": len(agents), "agents": self.reception.get_department_agents(dept),
                 "description": {"web": "Full web development with planning, frontend, backend, debugging",
                                 "seo": "SEO analysis and optimization", "marketing": "Marketing copy and campaigns"}.get(dept, "")}
                for dept, agents in AGENT_REGISTRY.items()]

    def get_task_details(self, task_id: str) -> Optional[Dict]: return self.task_system.get_task(task_id)
    def get_active_tasks(self) -> List[Dict]: return self.task_system.get_active_tasks()
    def get_completed_tasks(self) -> List[Dict]: return self.task_system.get_completed_tasks()
    def get_system_logs(self, limit: int = 50) -> List[Dict]: return self.log_system.get_logs(limit)
    def get_errors(self, limit: int = 20) -> List[Dict]: return self.log_system.get_errors(limit)
    def get_skills(self) -> List[Dict]: return self.skill_manager.get_all_skills()