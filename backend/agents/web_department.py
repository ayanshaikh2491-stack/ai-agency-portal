"""
Web Department Agent System - 7 Specialized Agents
UI Designer, Frontend Developer, Backend Developer, API Manager,
3D/Effects Agent, QA Tester, Coordinator (Secretary)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

# Skills loaded from markdown
SKILLS_MD = """
## UI Design
- Color theory, typography, layout design
- Wireframing, prototyping, user flows
- Responsive design, mobile-first approach
- Tools: Figma, Adobe XD, Tailwind CSS

## Frontend Development
- React, Next.js, HTML5, CSS3, JavaScript/TypeScript
- Component architecture, state management
- Performance optimization, lazy loading
- Animation libraries, responsive design

## Backend Development
- FastAPI, Python, Node.js
- Database design (SQL, NoSQL)
- Authentication, authorization
- Server architecture, caching

## API Design
- RESTful API patterns, GraphQL
- Request/Response formatting
- Rate limiting, pagination
- API documentation, versioning

## 3D/Effects
- Three.js, CSS 3D transforms
- GSAP animations, scroll effects
- Particle systems, WebGL
- Performance-friendly animations

## QA Testing
- Unit testing, integration testing
- E2E testing with Playwright
- Performance testing, Lighthouse
- Bug tracking, reporting

