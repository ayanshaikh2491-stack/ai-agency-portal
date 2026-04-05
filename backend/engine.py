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
        # Keep last 500 entries
        if len(data["entries"]) > 500:
            data["entries"] = data["entries"][-500:]
        self.save(name, data)


# ============================================================
# SKILL SYSTEM
# ============================================================
class SkillManager:
    """Load and manage skills dynamically from skills/ directory"""

    def __init__(self, skills_dir: str = None):
        self.skills_dir = skills_dir or os.path.join(BACKEND_DIR, "skills")
        self.skills = {}
        self._load_skills()

    def _load_skills(self):
        """Load all skill files (JSON) from skills/ directory"""
        os.makedirs(self.skills_dir, exist_ok=True)

        # Create default skills if not exist
        default_skills = {
            "frontend_design": {
                "id": "frontend_design",
                "name": "Frontend Design Skill",
                "description": "Generate HTML/CSS/JS for web pages using Tailwind CSS",
                "type": "frontend",
                "prompt": "Generate complete HTML structure with Tailwind CSS classes. Make it responsive, modern, and clean."
            },
            "backend_logic": {
                "id": "backend_logic",
                "name": "Backend Logic Skill",
                "description": "Design API endpoints, database models, and business logic",
                "type": "backend",
                "prompt": "Design the backend API routes, database models, and business logic for this feature."
            },
            "debug_analyzer": {
                "id": "debug_analyzer",
                "name": "Debug Analyzer Skill",
                "description": "Analyze code, find bugs, suggest fixes",
                "type": "debug",
                "prompt": "Analyze the provided code. Find bugs, security issues, performance problems. Suggest exact fixes."
            },
            "seo_optimization": {
                "id": "seo_optimization",
                "name": "SEO Optimization Skill",
                "description": "Analyze and optimize for search engines",
                "type": "seo",
                "prompt": "Analyze the page content and suggest specific SEO improvements: meta tags, keywords, structure, schema."
            },
            "marketing_copy": {
                "id": "marketing_copy",
                "name": "Marketing Copy Skill",
                "description": "Write compelling marketing copy and CTAs",
                "type": "marketing",
                "prompt": "Write persuasive marketing copy with clear CTAs. Focus on benefits, not features."
            }
        }

        # Load custom skills from files
        skills_file = os.path.join(self.skills_dir, "custom_skills.json")
        if os.path.exists(skills_file):
            with open(skills_file, "r") as f:
                custom_skills = json.load(f)
                self.skills.update(custom_skills)

        # Add defaults for missing skills
        for skill_id, skill_data in default_skills.items():
            if skill_id not in self.skills:
                self.skills[skill_id] = skill_data

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

    # Try primary model first
    for attempt, current_model in enumerate([mdl] + [m for m in GROQ_MODELS if m != mdl]):
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    GROQ_API_URL,
                    json={
                        "model": current_model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    }
                )
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                elif r.status_code == 429:
                    # Rate limited - try next model
                    continue
                else:
                    return f"[ERROR] API returned status {r.status_code}: {r.text[:200]}"
        except Exception as e:
            if attempt < len(GROQ_MODELS):
                continue
            return f"[ERROR] Connection failed: {str(e)[:200]}"

    return "[ERROR] All models rate limited. Please wait 30 seconds and try again."


