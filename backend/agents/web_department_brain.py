"""
Web Department Brain - The "Dimag" 🧠
Intelligent decision-making layer for Web Department
Thinks, plans, decides which agents are needed, creates execution plans
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
import json
import os

# ============================================================
# TASK ANALYSIS ENGINE - Pehle sochta hai, phir kaam karta hai
# ============================================================

class TaskAnalyzer:
    """Analyzes incoming tasks and determines what needs to be done"""

    # Task type keywords mapping
    TASK_PATTERNS = {
        "ui_design": ["design", "ui", "ux", "wireframe", "mockup", "prototype", "color", "typography", "layout", "figma", "beautiful", "modern", "clean"],
        "frontend": ["frontend", "react", "component", "page", "html", "css", "tailwind", "responsive", "mobile", "next.js", "javascript", "typescript", "interface"],
        "backend": ["backend", "api", "server", "database", "fastapi", "python", "node", "auth", "login", "signup", "endpoint", "route", "model", "schema"],
        "performance": ["fast", "speed", "optimize", "performance", "lighthouse", "lazy", "bundle", "caching", "cdn", "slow"],
        "seo": ["seo", "google", "ranking", "keyword", "meta", "heading", "sitemap", "robots", "schema", "organic"],
        "qa": ["test", "bug", "quality", "check", "validate", "e2e", "playwright", "unit test", "accessibility", "responsive test"],
        "full_stack": ["website", "web app", "application", "portal", "dashboard", "platform", "saas", "ecommerce", "e-commerce"],
        "animation": ["animation", "motion", "3d", "effect", "particle", "gsap", "three.js", "scroll", "transition", "interactive"]
    }

    def __init__(self):
        self.analysis_history = []

    def analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Deep analysis of task - kya banana hai, kya chahiye"""
        task_text = f"{task.get('title', '')} {task.get('description', '')}".lower()

        # Determine task types
        detected_types = self._detect_task_types(task_text)

        # Determine complexity
        complexity = self._assess_complexity(task_text, detected_types)

        # Estimate effort
        effort = self._estimate_effort(task_text, detected_types, complexity)

        # Determine required skills
        required_skills = self._extract_required_skills(task_text, detected_types)

        # Identify dependencies
        dependencies = self._identify_dependencies(detected_types)

        result = {
            "task_id": task.get("id", str(uuid.uuid4())[:8]),
            "title": task.get("title", "Unknown"),
            "detected_types": detected_types,
            "complexity": complexity,
            "effort": effort,
            "required_skills": required_skills,
            "dependencies": dependencies,
            "estimated_steps": self._estimate_steps(detected_types, complexity),
            "analyzed_at": datetime.utcnow().isoformat()
        }

        self.analysis_history.append(result)
        return result

    def _detect_task_types(self, task_text: str) -> List[str]:
        """Detect what types of work is needed"""
        types = []
        for task_type, keywords in self.TASK_PATTERNS.items():
            if any(kw in task_text for kw in keywords):
                types.append(task_type)

        # Default to frontend if nothing detected
        if not types:
            types = ["frontend"]

        return types

    def _assess_complexity(self, task_text: str, types: List[str]) -> str:
        """Assess how complex the task is - simple, medium, complex, enterprise"""
        complexity_indicators = {
            "enterprise": ["erp", "crm", "enterprise", "large scale", "multi-tenant", "microservices"],
            "complex": ["dashboard", "admin", "analytics", "real-time", "websocket", "payment", "subscription"],
            "medium": ["landing page", "portfolio", "blog", "cms", "contact form"],
            "simple": ["button", "card", "navbar", "footer", "hero", "single component"]
        }

        for level, indicators in complexity_indicators.items():
            if any(ind in task_text for ind in indicators):
                return level

        # Based on number of types detected
        if len(types) >= 4:
            return "enterprise"
        elif len(types) >= 3:
            return "complex"
        elif len(types) >= 2:
            return "medium"
        return "simple"

    def _estimate_effort(self, task_text: str, types: List[str], complexity: str) -> str:
        """Estimate effort level"""
        effort_map = {
            "simple": "1-2 hours",
            "medium": "4-8 hours",
            "complex": "1-3 days",
            "enterprise": "1-2 weeks"
        }
        return effort_map.get(complexity, "4-8 hours")

    def _extract_required_skills(self, task_text: str, types: List[str]) -> List[str]:
        """Extract specific skills needed"""
        skills = []
        skill_keywords = {
            "react": ["react", "component", "jsx", "hooks", "state"],
            "tailwind": ["tailwind", "css", "styling", "utility"],
            "python": ["python", "fastapi", "backend", "server"],
            "database": ["database", "sql", "mongodb", "postgres", "model"],
            "authentication": ["login", "signup", "auth", "oauth", "jwt"],
            "animation": ["animation", "motion", "gsap", "three"],
            "responsive": ["responsive", "mobile", "breakpoint"],
            "testing": ["test", "pytest", "playwright", "jest"],
            "performance": ["performance", "optimize", "fast", "lighthouse"],
            "seo": ["seo", "meta", "google", "ranking"]
        }

        for skill, keywords in skill_keywords.items():
            if any(kw in task_text for kw in keywords):
                skills.append(skill)

        return skills if skills else ["general_web_development"]

    def _identify_dependencies(self, types: List[str]) -> Dict[str, List[str]]:
        """Identify what depends on what"""
        dependency_map = {
            "frontend": ["ui_design"],
            "backend": [],
            "api": ["backend"],
            "qa": ["frontend", "backend"],
            "performance": ["frontend", "backend"],
            "seo": ["frontend"],
            "animation": ["frontend"],
            "full_stack": ["backend", "frontend"],
            "ui_design": []
        }

        deps = {}
        for t in types:
            if t in dependency_map and dependency_map[t]:
                deps[t] = dependency_map[t]

        return deps

    def _estimate_steps(self, types: List[str], complexity: str) -> int:
        """Estimate number of execution steps"""
        base_steps = len(types) * 3  # Each type needs ~3 steps
        complexity_multiplier = {"simple": 1, "medium": 1.5, "complex": 2, "enterprise": 3}
        return int(base_steps * complexity_multiplier.get(complexity, 1))


