"""
Department Manager - Acts as the manager for each department
Handles: task reception, analysis, agent selection, assignment, tracking, 
duplicate prevention, result collection, and final output return.

Each department IS the manager (no separate manager role).
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json


class DepartmentManager:
    """
    Department Manager Logic
    Each department instance acts as its own manager.
    """
    
    def __init__(self, name: str, lead_agent: str, agents: List[str], 
                 skills: List[str], description: str = ""):
        self.name = name
        self.lead_agent = lead_agent
        self.agents = agents  # List of agent IDs/names in this department
        self.skills = skills
        self.description = description
        self.status = "active"
        
        # Task management
        self.active_tasks: Dict[str, Dict] = {}
        self.completed_tasks: List[Dict] = []
        self.task_queue: List[Dict] = []
        
        # Duplicate prevention
        self.task_hashes: Dict[str, str] = {}  # hash -> task_id
        
        # Agent workload tracking
        self.agent_workload: Dict[str, int] = {agent: 0 for agent in agents}
        self.agent_skills: Dict[str, List[str]] = {}
        self.agent_status: Dict[str, str] = {agent: "active" for agent in agents}
        
        # Performance tracking
        self.stats = {
            "tasks_received": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_completion_time": 0,
            "completion_times": []
        }
    
    def receive_task(self, task: Dict) -> Dict:
        """
        Step 1: Receive task from CEO or direct user request
        """
        task_id = task.get("id", f"task_{len(self.task_queue) + 1}")
        task["received_at"] = datetime.utcnow().isoformat()
        task["department"] = self.name
        task["dept_status"] = "received"
        
        self.task_queue.append(task)
        self.stats["tasks_received"] += 1
        
        return {
            "status": "received",
            "task_id": task_id,
            "department": self.name,
            "message": f"Task received by {self.name} department"
        }
    
    def analyze_task(self, task: Dict) -> Dict:
        """
        Step 2: Analyze task to determine requirements and best agent
        """
        task_id = task.get("id")
        description = task.get("description", "").lower()
        title = task.get("title", "").lower()
        combined = f"{title} {description}"
        
        # Determine task type and required skills
        analysis = {
            "task_id": task_id,
            "task_type": self._classify_task(combined),
            "required_skills": self._extract_required_skills(combined),
            "complexity": self._estimate_complexity(combined),
            "estimated_agents": self._estimate_agents_needed(combined),
            "dependencies": self._identify_dependencies(combined)
        }
        
        task["analysis"] = analysis
        task["dept_status"] = "analyzed"
        
        return analysis
    
    def select_agent(self, task: Dict) -> str:
        """
        Step 3: Select the correct agent based on task analysis
        """
        analysis = task.get("analysis", {})
        required_skills = analysis.get("required_skills", [])
        task_type = analysis.get("task_type", "general")
        
        # Score each agent based on skills and workload
        best_agent = None
        best_score = -1
        
        for agent in self.agents:
            score = self._score_agent(agent, required_skills, task_type)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if not best_agent:
            best_agent = self.lead_agent
        
        return best_agent
    
    def assign_task(self, task: Dict, agent_id: str) -> Dict:
        """
        Step 4: Assign task to selected agent
        """
        task_id = task.get("id")
        task["assigned_agent"] = agent_id
        task["assigned_at"] = datetime.utcnow().isoformat()
        task["dept_status"] = "assigned"
        
        self.active_tasks[task_id] = task
        self.agent_workload[agent_id] = self.agent_workload.get(agent_id, 0) + 1
        self.agent_status[agent_id] = "busy"
        
        # Remove from queue
        self.task_queue = [t for t in self.task_queue if t.get("id") != task_id]
        
        return {
            "status": "assigned",
            "task_id": task_id,
            "agent": agent_id,
            "department": self.name
        }
    
    def track_progress(self, task_id: str, status: str, progress: float = 0.0) -> Dict:
        """
        Step 5: Track task progress
        """
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["progress"] = progress
            self.active_tasks[task_id]["current_status"] = status
            self.active_tasks[task_id]["last_update"] = datetime.utcnow().isoformat()
            
            return {
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "department": self.name
            }
        
        return {"error": "Task not found"}
    
    def prevent_duplicate(self, task: Dict) -> bool:
        """
        Step 6: Prevent duplicate work
        Returns True if task is duplicate
        """
        task_hash = self._generate_task_hash(task)
        
        if task_hash in self.task_hashes:
            existing_task_id = self.task_hashes[task_hash]
            return True
        
        task_id = task.get("id", f"task_{len(self.task_hashes) + 1}")
        self.task_hashes[task_hash] = task_id
        return False
    
    def collect_result(self, task_id: str, result: Dict) -> Dict:
        """
        Step 7: Collect results from agent
        """
        if task_id in self.active_tasks:
            task = self.active_tasks.pop(task_id)
            task["result"] = result
            task["completed_at"] = datetime.utcnow().isoformat()
            task["dept_status"] = "completed"
            
            # Update agent status
            agent_id = task.get("assigned_agent")
            if agent_id:
                self.agent_workload[agent_id] = max(0, self.agent_workload.get(agent_id, 1) - 1)
                self.agent_status[agent_id] = "active"
            
            # Track completion time
            created = task.get("created_at") or task.get("received_at")
            if created:
                try:
                    from datetime import datetime as dt
                    start = dt.fromisoformat(created.replace("Z", "+00:00"))
                    end = dt.fromisoformat(task["completed_at"].replace("Z", "+00:00"))
                    duration = (end - start).total_seconds()
                    self.stats["completion_times"].append(duration)
                    self.stats["avg_completion_time"] = sum(self.stats["completion_times"]) / len(self.stats["completion_times"])
                except:
                    pass
            
            self.completed_tasks.append(task)
            self.stats["tasks_completed"] += 1
            
            return {
                "status": "collected",
                "task_id": task_id,
                "result": result,
                "department": self.name
            }
        
        return {"error": "Task not found in active tasks"}
    
    def return_final_output(self, task_id: str) -> Dict:
        """
        Step 8: Return final output to CEO or user
        """
        # Check completed tasks
        for task in self.completed_tasks:
            if task.get("id") == task_id:
                return {
                    "status": "success",
                    "task_id": task_id,
                    "department": self.name,
                    "output": task.get("result", {}),
                    "metadata": {
                        "assigned_agent": task.get("assigned_agent"),
                        "completed_at": task.get("completed_at"),
                        "analysis": task.get("analysis", {})
                    }
                }
        
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "status": "in_progress",
                "task_id": task_id,
                "department": self.name,
                "progress": task.get("progress", 0),
                "current_status": task.get("current_status", "unknown")
            }
        
        return {"error": "Task not found"}
    
    def get_department_status(self) -> Dict:
        """Get complete department status"""
        return {
            "name": self.name,
            "lead": self.lead_agent,
            "agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "queued_tasks": len(self.task_queue),
            "agent_status": self.agent_status,
            "agent_workload": self.agent_workload,
            "stats": self.stats,
            "status": self.status
        }
    
    # --- Private Helper Methods ---
    
    def _classify_task(self, text: str) -> str:
        """Classify task type based on content"""
        if any(kw in text for kw in ["api", "backend", "database", "server", "endpoint"]):
            return "backend"
        elif any(kw in text for kw in ["frontend", "ui", "component", "page", "design"]):
            return "frontend"
        elif any(kw in text for kw in ["test", "qa", "bug", "quality"]):
            return "testing"
        elif any(kw in text for kw in ["deploy", "ci/cd", "infrastructure", "docker"]):
            return "devops"
        elif any(kw in text for kw in ["security", "vulnerability", "audit"]):
            return "security"
        elif any(kw in text for kw in ["data", "analytics", "ml", "chart"]):
            return "data"
        elif any(kw in text for kw in ["marketing", "seo", "content", "social"]):
            return "marketing"
        else:
            return "general"
    
    def _extract_required_skills(self, text: str) -> List[str]:
        """Extract required skills from task description"""
        skill_map = {
            "api": ["api_development"],
            "database": ["database_design"],
            "test": ["unit_testing", "integration_testing"],
            "deploy": ["deployment", "ci_cd"],
            "security": ["security_audit"],
            "ui": ["ui_design"],
            "frontend": ["component_development"],
            "data": ["data_analysis"],
            "ml": ["ml_modeling"],
        }
        
        skills = []
        for keyword, skill_list in skill_map.items():
            if keyword in text:
                skills.extend(skill_list)
        
        return skills if skills else ["general"]
    
    def _estimate_complexity(self, text: str) -> str:
        """Estimate task complexity"""
        complex_words = ["complex", "advanced", "enterprise", "scalable", "production"]
        simple_words = ["simple", "basic", "quick", "small"]
        
        if any(w in text for w in complex_words):
            return "high"
        elif any(w in text for w in simple_words):
            return "low"
        else:
            return "medium"
    
    def _estimate_agents_needed(self, text: str) -> int:
        """Estimate how many agents needed"""
        if any(kw in text for kw in ["full", "complete", "end-to-end", "entire"]):
            return 3
        elif any(kw in text for kw in ["complex", "large", "enterprise"]):
            return 2
        else:
            return 1
    
    def _identify_dependencies(self, text: str) -> List[str]:
        """Identify task dependencies"""
        deps = []
        if "api" in text and ("frontend" in text or "ui" in text):
            deps.append("api_first")
        if "database" in text:
            deps.append("schema_first")
        if "test" in text:
            deps.append("implementation_first")
        return deps
    
    def _score_agent(self, agent: str, required_skills: List[str], task_type: str) -> float:
        """Score agent suitability for task"""
        score = 0.0
        
        # Lead agent preference
        if agent == self.lead_agent:
            score += 1.0
        
        # Workload consideration (prefer less busy agents)
        workload = self.agent_workload.get(agent, 0)
        score += max(0, 3 - workload) * 0.5
        
        # Status consideration
        if self.agent_status.get(agent) == "active":
            score += 2.0
        
        # Skill matching
        agent_skills = self.agent_skills.get(agent, [])
        for skill in required_skills:
            if skill in agent_skills:
                score += 1.5
        
        return score
    
    def _generate_task_hash(self, task: Dict) -> str:
        """Generate hash for duplicate detection"""
        content = f"{task.get('title', '')}{task.get('description', '')}{task.get('type', '')}"
        return hashlib.md5(content.lower().encode()).hexdigest()
