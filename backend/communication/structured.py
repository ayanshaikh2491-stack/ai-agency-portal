"""
Structured Communication System - Enforces strict hierarchy
User → CEO → Department → Agent → Department → CEO → User

Message Types:
1. TASK_ASSIGNMENT: CEO → Department
2. TASK_EXECUTION: Department → Agent  
3. TASK_RESULT: Agent → Department
4. FINAL_OUTPUT: Department → CEO
5. DIRECT_REQUEST: User → Department (direct mode)
6. DIRECT_RESPONSE: Department → User (direct mode)

NO direct CEO ↔ Agent communication
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import uuid


class MessageType(str, Enum):
    TASK_ASSIGNMENT = "task_assignment"      # CEO → Department
    TASK_EXECUTION = "task_execution"        # Department → Agent
    TASK_RESULT = "task_result"              # Agent → Department
    FINAL_OUTPUT = "final_output"            # Department → CEO
    DIRECT_REQUEST = "direct_request"        # User → Department
    DIRECT_RESPONSE = "direct_response"      # Department → User
    STATUS_UPDATE = "status_update"          # Any → CEO (monitoring)
    ERROR_REPORT = "error_report"            # Agent → Department → CEO


class MessagePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StructuredMessage:
    """
    Strictly structured message for agency communication.
    Enforces hierarchy rules.
    """
    
    def __init__(self, msg_type: MessageType, sender: str, receiver: str,
                 content: str, task_id: str = None, priority: MessagePriority = MessagePriority.MEDIUM,
                 metadata: Dict = None):
        self.id = str(uuid.uuid4())[:8]
        self.type = msg_type
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.task_id = task_id
        self.priority = priority
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow().isoformat()
        self.delivered_at = None
        self.status = "pending"
        
        # Validate communication rules
        self._validate_hierarchy()
    
    def _validate_hierarchy(self):
        """Enforce strict communication hierarchy"""
        # CEO cannot directly message agents
        if self.sender == "ceo" and self.receiver not in ["user"] and not self.receiver.endswith("_dept"):
            raise ValueError(f"CEO cannot directly message {self.receiver}. Must go through department.")
        
        # Agents can only message their department
        if self.sender.endswith("_agent") and not self.receiver.endswith("_dept"):
            if self.receiver != "ceo":  # Error reports can escalate
                raise ValueError(f"Agent {self.sender} can only message their department, not {self.receiver}")
        
        # Departments can message CEO or their agents
        if self.sender.endswith("_dept"):
            if self.receiver != "ceo" and not self.receiver.endswith("_agent") and self.receiver != "user":
                raise ValueError(f"Department {self.sender} can only message CEO, its agents, or user")
    
    def mark_delivered(self):
        self.delivered_at = datetime.utcnow().isoformat()
        self.status = "delivered"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "task_id": self.task_id,
            "priority": self.priority.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "delivered_at": self.delivered_at,
            "status": self.status
        }


class CommunicationHub:
    """
    Central communication hub that enforces hierarchy rules.
    All messages pass through here for validation and routing.
    """
    
    def __init__(self):
        self.messages: List[Dict] = []
        self.message_log: Dict[str, List[Dict]] = {}
        self.active_tasks: Dict[str, Dict] = {}
        self.duplicate_tracker: Dict[str, str] = {}  # task_hash -> task_id
    
    def send_message(self, msg_type: MessageType, sender: str, receiver: str,
                     content: str, task_id: str = None, priority: MessagePriority = MessagePriority.MEDIUM,
                     metadata: Dict = None) -> Dict:
        """Send a structured message through the hub"""
        try:
            msg = StructuredMessage(msg_type, sender, receiver, content, task_id, priority, metadata)
            msg.mark_delivered()
            msg_dict = msg.to_dict()
            
            self.messages.append(msg_dict)
            
            # Index by task_id
            if task_id:
                if task_id not in self.message_log:
                    self.message_log[task_id] = []
                self.message_log[task_id].append(msg_dict)
            
            return msg_dict
        except ValueError as e:
            return {"error": str(e), "type": "hierarchy_violation"}
    
    def get_task_messages(self, task_id: str) -> List[Dict]:
        """Get all messages for a specific task"""
        return self.message_log.get(task_id, [])
    
    def get_messages_by_type(self, msg_type: MessageType) -> List[Dict]:
        """Get all messages of a specific type"""
        return [m for m in self.messages if m["type"] == msg_type.value]
    
    def get_messages_by_sender(self, sender: str) -> List[Dict]:
        """Get all messages from a specific sender"""
        return [m for m in self.messages if m["sender"] == sender]
    
    def get_messages_by_receiver(self, receiver: str) -> List[Dict]:
        """Get all messages for a specific receiver"""
        return [m for m in self.messages if m["receiver"] == receiver]
    
    def track_duplicate(self, task_hash: str, task_id: str) -> bool:
        """Check if task is duplicate. Returns True if duplicate found."""
        if task_hash in self.duplicate_tracker:
            return True
        self.duplicate_tracker[task_hash] = task_id
        return False
    
    def get_communication_stats(self) -> Dict:
        """Get communication statistics"""
        stats = {
            "total_messages": len(self.messages),
            "by_type": {},
            "by_sender": {},
            "active_tasks": len(self.active_tasks)
        }
        
        for msg in self.messages:
            msg_type = msg["type"]
            sender = msg["sender"]
            stats["by_type"][msg_type] = stats["by_type"].get(msg_type, 0) + 1
            stats["by_sender"][sender] = stats["by_sender"].get(sender, 0) + 1
        
        return stats