## Coordination
- Task assignment, progress tracking
- Resource allocation, deadline management
- Communication between agents
- Quality gate enforcement
"""

# Tools registry
TOOLS_REGISTRY = {
    "code_generator": "Generate code for specific framework",
    "file_writer": "Create/update files with content",
    "code_review": "Review code for quality and issues",
    "design_system": "Generate design tokens and components",
    "api_tester": "Test API endpoints",
    "animation_builder": "Create CSS/JS animations",
    "performance_analyzer": "Analyze page performance",
    "bug_tracker": "Track and report bugs",
    "task_manager": "Assign and track tasks"
}


class WebAgent:
    """Base class for Web Department agents"""

    def __init__(self, name: str, role: str, skills: List[str],
                 tools: List[str], system_prompt: str, execution_steps: List[str]):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.department = "web"
        self.skills = skills
        self.tools = tools
        self.system_prompt = system_prompt
        self.execution_steps = execution_steps
        self.status = "active"
        self.task_history = []
        self.message_history = []
        self.workload = 0

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task following agent's execution steps"""
        self.status = "busy"
        self.workload += 1

        result = {
            "agent": self.name,
            "role": self.role,
            "task_id": task.get("id", str(uuid.uuid4())[:8]),
            "task_type": task.get("type", "general"),
            "steps_executed": [],
            "output": "",
            "status": "completed",
            "completed_at": datetime.utcnow().isoformat()
        }

        # Follow execution steps
        for step in self.execution_steps:
            result["steps_executed"].append(step)

        self.workload -= 1
        self.status = "active"
        self.task_history.append(result)
        return result

    def send_message(self, to: str, task: str, message_type: str = "task") -> Dict:
        """Send structured message to another agent"""
        msg = {
            "from": self.name,
            "to": to,
            "task": task,
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.message_history.append(msg)
        return msg

    def receive_message(self, msg: Dict) -> str:
        """Receive message from another agent"""
        self.message_history.append(msg)
        return f"[{self.name}] Received: {msg.get('task', '')[:50]}"

    def get_status(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "skills": self.skills,
            "tools": self.tools,
            "status": self.status,
            "workload": self.workload,
            "tasks_completed": len(self.task_history)
        }


# ============================================================
# WEB DEPARTMENT AGENTS
# ============================================================

def create_ui_designer() -> WebAgent:
    return WebAgent(
        name="Maya",
        role="UI Designer",
        skills=["color_theory", "typography", "layout_design", "wireframing", "prototyping", "responsive_design"],
        tools=["design_system", "figma_export", "tailwind_generator"],
        system_prompt="""You are Maya, UI Designer. You create beautiful, functional UI designs.
Follow these Web Interface Guidelines:
- Use semantic HTML elements appropriately
- Ensure accessibility: WCAG 2.1 AA compliance, proper contrast ratios (4.5:1 minimum)
- Design responsive layouts with mobile-first approach
- Use consistent spacing scale (4px, 8px, 12px, 16px, 24px, 32px)
- Limit font sizes: body 14-16px, headings scale proportionally
- Use CSS custom properties for design tokens
- Support dark mode with prefers-color-scheme
- Keep touch targets at least 44x44px
- Use relative units (rem, em) instead of fixed px
- Optimize images with proper alt attributes and loading="lazy"
When given a task:
1. Understand the design requirements
2. Create wireframes and layouts
3. Choose appropriate color palette and typography
4. Ensure responsive design for all breakpoints
5. Output: Clean design specifications with tokens""",
        execution_steps=[
            "Step 1: Analyze design requirements",
            "Step 2: Create wireframe structure",
            "Step 3: Define color palette and typography",
            "Step 4: Design layout with responsive breakpoints",
            "Step 5: Generate design tokens (colors, spacing, fonts)",
            "Step 6: Output complete UI spec"
        ]
    )


def create_frontend_developer() -> WebAgent:
    return WebAgent(
        name="Riya",
        role="Frontend Developer",
        skills=["react", "nextjs", "html5", "css3", "javascript", "typescript", "tailwind"],
        tools=["code_generator", "file_writer", "component_builder"],
        system_prompt="""You are Riya, Frontend Developer. You build clean, performant UI components.
Follow these Web Interface Guidelines:
- Write semantic HTML: use nav, main, article, section, aside appropriately
- Ensure accessibility: aria-labels, keyboard navigation, focus management, screen reader support
- Use CSS Grid and Flexbox for layouts, avoid floats
- Implement responsive design with mobile-first media queries
- Optimize performance: lazy load images, code split, minimize bundle size
- Use proper meta tags, OpenGraph, Twitter Cards for SEO
- Ensure Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
- Use proper heading hierarchy: h1 once, then h2, h3 in order
- Form accessibility: label elements, proper error messages, aria-invalid
- Color contrast: minimum 4.5:1 for text, 3:1 for UI elements
When given a task:
1. Read the design specs from UI Designer
2. Build semantic HTML structure
3. Style with CSS/Tailwind
4. Make it interactive with React
5. Ensure responsive and accessible
6. Output: Production-ready React components""",
        execution_steps=[
            "Step 1: Review design specs",
            "Step 2: Create component structure",
            "Step 3: Write semantic HTML/JSX",
            "Step 4: Add Tailwind CSS styling",
            "Step 5: Add interactivity and state",
            "Step 6: Make responsive and accessible",
            "Step 7: Output production-ready code"
        ]
    )


def create_backend_developer() -> WebAgent:
    return WebAgent(
        name="Aryan",
        role="Backend Developer",
        skills=["python", "fastapi", "nodejs", "sql", "database_design", "authentication"],
        tools=["code_generator", "file_writer", "database_builder"],
        system_prompt="""You are Aryan, Backend Developer. You build robust server-side logic.
When given a task:
1. Understand data requirements
2. Design database schema
3. Create API routes and handlers
4. Add authentication/authorization
5. Implement business logic
6. Output: Working FastAPI/Node.js backend code""",
        execution_steps=[
            "Step 1: Analyze data requirements",
            "Step 2: Design database schema",
            "Step 3: Create API routes and models",
            "Step 4: Add authentication middleware",
            "Step 5: Implement business logic",
            "Step 6: Add error handling and validation",
            "Step 7: Output working backend code"
        ]
    )


def create_api_manager() -> WebAgent:
    return WebAgent(
        name="Dev",
        role="API Manager",
        skills=["rest_api", "graphql", "api_documentation", "rate_limiting", "pagination"],
        tools=["api_tester", "doc_generator", "schema_validator"],
        system_prompt="""You are Dev, API Manager. You design, test, and document clean APIs.
When given a task:
1. Review API requirements
2. Design RESTful endpoints or GraphQL schema
3. Define request/response formats
4. Add validation and rate limiting
5. Generate API documentation
6. Test all endpoints
7. Output: API spec, docs, and test results""",
        execution_steps=[
            "Step 1: Review API requirements",
            "Step 2: Design endpoint structure",
            "Step 3: Define request/response schemas",
            "Step 4: Add validation and error handling",
            "Step 5: Set up rate limiting and pagination",
            "Step 6: Generate API documentation",
            "Step 7: Run API tests and report results"
        ]
    )


def create_3d_effects_agent() -> WebAgent:
    return WebAgent(
        name="Zara",
        role="3D/Effects Agent",
        skills=["threejs", "css_animations", "gsap", "webgl", "scroll_effects", "particles"],
        tools=["animation_builder", "threejs_generator", "performance_analyzer"],
        system_prompt="""You are Zara, 3D/Effects Agent. You create stunning visual effects and animations.
When given a task:
1. Understand the visual requirements
2. Choose appropriate animation technique
3. Implement the effect/animation
4. Optimize for performance
5. Ensure it works across breakpoints
6. Output: Ready-to-use animation code""",
        execution_steps=[
            "Step 1: Analyze visual requirements",
            "Step 2: Choose animation approach (CSS/GSAP/Three.js)",
            "Step 3: Build the animation/effect",
            "Step 4: Add scroll/interaction triggers",
            "Step 5: Optimize performance (60fps target)",
            "Step 6: Test responsive behavior",
            "Step 7: Output optimized animation code"
        ]
    )


def create_seo_agent() -> WebAgent:
    return WebAgent(
        name="Kavita",
        role="SEO Agent",
        skills=["keyword_research", "on_page_seo", "technical_seo", "link_building", "analytics", "content_optimization"],
        tools=["seo_analyzer", "keyword_finder", "site_auditor"],
        system_prompt="""You are Kavita, SEO Agent. You optimize websites for Google ranking.
When given a task:
1. Analyze current SEO status
2. Research keywords for the niche
3. Optimize meta tags, headings, content
4. Check technical SEO (speed, mobile, schema)
5. Suggest backlink strategy
6. Output: SEO report with actionable items""",
        execution_steps=[
            "Step 1: Analyze current SEO status",
            "Step 2: Research target keywords",
            "Step 3: Optimize on-page elements",
            "Step 4: Check technical SEO",
            "Step 5: Create backlink strategy",
            "Step 6: Generate SEO report"
        ]
    )


def create_performance_agent() -> WebAgent:
    return WebAgent(
        name="Vikram",
        role="Performance Agent",
        skills=["page_speed", "lighthouse", "core_web_vitals", "bundle_optimization", "caching", "cdn"],
        tools=["lighthouse", "speed_tester", "bundle_analyzer"],
        system_prompt="""You are Vikram, Performance Agent. You make websites blazing fast.
When given a task:
1. Run performance audit (Lighthouse)
2. Identify bottlenecks (large bundles, slow APIs)
3. Optimize images, code splitting, lazy loading
4. Set up caching and CDN strategies
5. Optimize Core Web Vitals (LCP, FID, CLS)
6. Output: Performance report with optimizations""",
        execution_steps=[
            "Step 1: Run Lighthouse audit",
            "Step 2: Identify performance bottlenecks",
            "Step 3: Optimize images and assets",
            "Step 4: Implement code splitting and lazy loading",
            "Step 5: Set up caching strategy",
            "Step 6: Optimize Core Web Vitals",
            "Step 7: Generate performance report"
        ]
    )


def create_qa_tester() -> WebAgent:
    return WebAgent(
        name="Kira",
        role="QA Tester",
        skills=["unit_testing", "e2e_testing", "performance_testing", "accessibility", "cross_browser"],
        tools=["bug_tracker", "performance_analyzer", "lighthouse", "playwright"],
        system_prompt="""You are Kira, QA Tester. You thoroughly test web applications.
When given a task:
1. Review what was built
2. Create test cases
3. Test functionality
4. Test responsiveness
5. Test performance
6. Check accessibility
7. Report all bugs with severity
8. Output: Test report with pass/fail""",
        execution_steps=[
            "Step 1: Review implementation",
            "Step 2: Create test plan",
            "Step 3: Test core functionality",
            "Step 4: Test responsiveness (mobile, tablet, desktop)",
            "Step 5: Run performance tests (Lighthouse)",
            "Step 6: Check accessibility (WCAG)",
            "Step 7: Document all bugs with severity",
            "Step 8: Generate test report"
        ]
    )


def create_coordinator() -> WebAgent:
    return WebAgent(
        name="Sara",
        role="Coordinator (Secretary)",
        skills=["task_management", "communication", "quality_gate", "progress_tracking"],
        tools=["task_manager", "progress_dashboard", "notification_system"],
        system_prompt="""You are Sara, Coordinator for the Web Department. You manage all tasks and agents.
Your job:
1. Receive incoming tasks
2. Analyze what needs to be done
3. Assign to the right agent in order: UI Designer → Frontend → Backend → 3D Effects → QA
4. Track progress of all agents
5. Prevent duplicate work
6. Combine outputs from all agents
7. Report final status
8. Always communicate clearly in Hinglish""",
        execution_steps=[
            "Step 1: Receive and analyze task",
            "Step 2: Determine which agents are needed",
            "Step 3: Assign tasks in correct order",
            "Step 4: Monitor progress of each agent",
            "Step 5: Handle any blockers or issues",
            "Step 6: Collect and combine all outputs",
            "Step 7: Run QA review",
            "Step 8: Deliver final result"
        ]
    )


# ============================================================
# WEB DEPARTMENT CLASS
# ============================================================

class WebDepartment:
    """Web Department with all 7 agents"""

    def __init__(self):
        self.agents = {
            "ui_designer": create_ui_designer(),
            "frontend_developer": create_frontend_developer(),
            "backend_developer": create_backend_developer(),
            "api_manager": create_api_manager(),
            "seo": create_seo_agent(),
            "performance": create_performance_agent(),
            "qa_tester": create_qa_tester(),
            "coordinator": create_coordinator()
        }
        self.task_queue = []
        self.completed_tasks = []
        self.message_log = []

    def get_all_agents(self) -> List[Dict]:
        """Get all agents with their status"""
        return [agent.get_status() for agent in self.agents.values()]

    def get_agent(self, agent_key: str) -> Optional[WebAgent]:
        """Get a specific agent"""
        return self.agents.get(agent_key)

    def assign_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinator assigns and routes tasks"""
        coordinator = self.agents["coordinator"]
        result = coordinator.execute_task(task)
        self.task_queue.append({"task": task, "status": "assigned"})
        return result

    def send_message(self, from_agent: str, to_agent: str, task: str) -> Dict:
        """Send message between agents"""
        if from_agent in self.agents and to_agent in self.agents:
            msg = self.agents[from_agent].send_message(to_agent, task)
            response = self.agents[to_agent].receive_message(msg)
            self.message_log.append({"message": msg, "response": response})
            return {"sent": msg, "received": response}
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