# ============================================================
# AGENT DEFINITIONS
# ============================================================
AGENT_REGISTRY = {
    "web": {
        "planner": {
            "name": "Planner",
            "role": "Analyze tasks and create execution plans",
            "skills": ["frontend_design", "backend_logic"],
            "system_prompt": """You are the Planner Agent for a Web Department.
Your job is to:
1. Analyze incoming tasks
2. Break them into sub-tasks
3. Create a step-by-step execution plan
4. Assign sub-tasks to appropriate agents (frontend, backend, debug)

Respond with a structured JSON plan:
{
  "analysis": "What the task requires",
  "subtasks": [
    {"agent": "frontend", "task": "what to build", "priority": 1},
    {"agent": "backend", "task": "what to build", "priority": 2}
  ],
  "estimated_time": "rough estimate"
}"""
        },
        "frontend": {
            "name": "Frontend Developer",
            "role": "Build UI components, HTML, CSS, JavaScript",
            "skills": ["frontend_design", "debug_analyzer"],
            "system_prompt": """You are the Frontend Developer Agent.
Your job is to:
1. Generate HTML structure
2. Generate CSS (Tailwind CSS preferred)
3. Generate JavaScript for interactivity
4. Ensure responsive design

Always output complete, working code. Use proper formatting."""
        },
        "backend": {
            "name": "Backend Developer",
            "role": "Build API endpoints, database models, business logic",
            "skills": ["backend_logic", "debug_analyzer"],
            "system_prompt": """You are the Backend Developer Agent.
Your job is to:
1. Design API endpoints (REST)
2. Create database models
3. Write business logic
4. Add error handling

Always output complete, production-ready code."""
        },
        "debug": {
            "name": "Debug Agent",
            "role": "Find and fix bugs, validate code",
            "skills": ["debug_analyzer"],
            "system_prompt": """You are the Debug Agent.
Your job is to:
1. Analyze code for bugs
2. Check security vulnerabilities
3. Find performance issues
4. Provide exact fixes with code

Be specific. Show before/after code."""
        }
    },
    "seo": {
        "analyzer": {
            "name": "SEO Analyzer",
            "role": "Analyze websites for SEO",
            "skills": ["seo_optimization"],
            "system_prompt": """You are the SEO Analyzer Agent.
Analyze content for:
1. Meta tags
2. Keyword optimization
3. Site structure
4. Schema markup
5. Page speed suggestions

Provide actionable recommendations."""
        }
    },
    "marketing": {
        "copywriter": {
            "name": "Marketing Copywriter",
            "role": "Write marketing copy and CTAs",
            "skills": ["marketing_copy"],
            "system_prompt": """You are the Marketing Copywriter Agent.
Write compelling copy for:
1. Landing pages
2. Email campaigns
3. Social media posts
4. Ad copy

Focus on benefits, create strong CTAs, use persuasive language."""
        }
    }
}


# ============================================================
# TASK SYSTEM
# ============================================================
class TaskSystem:
    """Manage task lifecycle throughout the system"""

    def __init__(self, store: DataStore):
        self.store = store

    def create_task(self, task_type: str, department: str, description: str,
                   project_id: str = None, source: str = "ceo") -> str:
        """Create a new structured task"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = {
            "id": task_id,
            "type": task_type,
            "department": department,
            "description": description,
            "status": "pending",  # pending -> assigned -> executing -> completed / error
            "source": source,
            "project_id": project_id,
            "assigned_agents": [],
            "outputs": [],
            "errors": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "plan": None,
        }
        tasks = self.store.load("tasks", {"tasks": []})
        if "tasks" not in tasks:
            tasks["tasks"] = []
        tasks["tasks"].append(task)
        self.store.save("tasks", tasks)
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict]:
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                return t
        return None

    def update_task(self, task_id: str, **kwargs):
        """Update task fields"""
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                t.update(kwargs)
                t["updated_at"] = datetime.now().isoformat()
                break
        self.store.save("tasks", tasks)

    def assign_agent(self, task_id: str, agent_key: str, department: str):
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                agent_entry = {
                    "agent": agent_key,
                    "department": department,
                    "assigned_at": datetime.now().isoformat(),
                    "status": "assigned",
                    "output": None,
                }
                if "assigned_agents" not in t:
                    t["assigned_agents"] = []
                t["assigned_agents"].append(agent_entry)
                t["status"] = "assigned"
                break
        self.store.save("tasks", tasks)

    def record_output(self, task_id: str, agent_key: str, output: str):
        """Record agent output for a task"""
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                if "outputs" not in t:
                    t["outputs"] = []
                t["outputs"].append({
                    "agent": agent_key,
                    "output": output,
                    "timestamp": datetime.now().isoformat()
                })
                # Update the assigned agent status
                for agent in t.get("assigned_agents", []):
                    if agent["agent"] == agent_key:
                        agent["status"] = "completed"
                        agent["output"] = output
                break
        self.store.save("tasks", tasks)

    def record_error(self, task_id: str, agent_key: str, error: str):
        tasks = self.store.load("tasks", {"tasks": []})
        for t in tasks.get("tasks", []):
            if t["id"] == task_id:
                if "errors" not in t:
                    t["errors"] = []
                t["errors"].append({
                    "agent": agent_key,
                    "error": error,
                    "timestamp": datetime.now().isoformat()
                })
                for agent in t.get("assigned_agents", []):
                    if agent["agent"] == agent_key:
                        agent["status"] = "error"
                break
        self.store.save("tasks", tasks)

    def get_active_tasks(self) -> List[Dict]:
        tasks = self.store.load("tasks", {"tasks": []})
        active = [t for t in tasks.get("tasks", []) if t["status"] in ["pending", "assigned", "executing"]]
        return active

    def get_completed_tasks(self) -> List[Dict]:
        tasks = self.store.load("tasks", {"tasks": []})
        completed = [t for t in tasks.get("tasks", []) if t["status"] in ["completed", "error"]]
        return completed[-20:]  # Last 20


# ============================================================
# LOG SYSTEM
# ============================================================
class LogSystem:
    """Store all system execution logs"""

    def __init__(self, store: DataStore):
        self.store = store

    def log(self, event: str, data: Dict = None, level: str = "info"):
        """Record a system log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "level": level,  # info, warning, error
            "data": data or {}
        }
        self.store.append_log("system", entry)

    def get_logs(self, limit: int = 50) -> List[Dict]:
        logs = self.store.load("system", {"entries": []})
        entries = logs.get("entries", [])
        return entries[-limit:]

    def get_errors(self, limit: int = 20) -> List[Dict]:
        logs = self.store.load("system", {"entries": []})
        errors = [e for e in logs.get("entries", []) if e.get("level") == "error"]
        return errors[-limit:]


