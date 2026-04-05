"""
Base Agent Class - Foundation for all AI agents
Every agent inherits from this and gets memory, communication, and task handling
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid


class BaseAgent:
    """
    Base class for all AI agents in the agency.
    Provides core functionality: memory, communication, task execution.
    """
    
    def __init__(self, name: str, role: str, department: str, description: str = "", capabilities: List[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.department = department
        self.description = description
        self.capabilities = capabilities or []
        self.status = "active"  # active, busy, offline
        self.memory: Dict[str, Any] = {}
        self.task_history: List[Dict] = []
        self.message_history: List[Dict] = []
    
    def think(self, prompt: str) -> str:
        """
        Agent processes information and returns a response.
        Override this method for specific agent behavior.
        """
        return f"[{self.name}] Thinking about: {prompt[:50]}..."
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task and return result.
        Override this in child classes for specific behavior.
        """
        self.status = "busy"
        result = {
            "task_id": task.get("id"),
            "agent_id": self.id,
            "status": "completed",
            "output": self.think(task.get("description", "")),
            "completed_at": datetime.utcnow().isoformat()
        }
        self.task_history.append(result)
        self.status = "active"
        return result
    
    def store_memory(self, key: str, value: Any, memory_type: str = "context", importance: int = 1):
        """Store something in agent's memory"""
        self.memory[key] = {
            "value": value,
            "type": memory_type,
            "importance": importance,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def recall_memory(self, key: str) -> Optional[Any]:
        """Recall something from memory"""
        mem = self.memory.get(key)
        if mem:
            return mem.get("value")
        return None
    
    def search_memory(self, query: str) -> List[Dict]:
        """Search through agent's memory"""
        results = []
        for key, value in self.memory.items():
            if query.lower() in key.lower() or query.lower() in str(value).lower():
                results.append({"key": key, **value})
        return results
    
    def create_message(self, content: str, message_type: str = "text", 
                       channel: str = "general", subject: str = None) -> Dict:
        """Create a message to send to other agents"""
        return {
            "sender_id": self.id,
            "sender_name": self.name,
            "content": content,
            "message_type": message_type,
            "channel": channel,
            "subject": subject,
            "created_at": datetime.utcnow().isoformat()
        }
    
    def receive_message(self, message: Dict) -> str:
        """
        Receive and process a message from another agent.
        Returns response.
        """
        self.message_history.append(message)
        sender = message.get("sender_name", "Unknown")
        content = message.get("content", "")
        
        # Default response - override in child classes
        response = f"[{self.name}] Received message from {sender}: {content[:50]}..."
        return response
    
    def request_help(self, task: Dict, target_agent: str = None) -> Dict:
        """Request help from another agent"""
        return self.create_message(
            content=f"I need help with: {task.get('description', '')}",
            message_type="request",
            channel=self.department,
            subject=f"Help Request: {task.get('title', 'Unknown Task')}"
        )
    
    def report_error(self, error: str, task_id: str = None) -> Dict:
        """Report an error"""
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "error_type": type(error).__name__ if isinstance(error, Exception) else "RuntimeError",
            "error_message": str(error),
            "task_id": task_id,
            "severity": "error",
            "created_at": datetime.utcnow().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get agent's current status"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "status": self.status,
            "tasks_completed": len([t for t in self.task_history if t.get("status") == "completed"]),
            "capabilities": self.capabilities
        }
    
    def __repr__(self):
        return f"<Agent: {self.name} ({self.role}) - {self.department}>"