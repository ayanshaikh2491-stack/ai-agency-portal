"""
Workflow Engine - Manages task pipelines
Tasks flow through defined steps: Backend -> Testing -> Frontend -> Deployment
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep:
    """A single step in a workflow"""
    
    def __init__(self, name: str, department: str, action: str, 
                 description: str = "", depends_on: List[str] = None,
                 timeout: int = 300):
        self.name = name
        self.department = department
        self.action = action
        self.description = description
        self.depends_on = depends_on or []
        self.timeout = timeout
        self.status = StepStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "department": self.department,
            "action": self.action,
            "description": self.description,
            "depends_on": self.depends_on,
            "timeout": self.timeout,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class WorkflowInstance:
    """A running instance of a workflow"""
    
    def __init__(self, workflow_id: str, name: str, steps: List[WorkflowStep],
                 input_data: Dict = None):
        self.id = workflow_id
        self.name = name
        self.steps = steps
        self.input_data = input_data or {}
        self.output_data = {}
        self.status = WorkflowStatus.PENDING
        self.current_step = 0
        self.started_at = None
        self.completed_at = None
        self.error = None
    
    def get_next_step(self) -> Optional[WorkflowStep]:
        """Get the next step that can be executed"""
        for i, step in enumerate(self.steps):
            if step.status == StepStatus.PENDING:
                # Check if dependencies are met
                deps_met = all(
                    self.steps[j].status == StepStatus.COMPLETED
                    for j, s in enumerate(self.steps)
                    if s.name in step.depends_on
                )
                if deps_met:
                    return step
        return None
    
    def get_step_by_name(self, name: str) -> Optional[WorkflowStep]:
        """Get a step by name"""
        for step in self.steps:
            if step.name == name:
                return step
        return None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "current_step": self.current_step,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "steps": [s.to_dict() for s in self.steps],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class WorkflowEngine:
    """
    Manages workflow definitions and executions.
    Supports multi-department workflows with step dependencies.
    """
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowInstance] = {}
        self.workflow_counter = 0
        self.step_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, action: str, handler: Callable):
        """Register a handler function for a step action"""
        self.step_handlers[action] = handler
    
    def create_workflow(self, name: str, steps: List[Dict], 
                        input_data: Dict = None) -> WorkflowInstance:
        """Create a new workflow from step definitions"""
        self.workflow_counter += 1
        workflow_id = f"WF-{self.workflow_counter:04d}"
        
        workflow_steps = []
        for step_def in steps:
            step = WorkflowStep(
                name=step_def["name"],
                department=step_def["department"],
                action=step_def["action"],
                description=step_def.get("description", ""),
                depends_on=step_def.get("depends_on", []),
                timeout=step_def.get("timeout", 300)
            )
            workflow_steps.append(step)
        
        workflow = WorkflowInstance(
            workflow_id=workflow_id,
            name=name,
            steps=workflow_steps,
            input_data=input_data or {}
        )
        
        self.workflows[workflow_id] = workflow
        return workflow
    
    def start_workflow(self, workflow_id: str) -> Dict:
        """Start a workflow"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        
        return {
            "status": "started",
            "workflow": workflow.to_dict()
        }
    
    def execute_next_step(self, workflow_id: str, handler_result: Dict = None) -> Dict:
        """Execute the next available step in a workflow"""
        if workflow_id not in self.workflows:
            return {"error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.RUNNING:
            return {"error": f"Workflow is {workflow.status.value}"}
        
        step = workflow.get_next_step()
        if not step:
            # Check if all steps are completed
            if all(s.status == StepStatus.COMPLETED for s in workflow.steps):
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.utcnow()
                return {
                    "status": "completed",
                    "workflow": workflow.to_dict()
                }
            return {"status": "no_steps_available", "workflow": workflow.to_dict()}
        
        # Execute the step
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()
        workflow.current_step = workflow.steps.index(step)
        
        # Call the handler if registered
        if step.action in self.step_handlers:
            try:
                result = self.step_handlers[step.action](
                    step=step.to_dict(),
                    input_data=workflow.input_data,
                    previous_results=workflow.output_data
                )
                step.result = result
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.utcnow()
                workflow.output_data[step.name] = result
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                workflow.error = str(e)
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = datetime.utcnow()
                return {
                    "status": "step_failed",
                    "step": step.to_dict(),
                    "error": str(e)
                }
        else:
            # No handler, mark as completed
            step.result = {"message": f"Step '{step.name}' completed (no handler)"}
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            workflow.output_data[step.name] = step.result
        
        return {
            "status": "step_executed",
            "step": step.to_dict(),
            "workflow": workflow.to_dict()
        }
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow status"""
        workflow = self.workflows.get(workflow_id)
        return workflow.to_dict() if workflow else None
    
    def get_all_workflows(self) -> List[Dict]:
        """Get all workflows"""
        return [w.to_dict() for w in self.workflows.values()]
    
    def pause_workflow(self, workflow_id: str) -> Dict:
        """Pause a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        workflow.status = WorkflowStatus.PAUSED
        return {"status": "paused", "workflow": workflow.to_dict()}
    
    def resume_workflow(self, workflow_id: str) -> Dict:
        """Resume a paused workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        if workflow.status != WorkflowStatus.PAUSED:
            return {"error": f"Workflow is {workflow.status.value}, cannot resume"}
        
        workflow.status = WorkflowStatus.RUNNING
        return {"status": "resumed", "workflow": workflow.to_dict()}


# Predefined workflow templates
WORKFLOW_TEMPLATES = {
    "backend_to_frontend": {
        "name": "Backend to Frontend Pipeline",
        "steps": [
            {
                "name": "api_development",
                "department": "backend",
                "action": "develop_api",
                "description": "Develop the API endpoint"
            },
            {
                "name": "api_testing",
                "department": "qa",
                "action": "test_api",
                "description": "Test the API endpoint",
                "depends_on": ["api_development"]
            },
            {
                "name": "frontend_integration",
                "department": "frontend",
                "action": "integrate_frontend",
                "description": "Integrate API with frontend",
                "depends_on": ["api_testing"]
            },
            {
                "name": "e2e_testing",
                "department": "qa",
                "action": "test_e2e",
                "description": "End-to-end testing",
                "depends_on": ["frontend_integration"]
            },
            {
                "name": "deployment",
                "department": "website",
                "action": "deploy",
                "description": "Deploy to production",
                "depends_on": ["e2e_testing"]
            }
        ]
    },
    "feature_development": {
        "name": "Feature Development Pipeline",
        "steps": [
            {
                "name": "requirements",
                "department": "website",
                "action": "gather_requirements",
                "description": "Gather feature requirements"
            },
            {
                "name": "design",
                "department": "website",
                "action": "create_design",
                "description": "Create UI/UX design",
                "depends_on": ["requirements"]
            },
            {
                "name": "backend_dev",
                "department": "backend",
                "action": "develop_backend",
                "description": "Develop backend logic",
                "depends_on": ["design"]
            },
            {
                "name": "frontend_dev",
                "department": "frontend",
                "action": "develop_frontend",
                "description": "Develop frontend UI",
                "depends_on": ["design"]
            },
            {
                "name": "integration",
                "department": "backend",
                "action": "integrate",
                "description": "Integrate backend and frontend",
                "depends_on": ["backend_dev", "frontend_dev"]
            },
            {
                "name": "testing",
                "department": "qa",
                "action": "test_feature",
                "description": "Test the complete feature",
                "depends_on": ["integration"]
            }
        ]
    }
}