# ============================================================
# RECEPTION SYSTEM
# ============================================================
class ReceptionSystem:
    """Department reception - receives tasks, decides which agent to assign"""

    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager

    def receive_task(self, task: Dict, department: str) -> List[str]:
        """
        Receive a task and determine which agents should handle it.
        Returns list of agent keys to assign.
        """
        agents_to_assign = []
        description = task.get("description", "").lower()

        if department == "web":
            # All web tasks start with planning
            agents_to_assign.append("planner")

            # Detect what type of work is needed
            if any(word in description for word in ["ui", "frontend", "html", "css", "design", "page", "page", "website", "landing"]):
                agents_to_assign.append("frontend")

            if any(word in description for word in ["api", "backend", "database", "server", "auth", "login", "endpoint"]):
                agents_to_assign.append("backend")

            # Always assign debug for code review
            agents_to_assign.append("debug")

        elif department == "seo":
            agents_to_assign.append("analyzer")

        elif department == "marketing":
            agents_to_assign.append("copywriter")

        return agents_to_assign

    def get_department_agents(self, department: str) -> List[Dict]:
        """Get all agents for a department with their details"""
        dept_agents = AGENT_REGISTRY.get(department, {})
        result = []
        for key, agent_info in dept_agents.items():
            skills = [self.skill_manager.get_skill(s) for s in agent_info.get("skills", [])]
            result.append({
                "id": key,
                "name": agent_info["name"],
                "role": agent_info["role"],
                "skills": [s for s in skills if s],
                "system_prompt": agent_info["system_prompt"],
                "status": "idle",
                "department": department
            })
        return result


# ============================================================
# DEPARTMENT EXECUTOR
# ============================================================
class DepartmentExecutor:
    """Execute tasks within a department using agents"""

    def __init__(self, department: str, skill_manager: SkillManager,
                 task_system: TaskSystem, log_system: LogSystem):
        self.department = department
        self.skill_manager = skill_manager
        self.task_system = task_system
        self.log_system = log_system

    async def execute_task(self, task_id: str, agent_key: str) -> str:
        """Execute a specific agent on a task. Returns output string."""
        agents = AGENT_REGISTRY.get(self.department, {})
        agent_info = agents.get(agent_key)

        if not agent_info:
            error_msg = f"Agent '{agent_key}' not found in department '{self.department}'"
            self.log_system.log(error_msg, {"task_id": task_id}, "error")
            self.task_system.record_error(task_id, agent_key, error_msg)
            return error_msg

        task = self.task_system.get_task(task_id)
        if not task:
            error_msg = f"Task '{task_id}' not found"
            self.log_system.log(error_msg, {"task_id": task_id}, "error")
            return error_msg

        # Update task status
        self.task_system.update_task(task_id, status="executing")
        self.log_system.log("agent_started", {
            "task_id": task_id,
            "agent": agent_key,
            "department": self.department
        })

        # Build messages with skill prompts
        agent_skills = agent_info.get("skills", [])
        skill_context = ""
        for skill_id in agent_skills:
            skill_prompt = self.skill_manager.get_skill_prompt(skill_id)
            if skill_prompt:
                skill_info = self.skill_manager.get_skill(skill_id)
                skill_context += f"\n--- {skill_info['name']} ---\n{skill_prompt}"

        system_prompt = agent_info["system_prompt"]
        if skill_context:
            system_prompt += f"\n\n## ACTIVE SKILLS:\n{skill_context}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""TASK: {task['description']}
