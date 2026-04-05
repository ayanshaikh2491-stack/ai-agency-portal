"""
Web Department - Loads all 8 agents from individual files
Provides chat interface with Groq API connection for each agent
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import os, json, httpx, asyncio

# Import all agents from individual files
from .agents.coordinator import CoordinatorAgent, SYSTEM_PROMPT as COORDINATOR_PROMPT
from .agents.ui_designer import UIDesignerAgent, SYSTEM_PROMPT as UI_PROMPT
from .agents.frontend import FrontendAgent, SYSTEM_PROMPT as FRONTEND_PROMPT
from .agents.backend import BackendAgent, SYSTEM_PROMPT as BACKEND_PROMPT
from .agents.api_manager import APIManagerAgent, SYSTEM_PROMPT as API_PROMPT
from .agents.seo import SEOAgent, SYSTEM_PROMPT as SEO_PROMPT
from .agents.performance import PerformanceAgent, SYSTEM_PROMPT as PERF_PROMPT
from .agents.qa import QAAgent, SYSTEM_PROMPT as QA_PROMPT

API_URL = "https://api.groq.com/openai/v1/chat/completions"

class WebDepartment:
    """Web Department with all 8 agents - each in their own file"""

    def __init__(self):
        self.agents = {
            "coordinator": CoordinatorAgent(),
            "ui_designer": UIDesignerAgent(),
            "frontend": FrontendAgent(),
            "backend": BackendAgent(),
            "api_manager": APIManagerAgent(),
            "seo": SEOAgent(),
            "performance": PerformanceAgent(),
            "qa": QAAgent()
        }
        self.task_queue = []
        self.completed_tasks = []
        self.message_log = []
        self.settings = self._load_settings()

    def _load_settings(self) -> Dict:
        """Load API settings from settings.json"""
        settings_path = os.path.join(os.path.dirname(__file__), "..", "..", "settings.json")
        if os.path.exists(settings_path):
            with open(settings_path) as f:
                return json.load(f)
        return {}

    def _get_api_key(self, agent_key: str) -> tuple:
        """Get API key and model for an agent"""
        settings = self.settings
        dept_settings = settings.get("web", {})
        api_key = dept_settings.get("api_key", os.getenv("GROQ_API_KEY", ""))
        model = dept_settings.get("model", "llama-3.1-8b-instant")
        return api_key, model

    async def chat_with_agent(self, agent_key: str, message: str, history: Optional[List[Dict]] = None) -> Dict:
        """Chat with a specific web agent using Groq API"""
        agent = self.agents.get(agent_key)
        if not agent:
            return {"error": f"Agent '{agent_key}' not found", "sender": "System"}

        api_key, model = self._get_api_key(agent_key)
        if not api_key:
            return {"error": "API key not set - go to Settings", "sender": "System"}

        msgs = [{"role": "system", "content": agent.system_prompt}]
        if history:
            msgs.extend(history[-8:])
        msgs.append({"role": "user", "content": message})

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    API_URL,
                    json={"model": model, "messages": msgs, "temperature": 0.7, "max_tokens": 1024},
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                )
                if r.status_code == 200:
                    response = r.json()["choices"][0]["message"]["content"]
                    agent.task_history.append({"message": message, "response": response, "time": datetime.utcnow().isoformat()})
                    return {"sender": agent.name, "response": response, "agent": agent_key}
                else:
                    return {"sender": "System", "response": f"[API Error: {r.status_code}]", "agent": agent_key}
        except Exception as e:
            return {"sender": "System", "response": f"[Connection Error: {str(e)[:100]}]", "agent": agent_key}

    async def chat_with_coordinator(self, message: str, history: List[Dict] = None) -> Dict:
        """Chat with Sara (Coordinator)"""
        return await self.chat_with_agent("coordinator", message, history)

    def get_all_agents(self) -> List[Dict]:
        """Get all agents with their status"""
        return [agent.get_status() for agent in self.agents.values()]

    def get_agent(self, agent_key: str) -> Optional[Any]:
        """Get a specific agent"""
        return self.agents.get(agent_key)

    def get_agent_by_name(self, name: str) -> Optional[Any]:
        """Get agent by name (e.g., 'Maya', 'Sara')"""
        for key, agent in self.agents.items():
            if agent.name.lower() == name.lower():
                return agent
        return None

    def assign_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinator assigns and routes tasks"""
        coordinator = self.agents["coordinator"]
        result = coordinator.execute_task(task)
        self.task_queue.append({"task": task, "status": "assigned"})
        return result

    def send_message(self, from_agent: str, to_agent: str, task: str) -> Dict:
        """Send message between agents"""
        if from_agent in self.agents and to_agent in self.agents:
            msg = {
                "from": self.agents[from_agent].name,
                "to": self.agents[to_agent].name,
                "task": task,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.message_log.append(msg)
            return {"sent": msg, "received": f"[{self.agents[to_agent].name}] Received"}
        return {"error": "Agent not found"}

    def get_status(self) -> Dict:
        return {
            "department": "web",
            "total_agents": len(self.agents),
            "agents": self.get_all_agents(),
            "task_queue": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "messages": len(self.message_log)
        }

    def get_agent_files(self, agent_key: str) -> Dict:
        """Get all md files for an agent (skills.md, system.md)"""
        agent = self.agents.get(agent_key)
        if not agent:
            return {"error": f"Agent '{agent_key}' not found"}
        
        md_dir = os.path.join(os.path.dirname(__file__), "agents", "md")
        agent_name = agent.name.lower()
        
        files = {}
        for filename in os.listdir(md_dir):
            if filename.startswith(agent_name) and filename.endswith(".md"):
                filepath = os.path.join(md_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    files[filename] = f.read()
        
        return {
            "agent": agent.name,
            "agent_key": agent_key,
            "files": files,
            "file_names": list(files.keys())
        }

    def get_agent_file_content(self, agent_key: str, filename: str) -> Dict:
        """Get specific file content for an agent"""
        agent = self.agents.get(agent_key)
        if not agent:
            return {"error": f"Agent '{agent_key}' not found"}
        
        agent_name = agent.name.lower()
        md_dir = os.path.join(os.path.dirname(__file__), "agents", "md")
        filepath = os.path.join(md_dir, filename)
        
        if not os.path.exists(filepath):
            return {"error": f"File '{filename}' not found for agent '{agent.name}'"}
        
        if not filename.startswith(agent_name):
            return {"error": f"File '{filename}' does not belong to agent '{agent.name}'"}
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "agent": agent.name,
            "agent_key": agent_key,
            "filename": filename,
            "content": content
        }

    def get_agent_files(self, agent_key: str) -> Dict:
        """Get all md files for an agent (skills.md, system.md)"""
        agent = self.agents.get(agent_key)
        if not agent:
            return {"error": f"Agent '{agent_key}' not found"}
        
        md_dir = os.path.join(os.path.dirname(__file__), "agents", "md")
        agent_name = agent.name.lower()
        
        files = {}
        for filename in os.listdir(md_dir):
            if filename.startswith(agent_name) and filename.endswith(".md"):
                filepath = os.path.join(md_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    files[filename] = f.read()
        
        return {
            "agent": agent.name,
            "agent_key": agent_key,
            "files": files,
            "file_names": list(files.keys())
        }

    def get_agent_file_content(self, agent_key: str, filename: str) -> Dict:
        """Get specific file content for an agent"""
        agent = self.agents.get(agent_key)
        if not agent:
            return {"error": f"Agent '{agent_key}' not found"}
        
        agent_name = agent.name.lower()
        md_dir = os.path.join(os.path.dirname(__file__), "agents", "md")
        filepath = os.path.join(md_dir, filename)
        
        if not os.path.exists(filepath):
            return {"error": f"File '{filename}' not found for agent '{agent.name}'"}
        
        if not filename.startswith(agent_name):
            return {"error": f"File '{filename}' does not belong to agent '{agent.name}'"}
        
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "agent": agent.name,
            "agent_key": agent_key,
            "filename": filename,
            "content": content
        }
