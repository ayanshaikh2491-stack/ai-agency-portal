"""
Test Script for AI Agency Portal
Tests all systems: agents, communication, workflows, memory
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents.base import BaseAgent
from agents.ceo import CEOAgent
from agents.department_agents import (
    BackendDeveloperAgent, FrontendDeveloperAgent,
    WebsiteDeveloperAgent, QAAgent, MarketingAgent, DesignerAgent,
    DevOpsAgent, ProductManagerAgent, DataScientistAgent, SecurityAgent, HRAgent
)
from communication.chat import MessageBoard, AgentChat, IssueTracker
from workflows.engine import WorkflowEngine, WORKFLOW_TEMPLATES
from database.memory import MemoryStore, SharedKnowledge


def test_agents():
    print("=" * 60)
    print("TESTING AGENTS")
    print("=" * 60)
    
    # Create CEO
    ceo = CEOAgent(name="Atlas")
    print(f"[OK] CEO created: {ceo.name}")
    
    # Create all department leads
    backend_lead = BackendDeveloperAgent(name="Ravi")
    frontend_lead = FrontendDeveloperAgent(name="Priya")
    website_lead = WebsiteDeveloperAgent(name="Amit")
    qa_lead = QAAgent(name="Sneha")
    marketing_lead = MarketingAgent(name="Kavita")
    designer = DesignerAgent(name="Rohan")
    devops_lead = DevOpsAgent(name="Vikram")
    product_lead = ProductManagerAgent(name="Neha")
    data_lead = DataScientistAgent(name="Arjun")
    security_lead = SecurityAgent(name="Deepak")
    hr_lead = HRAgent(name="Pooja")
    
    # Register all departments
    ceo.register_department("backend", backend_lead)
    ceo.register_department("frontend", frontend_lead)
    ceo.register_department("website", website_lead)
    ceo.register_department("qa", qa_lead)
    ceo.register_department("marketing", marketing_lead)
    ceo.register_department("devops", devops_lead)
    ceo.register_department("product", product_lead)
    ceo.register_department("data", data_lead)
    ceo.register_department("security", security_lead)
    ceo.register_department("hr", hr_lead)
    
    # Register additional agents
    ceo.register_agent(designer, "website")
    
    print(f"[OK] Departments registered: {list(ceo.departments.keys())}")
    print(f"[OK] Total agents: {len(ceo.agents)}")
    
    # Test agent memory
    backend_lead.store_memory("api_pattern", {"endpoint": "/api/users", "method": "GET"}, "skill", 3)
    recalled = backend_lead.recall_memory("api_pattern")
    print(f"[OK] Memory stored and recalled: {recalled}")
    
    # Test agent task execution
    task = {"id": "1", "title": "Create API", "description": "Create a user API endpoint", "type": "api_endpoint", "input_data": {"endpoint": "/api/users", "method": "POST"}}
    result = backend_lead.execute_task(task)
    print(f"[OK] Task executed: {result['status']}")
    
    # Test DevOps agent
    deploy_task = {"id": "2", "title": "Deploy App", "description": "Deploy to production", "type": "deploy", "input_data": {"environment": "production"}}
    deploy_result = devops_lead.execute_task(deploy_task)
    print(f"[OK] DevOps deploy: {deploy_result['status']}")
    
    # Test Security agent
    security_task = {"id": "3", "title": "Security Audit", "description": "Audit the API", "type": "security_audit"}
    security_result = security_lead.execute_task(security_task)
    print(f"[OK] Security audit: {security_result['status']}")
    
    # Test HR agent
    hr_task = {"id": "4", "title": "Onboard Agent", "description": "Onboard new agent", "type": "onboard", "input_data": {"agent_name": "NewBot"}}
    hr_result = hr_lead.execute_task(hr_task)
    print(f"[OK] HR onboarding: {hr_result['status']}")
    
    # Test agent status
    status = backend_lead.get_status()
    print(f"[OK] Agent status: {status['name']} - {status['status']}")
    
    return ceo


def test_communication(ceo):
    print("\n" + "=" * 60)
    print("TESTING COMMUNICATION")
    print("=" * 60)
    
    # Message board
    board = MessageBoard()
    board.create_channel("general", "General chat")
    board.create_channel("backend", "Backend team")
    board.create_channel("devops", "DevOps team")
    board.create_channel("security", "Security team")
    
    # Post message
    msg = board.post_message(
        channel="general",
        sender_id=ceo.id,
        sender_name=ceo.name,
        content="Welcome to the AI Agency! Let's build great things.",
        subject="Welcome Message"
    )
    print(f"[OK] Message posted: {msg['id']}")
    
    # Get messages
    messages = board.get_channel_messages("general")
    print(f"[OK] Messages in channel: {len(messages)}")
    
    # Direct chat
    chat = AgentChat()
    dm = chat.send_message(
        from_id="agent1", from_name="Ravi",
        to_id="agent2", to_name="Priya",
        content="Hey, need help with the API integration?"
    )
    print(f"[OK] Direct message sent")
    
    # Issue tracker
    tracker = IssueTracker()
    issue = tracker.create_issue(
        title="API returning 500 error",
        description="The /api/users endpoint is failing",
        reported_by="agent1",
        reported_by_name="Ravi",
        severity="high",
        department="backend"
    )
    print(f"[OK] Issue created: {issue['id']}")
    
    # Add comment
    comment = tracker.add_comment(
        issue_id=issue['id'],
        agent_id="agent2",
        agent_name="Priya",
        content="I'll look into this. Might be a database connection issue."
    )
    print(f"[OK] Comment added to issue")
    
    return board, chat, tracker


def test_workflows():
    print("\n" + "=" * 60)
    print("TESTING WORKFLOWS")
    print("=" * 60)
    
    engine = WorkflowEngine()
    
    # Create workflow from template
    template = WORKFLOW_TEMPLATES["backend_to_frontend"]
    workflow = engine.create_workflow(
        name="User API Pipeline",
        steps=template["steps"],
        input_data={"endpoint": "/api/users"}
    )
    print(f"[OK] Workflow created: {workflow.id}")
    
    # Start workflow
    result = engine.start_workflow(workflow.id)
    print(f"[OK] Workflow started: {result['status']}")
    
    # Execute steps
    step_count = 0
    while True:
        result = engine.execute_next_step(workflow.id)
        if result.get("status") in ["completed", "no_steps_available"]:
            break
        step_count += 1
        print(f"  Step {step_count} executed: {result.get('step', {}).get('name', 'unknown')}")
    
    print(f"[OK] Workflow completed: {step_count} steps executed")
    
    # Get workflow status
    wf_status = engine.get_workflow(workflow.id)
    print(f"[OK] Final status: {wf_status['status']}")
    
    return engine


def test_memory():
    print("\n" + "=" * 60)
    print("TESTING MEMORY SYSTEM")
    print("=" * 60)
    
    # Memory store
    mem = MemoryStore(storage_path="test_data/memory")
    
    # Store memory
    result = mem.store(
        agent_id="agent1",
        key="best_practice",
        value={"tip": "Always validate input data"},
        memory_type="learning",
        importance=4
    )
    print(f"[OK] Memory stored: best_practice")
    
    # Recall memory
    recalled = mem.recall("agent1", "best_practice")
    print(f"[OK] Memory recalled: {recalled}")
    
    # Search memory
    results = mem.search("agent1", query="validate")
    print(f"[OK] Memory search results: {len(results)}")
    
    # Stats
    stats = mem.get_stats("agent1")
    print(f"[OK] Memory stats: {stats}")
    
    # Shared knowledge
    kb = SharedKnowledge(storage_path="test_data/knowledge")
    
    kb.add(
        key="api_guidelines",
        content="Always use proper error handling and validation",
        category="backend",
        tags=["api", "best-practices"]
    )
    print(f"[OK] Knowledge added")
    
    # Search knowledge
    kb_results = kb.search(query="error")
    print(f"[OK] Knowledge search results: {len(kb_results)}")
    
    return mem, kb


def test_ceo_task_management(ceo):
    print("\n" + "=" * 60)
    print("TESTING CEO TASK MANAGEMENT")
    print("=" * 60)
    
    # Create and assign task
    result = ceo.assign_and_execute(
        title="Build User API",
        description="Create REST API for user management",
        department="backend",
        priority=3
    )
    print(f"[OK] Task assigned and executed: {result.get('status')}")
    
    # Test DevOps task
    devops_result = ceo.assign_and_execute(
        title="Deploy to Production",
        description="Deploy the application",
        department="devops",
        priority=4
    )
    print(f"[OK] DevOps task: {devops_result.get('status')}")
    
    # Test Security task
    security_result = ceo.assign_and_execute(
        title="Security Audit",
        description="Audit the application",
        department="security",
        priority=5
    )
    print(f"[OK] Security task: {security_result.get('status')}")
    
    # Monitor progress
    report = ceo.monitor_progress()
    print(f"[OK] Progress report: {report['active_tasks']} active, {report['completed_tasks']} completed")
    
    # Broadcast message
    broadcast = ceo.broadcast_message(
        content="Great work everyone! Let's keep up the momentum.",
        subject="Team Update"
    )
    print(f"[OK] Broadcast sent to {len(broadcast.get('responses', {}))} agents")
    
    return report


def run_all_tests():
    print("\n" + "=" * 60)
    print("AI AGENCY PORTAL - FULL SYSTEM TEST")
    print("=" * 60 + "\n")
    
    try:
        # Test agents
        ceo = test_agents()
        
        # Test communication
        board, chat, tracker = test_communication(ceo)
        
        # Test workflows
        engine = test_workflows()
        
        # Test memory
        mem, kb = test_memory()
        
        # Test CEO task management
        report = test_ceo_task_management(ceo)
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
        print(f"""
Final Summary:
   - Agents: {len(ceo.agents)} registered
   - Departments: {len(ceo.departments)} active
   - Tasks Completed: {report['completed_tasks']}
   - Workflows: {len(engine.workflows)} created
   - Messages: {len(board.messages)} posted
   - Issues: {len(tracker.issues)} tracked
   - Memories: {mem.get_stats('agent1')['total']} stored
   - Knowledge: {len(kb.knowledge)} entries

Agency Structure:
   CEO: {ceo.name}
   Departments: {', '.join(ceo.departments.keys())}
   
Communication Channels:
   {', '.join(board.get_all_channels())}

Workflow Templates:
   {', '.join(WORKFLOW_TEMPLATES.keys())}
""")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)