Task ID: {task['id']}
Type: {task['type']}
Department: {self.department}

Execute this task and provide your complete output. Be specific and actionable."""}
        ]

        # Check for previous agent outputs to include context
        for output in task.get("outputs", []):
            messages.append({"role": "assistant", "content": f"[{output['agent']} output]: {output['output'][:500]}"})
            messages.append({"role": "user", "content": "Continue with the next step."})

        # Call Groq
        result = await call_groq(messages)

        if result.startswith("[ERROR]"):
            self.log_system.log("agent_error", {
                "task_id": task_id,
                "agent": agent_key,
                "error": result
            }, "error")
            self.task_system.record_error(task_id, agent_key, result)
            return result

        # Record output
        self.task_system.record_output(task_id, agent_key, result)
        self.log_system.log("agent_completed", {
            "task_id": task_id,
            "agent": agent_key,
            "output_length": len(result)
        })

        return result


# ============================================================
# MAIN ENGINE (CEO -> Controller -> Department -> Agents)
# ============================================================
class AgencyEngine:
    """Main engine: CEO -> Controller -> Department -> Agents"""

    def __init__(self):
        self.store = DataStore()
        self.skill_manager = SkillManager()
        self.task_system = TaskSystem(self.store)
        self.log_system = LogSystem(self.store)
        self.reception = ReceptionSystem(self.skill_manager)

        # Create department executors
        self.dept_executors = {}
        for dept in AGENT_REGISTRY:
            self.dept_executors[dept] = DepartmentExecutor(
                dept, self.skill_manager, self.task_system, self.log_system
            )

        self.log_system.log("system_initialized", {"message": "AI Agency Engine initialized"})

    async def process_ceo_request(self, message: str, project_id: str = None) -> Dict:
        """
        Main entry point: CEO sends request -> system processes -> returns result
        Flow: CEO -> Reception -> Department -> Agents -> Response
        """
        self.log_system.log("ceo_request", {"message": message[:100], "project_id": project_id})

        # Step 1: Analyze request to determine department(s)
        departments = self._detect_departments(message)
        if not departments:
            departments = ["web"]  # Default to web

        # Step 2: Create tasks for each department
        task_ids = {}
        for dept in departments:
            task_type = self._determine_task_type(message, dept)
            task_id = self.task_system.create_task(
                task_type=task_type,
                department=dept,
                description=message,
                project_id=project_id,
                source="ceo"
            )
            task_ids[dept] = task_id
            self.log_system.log("task_created", {"task_id": task_id, "department": dept})

            # Step 3: Reception decides which agents to assign
            agents = self.reception.receive_task(
                {"description": message, "type": task_type}, dept
            )
            for agent_key in agents:
                self.task_system.assign_agent(task_id, agent_key, dept)
                self.log_system.log("agent_assigned", {
                    "task_id": task_id,
                    "agent": agent_key,
                    "department": dept
                })

        # Step 4: Execute agents sequentially (planner first, then others)
        results = {}
        for dept, task_id in task_ids.items():
            executor = self.dept_executors.get(dept)
            if not executor:
                continue

            # Get agents assigned to this task
            task = self.task_system.get_task(task_id)
            for agent_entry in task.get("assigned_agents", []):
                agent_key = agent_entry["agent"]
                self.log_system.log("agent_executing", {
                    "task_id": task_id,
                    "agent": agent_key,
                    "department": dept
                })

                # Execute the agent
                output = await executor.execute_task(task_id, agent_key)

                results[f"{dept}.{agent_key}"] = {
                    "status": "error" if output.startswith("[ERROR]") else "completed",
                    "output": output[:4000],  # Truncate for response
                }

                # Check if agent errored, skip dependent agents if so
                if output.startswith("[ERROR]"):
                    self.log_system.log("agent_failed", {
                        "task_id": task_id,
                        "agent": agent_key,
                        "error": output[:200]
                    }, "error")

        # Step 5: Update all task statuses to completed
        for dept, task_id in task_ids.items():
            self.task_system.update_task(task_id, status="completed", completed_at=datetime.now().isoformat())

        # Step 6: Build response
        response = self._build_response(task_ids, results, departments)

        self.log_system.log("request_completed", {
            "task_ids": task_ids,
            "departments": departments,
            "result_count": len(results)
        })

        return response

    def _detect_departments(self, message: str) -> List[str]:
        """Detect which departments should handle this request"""
        msg = message.lower()
        departments = []

        if any(w in msg for w in ["website", "web", "site", "frontend", "backend", "api", "app", "page", "landing", "html", "css", "database", "server"]):
            departments.append("web")

        if any(w in msg for w in ["seo", "ranking", "google", "search", "keyword", "traffic", "optimize"]):
            departments.append("seo")

        if any(w in msg for w in ["marketing", "ad", "campaign", "email", "copy", "social", "content", "post", "brand"]):
            departments.append("marketing")

        return departments

    def _determine_task_type(self, message: str, department: str) -> str:
        """Determine task type from message"""
        msg = message.lower()
        if any(w in msg for w in ["build", "create", "make", "develop", "design"]):
            return "build"
        elif any(w in msg for w in ["fix", "debug", "repair", "error", "bug"]):
            return "fix"
        elif any(w in msg for w in ["analyze", "audit", "review", "check"]):
            return "analyze"
        elif any(w in msg for w in ["optimize", "improve", "speed", "performance"]):
            return "optimize"
        return "general"

    def _build_response(self, task_ids: Dict, results: Dict, departments: List[str]) -> Dict:
        """Build final response from execution results"""
        successful = [k for k, v in results.items() if v["status"] == "completed"]
        failed = [k for k, v in results.items() if v["status"] == "error"]

        response = {
            "status": "completed" if not failed else "partial",
            "departments_used": departments,
            "tasks": task_ids,
            "successful_agents": successful,
            "failed_agents": failed,
            "results": results,
            "summary": f"Task executed across {len(departments)} department(s), {len(successful)} agent(s) succeeded, {len(failed)} failed."
        }

        # Add key outputs for display
        for key, result in results.items():
            if result["status"] == "completed":
                response[f"{key}_output"] = result["output"][:1000]

        return response

    # ============================================================
    # STATUS METHODS (for dashboard)
    # ============================================================
    def get_overview(self) -> Dict:
        """Get system overview for dashboard"""
        tasks = self.store.load("tasks", {"tasks": []})
        task_list = tasks.get("tasks", [])

        active = [t for t in task_list if t["status"] in ["pending", "assigned", "executing"]]
        completed = [t for t in task_list if t["status"] == "completed"]
        errors = [t for t in task_list if t["status"] == "error"]

        # Count agents
        total_agents = sum(len(a) for a in AGENT_REGISTRY.values())
        idle_agents = total_agents - len(active)  # rough estimate

        return {
            "total_agents": total_agents,
            "active_tasks": len(active),
            "completed_tasks": len(completed),
            "error_tasks": len(errors),
            "departments": list(AGENT_REGISTRY.keys()),
            "skills_loaded": len(self.skill_manager.get_all_skills()),
            "status": "running"
        }

    def get_all_agents_info(self) -> List[Dict]:
        """Get info about all agents across departments"""
        all_agents = []
        for dept, agents in AGENT_REGISTRY.items():
            all_agents.extend(self.reception.get_department_agents(dept))
        return all_agents

    def get_department_info(self) -> List[Dict]:
        """Get info about all departments"""
        result = []
        for dept, agents in AGENT_REGISTRY.items():
            result.append({
                "name": dept,
                "agent_count": len(agents),
                "agents": self.reception.get_department_agents(dept),
                "description": {
                    "web": "Full web development with planning, frontend, backend, and debugging",
                    "seo": "SEO analysis and optimization",
                    "marketing": "Marketing copy and campaign content"
                }.get(dept, "")
            })
        return result

    def get_task_details(self, task_id: str) -> Optional[Dict]:
        return self.task_system.get_task(task_id)

    def get_active_tasks(self) -> List[Dict]:
        return self.task_system.get_active_tasks()

    def get_completed_tasks(self) -> List[Dict]:
        return self.task_system.get_completed_tasks()

    def get_system_logs(self, limit: int = 50) -> List[Dict]:
        return self.log_system.get_logs(limit)

    def get_errors(self, limit: int = 20) -> List[Dict]:
        return self.log_system.get_errors(limit)

    def get_skills(self) -> List[Dict]:
        return self.skill_manager.get_all_skills()