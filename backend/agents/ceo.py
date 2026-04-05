"""
CEO Agent - The main coordinator of the AI Agency
Assigns tasks, monitors departments, coordinates work between departments
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from .base import BaseAgent


class CEOAgent(BaseAgent):
    """
    CEO Agent - Top-level coordinator
    Manages departments, assigns tasks, monitors progress
    """
    
    def __init__(self, name: str = "CEO"):
        super().__init__(
            name=name,
            role="ceo",
            department="management",
            description="Chief Executive Officer - Manages all departments and coordinates work",
            capabilities=["task_assignment", "department_management", "progress_monitoring", "cross_department_coordination"]
        )
        self.departments: Dict[str, Dict] = {}
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict] = []
        self.completed_tasks: List[Dict] = []
        self.active_tasks: Dict[str, Dict] = {}
    
    def register_department(self, dept_name: str, dept_lead: BaseAgent):
        """Register a department with its lead agent"""
        self.departments[dept_name] = {
            "name": dept_name,
            "lead": dept_lead,
            "lead_id": dept_lead.id,
            "agents": [],
            "status": "active"
        }
        self.agents[dept_lead.id] = dept_lead
        print(f"[CEO] Department '{dept_name}' registered with lead: {dept_lead.name}")
    
    def register_agent(self, agent: BaseAgent, department: str):
        """Register an agent to a department"""
        if department not in self.departments:
            raise ValueError(f"Department '{department}' not registered")
        
        self.agents[agent.id] = agent
        self.departments[department]["agents"].append(agent.id)
        print(f"[CEO] Agent '{agent.name}' registered to department '{department}'")
    
    def assign_task(self, task: Dict[str, Any], department: str, agent_id: str = None) -> Dict:
        """
        Assign a task to a department or specific agent
        """
        task["assigned_by"] = self.id
        task["assigned_at"] = datetime.utcnow().isoformat()
        task["status"] = "assigned"
        
        if agent_id and agent_id in self.agents:
            # Assign to specific agent
            agent = self.agents[agent_id]
            task["agent_id"] = agent_id
            task["agent_name"] = agent.name
            self.active_tasks[task.get("id", str(len(self.active_tasks)))] = task
            print(f"[CEO] Task '{task['title']}' assigned to {agent.name}")
            
            # Notify the agent
            message = self.create_message(
                content=f"New task assigned: {task['title']}\n{task.get('description', '')}",
                message_type="request",
                channel=department,
                subject=f"Task Assignment: {task['title']}"
            )
            agent.receive_message(message)
        elif department in self.departments:
            # Assign to department lead
            dept = self.departments[department]
            lead = dept["lead"]
            task["agent_id"] = lead.id
            task["agent_name"] = lead.name
            self.active_tasks[task.get("id", str(len(self.active_tasks)))] = task
            print(f"[CEO] Task '{task['title']}' assigned to department '{department}' (lead: {lead.name})")
            
            # Notify the department lead
            message = self.create_message(
                content=f"New task for your department: {task['title']}\n{task.get('description', '')}",
                message_type="request",
                channel=department,
                subject=f"Department Task: {task['title']}"
            )
            lead.receive_message(message)
        else:
            raise ValueError(f"Department '{department}' not found")
        
        return task
    
    def create_task(self, title: str, description: str, department: str, 
                    priority: int = 1, input_data: Dict = None) -> Dict:
        """Create a new task and assign it"""
        task = {
            "id": str(len(self.task_queue) + 1),
            "title": title,
            "description": description,
            "department": department,
            "priority": priority,
            "input_data": input_data or {},
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        self.task_queue.append(task)
        return task
    
    def assign_and_execute(self, title: str, description: str, department: str, 
                           agent_id: str = None, priority: int = 1) -> Dict:
        """Create, assign, and execute a task"""
        task = self.create_task(title, description, department, priority)
        assigned_task = self.assign_task(task, department, agent_id)
        
        # Execute the task through the assigned agent
        if assigned_task.get("agent_id") in self.agents:
            agent = self.agents[assigned_task["agent_id"]]
            result = agent.execute_task(assigned_task)
            assigned_task["result"] = result
            assigned_task["status"] = result.get("status", "completed")
            
            if assigned_task["status"] == "completed":
                self.completed_tasks.append(assigned_task)
                self.active_tasks.pop(assigned_task["id"], None)
        
        return assigned_task
    
    def monitor_progress(self) -> Dict:
        """Get overview of all departments and tasks"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "departments": {},
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.task_queue),
            "total_agents": len(self.agents)
        }
        
        for dept_name, dept in self.departments.items():
            lead = dept["lead"]
            report["departments"][dept_name] = {
                "lead": lead.name,
                "lead_status": lead.status,
                "agent_count": len(dept["agents"]),
                "agents": []
            }
            
            for agent_id in dept["agents"]:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    report["departments"][dept_name]["agents"].append(agent.get_status())
        
        return report
    
    def broadcast_message(self, content: str, subject: str = None, 
                          department: str = None) -> Dict:
        """Send message to all agents or a specific department"""
        message = self.create_message(
            content=content,
            message_type="update",
            channel=department or "all",
            subject=subject
        )
        
        targets = self.agents.values()
        if department:
            targets = [self.agents[aid] for aid in self.departments.get(department, {}).get("agents", [])]
            if department in self.departments:
                targets.append(self.departments[department]["lead"])
        
        responses = {}
        for agent in targets:
            responses[agent.name] = agent.receive_message(message)
        
        message["responses"] = responses
        return message
    
    def request_cross_department_collaboration(self, from_dept: str, to_dept: str, 
                                                request: str) -> Dict:
        """Facilitate communication between departments"""
        if from_dept not in self.departments or to_dept not in self.departments:
            raise ValueError("One or both departments not found")
        
        from_lead = self.departments[from_dept]["lead"]
        to_lead = self.departments[to_dept]["lead"]
        
        # Send request from one department to another
        message = self.create_message(
            content=f"Request from {from_dept} department: {request}",
            message_type="request",
            channel="cross_department",
            subject=f"Cross-Department Request: {from_dept} -> {to_dept}"
        )
        
        to_lead.receive_message(message)
        
        return {
            "from": from_dept,
            "to": to_dept,
            "request": request,
            "status": "delivered"
        }
    
    def get_department_status(self, department: str) -> Dict:
        """Get status of a specific department"""
        if department not in self.departments:
            raise ValueError(f"Department '{department}' not found")
        
        dept = self.departments[department]
        lead = dept["lead"]
        
        return {
            "name": department,
            "lead": lead.get_status(),
            "agents": [self.agents[aid].get_status() for aid in dept["agents"] if aid in self.agents],
            "status": dept["status"]
        }
    
    def think(self, prompt: str) -> str:
        """CEO processes strategic information"""
        return f"[CEO {self.name}] Analyzing: {prompt[:50]}... Considering department capacities and priorities."
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """CEO executes a management task"""
        self.status = "busy"
        result = {
            "task_id": task.get("id"),
            "agent_id": self.id,
            "status": "completed",
            "output": f"[CEO] Management task completed: {task.get('title', '')}",
            "completed_at": datetime.utcnow().isoformat()
        }
        self.task_history.append(result)
        self.status = "active"
        return result