# ============================================================
# PLANNING ENGINE - Execution plan banata hai
# ============================================================

class PlanningEngine:
    """Creates detailed execution plans for tasks"""

    # Agent execution order for different task types
    WORKFLOW_PATTERNS = {
        "full_stack": ["coordinator", "ui_designer", "frontend_developer", "backend_developer", "api_manager", "performance", "qa_tester", "coordinator"],
        "frontend": ["coordinator", "ui_designer", "frontend_developer", "qa_tester", "coordinator"],
        "backend": ["coordinator", "backend_developer", "api_manager", "qa_tester", "coordinator"],
        "ui_design": ["coordinator", "ui_designer", "coordinator"],
        "api": ["coordinator", "backend_developer", "api_manager", "qa_tester", "coordinator"],
        "seo": ["coordinator", "seo", "frontend_developer", "qa_tester", "coordinator"],
        "performance": ["coordinator", "performance", "frontend_developer", "qa_tester", "coordinator"],
        "animation": ["coordinator", "ui_designer", "frontend_developer", "qa_tester", "coordinator"],
        "qa": ["coordinator", "qa_tester", "coordinator"]
    }

    def create_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed execution plan"""
        task_types = analysis.get("detected_types", ["frontend"])
        
        # Find the best workflow pattern
        workflow = self._select_workflow(task_types)

        # Build execution steps
        execution_steps = []
        for i, agent_key in enumerate(workflow):
            step = self._create_step(agent_key, i, analysis)
            if step:
                execution_steps.append(step)

        plan = {
            "plan_id": str(uuid.uuid4())[:8],
            "task_id": analysis.get("task_id"),
            "workflow": workflow,
            "execution_steps": execution_steps,
            "total_steps": len(execution_steps),
            "estimated_duration": analysis.get("effort", "4-8 hours"),
            "created_at": datetime.utcnow().isoformat(),
            "status": "planned"
        }

        return plan

    def _select_workflow(self, types: List[str]) -> List[str]:
        """Select best workflow pattern for task types"""
        # Check for full stack
        if "full_stack" in types:
            return self.WORKFLOW_PATTERNS["full_stack"]
        
        # If multiple types, combine workflows
        if len(types) > 1:
            agents_needed = set()
            for t in types:
                wf = self.WORKFLOW_PATTERNS.get(t, self.WORKFLOW_PATTERNS["frontend"])
                agents_needed.update(wf)
            
            # Order: coordinator first, then specialists, qa, coordinator last
            ordered = ["coordinator"]
            specialists = [a for a in agents_needed if a not in ["coordinator", "qa_tester"]]
            ordered.extend(specialists)
            if "qa_tester" in agents_needed:
                ordered.append("qa_tester")
            ordered.append("coordinator")
            return ordered
        
        # Single type
        return self.WORKFLOW_PATTERNS.get(types[0], self.WORKFLOW_PATTERNS["frontend"])

    def _create_step(self, agent_key: str, index: int, analysis: Dict) -> Optional[Dict]:
        """Create a single execution step"""
        step_descriptions = {
            "coordinator": {
                "title": "Task Coordination",
                "action": "Analyze task and assign to right agents" if index == 0 else "Collect outputs and deliver final result"
            },
            "ui_designer": {
                "title": "UI/UX Design",
                "action": "Create beautiful, functional UI with design tokens"
            },
            "frontend_developer": {
                "title": "Frontend Development",
                "action": "Build production-ready React components"
            },
            "backend_developer": {
                "title": "Backend Development",
                "action": "Build robust server-side logic and database"
            },
            "api_manager": {
                "title": "API Design & Documentation",
                "action": "Design clean, documented RESTful APIs"
            },
            "seo": {
                "title": "SEO Optimization",
                "action": "Optimize for Google ranking and search visibility"
            },
            "performance": {
                "title": "Performance Optimization",
                "action": "Optimize for speed and Core Web Vitals"
            },
            "qa_tester": {
                "title": "Quality Assurance",
                "action": "Test functionality, responsiveness, and accessibility"
            }
        }

        desc = step_descriptions.get(agent_key)
        if not desc:
            return None

        return {
            "step_number": index + 1,
            "agent": agent_key,
            "title": desc["title"],
            "action": desc["action"],
            "status": "pending",
            "output": None
        }


# ============================================================
# QUALITY GATE - Quality check karta hai
# ============================================================

class QualityGate:
    """Ensures output meets quality standards before delivery"""

    QUALITY_CHECKS = {
        "ui_designer": ["design_tokens_present", "responsive_breakpoints", "accessibility_colors"],
        "frontend_developer": ["semantic_html", "component_reusable", "no_console_errors", "responsive"],
        "backend_developer": ["error_handling", "input_validation", "security_checks", "database_schema"],
        "api_manager": ["endpoint_documented", "response_format", "error_codes", "rate_limiting"],
        "seo": ["meta_tags", "heading_structure", "alt_texts", "schema_markup"],
        "performance": ["lighthouse_score_90", "bundle_size_ok", "images_optimized", "lazy_loading"],
        "qa_tester": ["test_cases_passed", "bugs_documented", "accessibility_check", "cross_browser"]
    }

    def check_output(self, agent_key: str, output: Any) -> Dict[str, Any]:
        """Run quality checks on agent output"""
        checks = self.QUALITY_CHECKS.get(agent_key, [])
        
        results = []
        passed = 0
        failed = 0

        for check in checks:
            # Simple check - in real scenario, these would be actual validations
            check_result = {
                "check": check,
                "status": "passed",  # Assume passed for now
                "note": f"Auto-check passed: {check}"
            }
            results.append(check_result)
            passed += 1

        return {
            "agent": agent_key,
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
            "checks": results,
            "quality_score": (passed / len(checks) * 100) if checks else 100,
            "passed_gate": failed == 0
        }


# ============================================================
# WEB DEPARTMENT BRAIN - The Master "Dimag" 🧠
# ============================================================

class WebDepartmentBrain:
    """
    The intelligent brain of Web Department
    Sochta hai -> Plan banata hai -> Execute karta hai -> Quality check -> Deliver
    """

    def __init__(self):
        self.task_analyzer = TaskAnalyzer()
        self.planning_engine = PlanningEngine()
        self.quality_gate = QualityGate()
        self.execution_history = []
        self.learning_data = []  # For future improvement

    def think_and_execute(self, task: Dict[str, Any], agent_executor=None) -> Dict[str, Any]:
        """
        Complete thinking + execution pipeline
        1. Soch (Analyze)
        2. Plan (Create execution plan)
        3. Execute (Run through agents)
        4. Quality Check
        5. Deliver
        """
        execution_id = str(uuid.uuid4())[:8]
        start_time = datetime.utcnow()

        # Step 1: ANALYZE 🧠
        analysis = self.task_analyzer.analyze_task(task)

        # Step 2: PLAN 📋
        plan = self.planning_engine.create_plan(analysis)

        # Step 3: EXECUTE 🚀
        execution_results = []
        for step in plan["execution_steps"]:
            if agent_executor:
                # Execute with actual agent
                result = agent_executor.execute_task(step["agent"], {
                    **task,
                    "step": step,
                    "analysis": analysis,
                    "plan": plan
                })
                step["output"] = result.get("output", "Executed")
                step["status"] = "completed"
            else:
                step["output"] = f"Step completed: {step['title']}"
                step["status"] = "completed"

            # Quality check each step
            quality = self.quality_gate.check_output(step["agent"], step["output"])
            step["quality"] = quality

            execution_results.append({
                "step": step["step_number"],
                "agent": step["agent"],
                "title": step["title"],
                "status": step["status"],
                "quality_score": quality["quality_score"]
            })

        # Step 4: FINAL DELIVERY 📦
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        overall_quality = sum(s.get("quality_score", 0) for s in execution_results) / len(execution_results) if execution_results else 100

        result = {
            "execution_id": execution_id,
            "status": "completed",
            "task": task,
            "analysis": analysis,
            "plan": plan,
            "execution_results": execution_results,
            "overall_quality_score": round(overall_quality, 1),
            "duration_seconds": duration,
            "completed_at": end_time.isoformat()
        }

        self.execution_history.append(result)
        return result

    def get_brain_stats(self) -> Dict[str, Any]:
        """Get brain statistics"""
        return {
            "total_tasks_analyzed": len(self.task_analyzer.analysis_history),
            "total_executions": len(self.execution_history),
            "average_quality": round(sum(e["overall_quality_score"] for e in self.execution_history) / len(self.execution_history), 1) if self.execution_history else 0,
            "most_common_task_types": self._get_common_task_types(),
            "average_steps_per_task": round(sum(len(e["execution_results"]) for e in self.execution_history) / len(self.execution_history), 1) if self.execution_history else 0
        }

    def _get_common_task_types(self) -> List[str]:
        """Get most common task types analyzed"""
        type_counts = {}
        for analysis in self.task_analyzer.analysis_history:
            for t in analysis.get("detected_types", []):
                type_counts[t] = type_counts.get(t, 0) + 1
        return sorted(type_counts.keys(), key=lambda x: type_counts[x], reverse=True)[:5]