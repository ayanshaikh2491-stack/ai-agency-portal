"""Test the Web Department Brain"""
from agents.web_department_brain import WebDepartmentBrain

brain = WebDepartmentBrain()
print("Web Department Brain initialized!")
print("Brain stats:", brain.get_brain_stats())

# Test task analysis
task = {
    "id": "test_001",
    "title": "Build a landing page",
    "description": "Create a responsive landing page with hero section, features, and contact form"
}
analysis = brain.task_analyzer.analyze_task(task)
print("\nTask analysis:", analysis)

plan = brain.planning_engine.create_plan(analysis)
print("\nExecution plan:", plan)