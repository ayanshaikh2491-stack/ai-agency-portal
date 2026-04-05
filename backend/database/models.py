"""
Database models for AI Agency Portal - Memory System
All agent data, tasks, workflows, and communications are stored here.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class DepartmentEnum(str, enum.Enum):
    WEBSITE = "website"
    BACKEND = "backend"
    FRONTEND = "frontend"
    MARKETING = "marketing"
    QA = "qa"


class TaskStatusEnum(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class AgentRoleEnum(str, enum.Enum):
    CEO = "ceo"
    DEPARTMENT_LEAD = "department_lead"
    DEVELOPER = "developer"
    TESTER = "tester"
    DESIGNER = "designer"


class Agent(Base):
    """Represents an AI agent in the agency"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    role = Column(Enum(AgentRoleEnum), nullable=False)
    department = Column(Enum(DepartmentEnum), nullable=False)
    description = Column(Text, nullable=True)
    capabilities = Column(JSON, nullable=True)
    status = Column(String(20), default="active")  # active, busy, offline
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="agent")
    messages_sent = relationship("Message", back_populates="sender_agent", foreign_keys="Message.sender_id")
    messages_received = relationship("Message", back_populates="receiver_agent", foreign_keys="Message.receiver_id")
    memories = relationship("AgentMemory", back_populates="agent")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value if self.role else None,
            "department": self.department.value if self.department else None,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Department(Base):
    """Represents a department in the agency"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Enum(DepartmentEnum), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    lead_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Agent", foreign_keys=[lead_id])
    agents = relationship("Agent", foreign_keys="[Agent.department]")
    workflows = relationship("Workflow", back_populates="department")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name.value if self.name else None,
            "description": self.description,
            "lead_id": self.lead_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Task(Base):
    """Represents a task assigned to an agent"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    priority = Column(Integer, default=1)  # 1-5 scale
    assigned_by = Column(Integer, ForeignKey("agents.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    department = Column(Enum(DepartmentEnum), nullable=False)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    workflow = relationship("Workflow", back_populates="tasks")
    comments = relationship("TaskComment", back_populates="task")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "priority": self.priority,
            "assigned_by": self.assigned_by,
            "agent_id": self.agent_id,
            "department": self.department.value if self.department else None,
            "parent_task_id": self.parent_task_id,
            "workflow_id": self.workflow_id,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskComment(Base):
    """Comments on tasks for agent discussion"""
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="comments")
    agent = relationship("Agent")
    
    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(Base):
    """Messages between agents for communication"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("agents.id"), nullable=True)  # None = broadcast
    channel = Column(String(50), nullable=False)  # department, workflow, general
    subject = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, request, response, error, update
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    attachments = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sender_agent = relationship("Agent", back_populates="messages_sent", foreign_keys=[sender_id])
    receiver_agent = relationship("Agent", back_populates="messages_received", foreign_keys=[receiver_id])
    replies = relationship("Message", backref=backref("parent_message", remote_side=[id]))
    
    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "channel": self.channel,
            "subject": self.subject,
            "content": self.content,
            "message_type": self.message_type,
            "parent_message_id": self.parent_message_id,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AgentMemory(Base):
    """Persistent memory for agents - stores context, learnings, and history"""
    __tablename__ = "agent_memories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    memory_type = Column(String(50), nullable=False)  # context, learning, history, skill
    key = Column(String(200), nullable=False)
    value = Column(JSON, nullable=False)
    importance = Column(Integer, default=1)  # 1-5 scale for memory prioritization
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="memories")
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "memory_type": self.memory_type,
            "key": self.key,
            "value": self.value,
            "importance": self.importance,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
        }


class Workflow(Base):
    """Workflow definitions for task pipelines"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    department = Column(Enum(DepartmentEnum), nullable=False)
    steps = Column(JSON, nullable=False)  # List of step definitions
    status = Column(String(20), default="active")  # active, paused, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tasks = relationship("Task", back_populates="workflow")
    runs = relationship("WorkflowRun", back_populates="workflow")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "department": self.department.value if self.department else None,
            "steps": self.steps,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class WorkflowRun(Base):
    """Tracking individual workflow executions"""
    __tablename__ = "workflow_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    current_step = Column(Integer, default=0)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    workflow = relationship("Workflow", back_populates="runs")
    
    def to_dict(self):
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "current_step": self.current_step,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class ErrorLog(Base):
    """Centralized error logging for all agent issues"""
    __tablename__ = "error_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    severity = Column(String(20), default="error")  # warning, error, critical
    resolved = Column(Integer, default=0)  # 0 = unresolved, 1 = resolved
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent")
    task = relationship("Task")
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "severity": self.severity,
            "resolved": self.resolved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }