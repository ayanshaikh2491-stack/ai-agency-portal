"""AI Agency Portal v6.0 - Structured AI Agency System"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx, os, json, asyncio, uuid
from dotenv import load_dotenv
load_dotenv()

# Import structured systems
import sys
sys.path.insert(0, os.path.dirname(__file__))
from communication.structured import CommunicationHub, MessageType, MessagePriority
from agents.department_manager import DepartmentManager
from agents.agent_system import AgentExecutor
from departments.web.web_department import WebDepartment as NewWebDepartment

# Initialize Web Department with individual agent files
web_dept = NewWebDepartment()

app = FastAPI(title="AI Agency Portal v6.0", version="6.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Config ---
API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MEM = os.path.join(os.path.dirname(__file__), "memory")
os.makedirs(MEM, exist_ok=True)
SETTINGS = os.path.join(os.path.dirname(__file__), "settings.json")

# --- Initialize Systems ---
comm_hub = CommunicationHub()
agent_executor = AgentExecutor()

# Department definitions
DEPT_CONFIG = {
    "web": {"lead": "Sara", "agents": ["Maya", "Riya", "Aryan", "Dev", "Kavita", "Vikram", "Kira", "Sara"], "skills": ["web_development", "frontend", "backend", "seo", "performance", "qa"], "desc": "Full website development with 8 specialized agents"},
    "seo": {"lead": "Kavita", "agents": ["Kavita", "Arjun"], "skills": ["seo", "analytics", "content_writing"], "desc": "SEO tracking Google ranking, traffic analysis, growth"},
    "marketing": {"lead": "Neha", "agents": ["Neha", "Pooja"], "skills": ["marketing", "content_writing", "data_analysis"], "desc": "Digital marketing, ads, campaigns, email marketing, funnels"},
    "social_media": {"lead": "Rohan", "agents": ["Rohan", "Deepak"], "skills": ["social_media", "content_creation", "video_editing"], "desc": "Social media management, content creation, reels, posts"}
}

# Initialize department managers
dept_managers: Dict[str, DepartmentManager] = {}
for dept_name, config in DEPT_CONFIG.items():
    dept_managers[dept_name] = DepartmentManager(
        name=dept_name,
        lead_agent=config["lead"],
        agents=config["agents"],
        skills=config["skills"],
        description=config["desc"]
    )

# --- Memory ---
def ld(n):
    p = os.path.join(MEM, f"{n}.json")
    if os.path.exists(p):
        with open(p) as f: return json.load(f)
    return {}

def sv(n, d):
    with open(os.path.join(MEM, f"{n}.json"), "w") as f: json.dump(d, f, indent=2)

def log(ev, data=None):
    l = ld("logs")
    if "e" not in l: l["e"] = []
    l["e"].append({"t": datetime.now().isoformat(), "ev": ev, "d": data or {}})
    if len(l["e"]) > 300: l["e"] = l["e"][-300:]
    sv("logs", l)

for n in ["agents","tasks","projects","logs","events"]:
    if not os.path.exists(os.path.join(MEM, f"{n}.json")):
        sv(n, {"e":[]} if n!="tasks" else {"active":[],"done":[]})

# --- Settings ---
def cfgs():
    if os.path.exists(SETTINGS):
        with open(SETTINGS) as f: return json.load(f)
    return {}

def dcfg(d):
    c = cfgs()
    x = c.get(d, {})
    return x.get("api_key", API_KEY), x.get("model", MODEL)

# --- AI Call with fast fallback ---
GROQ_MODELS = ["llama-3.1-8b-instant", "llama3-8b-8192", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]

async def ai(msgs, key=None, mdl=None):
    k = key or API_KEY
    m = mdl or MODEL
    if not k: return "API key not set - go to Settings page"
    for i in range(2):
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(API_URL, json={"model":m,"messages":msgs,"temperature":0.7,"max_tokens":1024},
                    headers={"Authorization":f"Bearer {k}","Content-Type":"application/json","HTTP-Referer":"http://localhost:3000","X-Title":"AI Agency"})
                if r.status_code==429:
                    if i==0: await asyncio.sleep(1); continue
                    break
                if r.status_code==200:
                    return r.json()["choices"][0]["message"]["content"]
        except: 
            if i==0: await asyncio.sleep(0.5); continue
    for fm in GROQ_MODELS:
        if fm==m: continue
        try:
            async with httpx.AsyncClient(timeout=30) as c:
                r = await c.post(API_URL, json={"model":fm,"messages":msgs,"temperature":0.7,"max_tokens":1024},
                    headers={"Authorization":f"Bearer {k}","Content-Type":"application/json","HTTP-Referer":"http://localhost:3000","X-Title":"AI Agency"})
                if r.status_code==200:
                    return r.json()["choices"][0]["message"]["content"]
        except: continue
    return "[Rate limited - wait 30s or change model in Settings]"

# --- Models ---
class ChatR(BaseModel):
    message: str
    history: Optional[List[Dict[str,str]]] = []

class DeptR(BaseModel):
    department: str
    message: str
    history: Optional[List[Dict[str,str]]] = []

class TaskR(BaseModel):
    title: str
    description: str
    department: str
    assignee: Optional[str] = None
    project_id: Optional[str] = None

class ProjR(BaseModel):
    name: str
    members: List[str] = []
    description: str = ""

class EventR(BaseModel):
    event: str
    from_dept: str
    to_dept: str
    data: Dict = {}

class ExecuteTaskR(BaseModel):
    task_id: str
    department: str
    agent_name: Optional[str] = None

class DirectDeptR(BaseModel):
    department: str
    message: str

class AgentChatR(BaseModel):
    agent_name: str
    message: str
    history: Optional[List[Dict[str,str]]] = []
    task_context: Optional[str] = None

# --- Routes ---
@app.get("/")
async def root():
    return {
        "name": "AI Agency v6.0",
        "status": "running",
        "system": "structured_hierarchy",
        "departments": list(DEPT_CONFIG.keys()),
        "communication": "strict_hierarchy_enforced"
    }

@app.get("/api/overview")
async def overview():
    t = ld("tasks")
    p = ld("projects")
    dept_status = {name: mgr.get_department_status() for name, mgr in dept_managers.items()}
    return {
        "agents": len(agent_executor.get_all_agents()),
        "departments": list(DEPT_CONFIG.keys()),
        "active_tasks": len(t.get("active",[])),
        "done_tasks": len(t.get("done",[])),
        "projects": len(p.get("e",[])),
        "comm_stats": comm_hub.get_communication_stats(),
        "department_status": dept_status
    }

@app.get("/api/agents")
async def agents():
    return agent_executor.get_all_agents()

@app.get("/api/agents/{name}")
async def get_agent(name: str):
    agent = agent_executor.get_agent(name)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent

@app.get("/api/agents/department/{dept}")
async def get_dept_agents(dept: str):
    return agent_executor.get_agents_by_department(dept)

@app.get("/api/departments")
async def depts():
    return [
        {"name": name, "lead": config["lead"], "agents": len(config["agents"]), "desc": config["desc"],
         "status": dept_managers[name].get_department_status()}
        for name, config in DEPT_CONFIG.items()
    ]

@app.get("/api/departments/{dept}")
async def get_dept(dept: str):
    if dept not in DEPT_CONFIG:
        raise HTTPException(404, f"Department '{dept}' not found")
    config = DEPT_CONFIG[dept]
    mgr = dept_managers[dept]
    icon = {"web": "💻", "website": "💻", "seo": "🔍", "marketing": "📢", "social_media": "📱"}.get(dept, "📋")
    agents_list = [{"id": a, "name": a, "emoji": icon, "role": "Agent", "department": dept} for a in config["agents"]]
    return {
        "name": dept.replace("_", " ").title(),
        "lead": config["lead"],
        "desc": config["desc"],
        "icon": icon,
        "agent_count": len(config["agents"]),
        "agents": agents_list,
        "status": mgr.get_department_status()
    }

# ============================================================
# STRUCTURED COMMUNICATION FLOWS
# ============================================================

# --- Flow 1: CEO → Department (task assignment) ---
@app.post("/api/flow/ceo-to-dept")
async def ceo_to_dept(dept: str, task: TaskR):
    """CEO assigns task to department"""
    if dept not in dept_managers:
        raise HTTPException(404, f"Department '{dept}' not found")
    
    mgr = dept_managers[dept]
    task_id = task.title.lower().replace(" ", "_")[:20] + "_" + str(uuid.uuid4())[:6]
    task_data = {"id": task_id, "title": task.title, "description": task.description, 
                 "created": datetime.now().isoformat()}
    
    # Check duplicates
    if mgr.prevent_duplicate(task_data):
        return {"status": "duplicate", "message": "Task already exists"}
    
    # CEO → Department message
    msg = comm_hub.send_message(
        MessageType.TASK_ASSIGNMENT, "ceo", f"{dept}_dept",
        f"Task: {task.title}\n{task.description}",
        task_id=task_id, priority=MessagePriority.HIGH
    )
    
    # Department receives and processes
    mgr.receive_task(task_data)
    analysis = mgr.analyze_task(task_data)
    selected_agent = mgr.select_agent(task_data)
    
    return {
        "status": "assigned",
        "task_id": task_id,
        "department": dept,
        "selected_agent": selected_agent,
        "analysis": analysis,
        "message": msg
    }

# --- Flow 2: Department → Agent (execution) ---
@app.post("/api/flow/dept-to-agent")
async def dept_to_agent(r: ExecuteTaskR):
    """Department assigns task to agent for execution"""
    if r.department not in dept_managers:
        raise HTTPException(404, f"Department '{r.department}' not found")
    
    mgr = dept_managers[r.department]
    
    # Get task from active tasks or create new
    task_data = mgr.active_tasks.get(r.task_id, {"id": r.task_id, "description": "Execute task"})
    
    # Determine agent
    agent_name = r.agent_name
    if not agent_name:
        analysis = mgr.analyze_task(task_data)
        agent_name = mgr.select_agent(task_data)
    
    # Assign task
    assignment = mgr.assign_task(task_data, agent_name)
    
    # Department → Agent message
    msg = comm_hub.send_message(
        MessageType.TASK_EXECUTION, f"{r.department}_dept", f"{agent_name.lower()}_agent",
        f"Execute: {task_data.get('title', r.task_id)}",
        task_id=r.task_id
    )
    
    return {
        "status": "executing",
        "task_id": r.task_id,
        "agent": agent_name,
        "assignment": assignment,
        "message": msg
    }

# --- Flow 3: Agent → Department (result) ---
@app.post("/api/flow/agent-to-dept")
async def agent_to_dept(r: ExecuteTaskR):
    """Agent returns result to department"""
    if r.department not in dept_managers:
        raise HTTPException(404, f"Department '{r.department}' not found")
    
    mgr = dept_managers[r.department]
    
    # Get agent name
    agent_name = r.agent_name
    if not agent_name:
        task = mgr.active_tasks.get(r.task_id, {})
        agent_name = task.get("assigned_agent", mgr.lead_agent)
    
    # Execute task with real agent
    task_data = mgr.active_tasks.get(r.task_id, {"id": r.task_id, "description": "Task execution", "type": "general"})
    result = agent_executor.execute_task(agent_name, task_data)
    
    # Collect result
    collection = mgr.collect_result(r.task_id, result)
    
    # Agent → Department message
    msg = comm_hub.send_message(
        MessageType.TASK_RESULT, f"{agent_name.lower()}_agent", f"{r.department}_dept",
        f"Result: {result.get('output', '')[:200]}",
        task_id=r.task_id
    )
    
    return {
        "status": "result_collected",
        "task_id": r.task_id,
        "result": result,
        "collection": collection,
        "message": msg
    }

# --- Flow 4: Department → CEO (final output) ---
@app.get("/api/flow/dept-to-ceo/{task_id}")
async def dept_to_ceo(task_id: str):
    """Department returns final output to CEO"""
    # Search all departments for task
    for dept_name, mgr in dept_managers.items():
        output = mgr.return_final_output(task_id)
        if output.get("status") in ["success", "in_progress"]:
            # Department → CEO message
            msg = comm_hub.send_message(
                MessageType.FINAL_OUTPUT, f"{dept_name}_dept", "ceo",
                f"Task {task_id} output: {str(output.get('output', ''))[:200]}",
                task_id=task_id
            )
            return {
                "status": output["status"],
                "department": dept_name,
                "output": output,
                "message": msg
            }
    
    raise HTTPException(404, "Task not found in any department")

# ============================================================
# DIRECT MODE: User → Department (no CEO involvement)
# ============================================================

@app.post("/api/direct/department")
async def direct_dept_chat(r: DirectDeptR):
    """User directly chats with department - department handles task directly"""
    if r.department not in dept_managers:
        raise HTTPException(404, f"Department '{r.department}' not found")
    
    mgr = dept_managers[r.department]
    task_id = "direct_" + str(uuid.uuid4())[:8]
    
    # Direct request message
    msg = comm_hub.send_message(
        MessageType.DIRECT_REQUEST, "user", f"{r.department}_dept",
        r.message, task_id=task_id
    )
    
    # Department handles directly
    task_data = {"id": task_id, "title": "Direct Request", "description": r.message, "type": "general"}
    mgr.receive_task(task_data)
    analysis = mgr.analyze_task(task_data)
    selected_agent = mgr.select_agent(task_data)
    
    # Execute with agent using Groq API
    agent = agent_executor.get_agent(selected_agent)
    if agent:
        k, m = dcfg(r.department)
        system_prompt = agent.get("system_prompt", f"You are {selected_agent}.")
        ai_msgs = [{"role":"system","content":system_prompt},{"role":"user","content":r.message}]
        result_output = await ai(ai_msgs, k, m)
    else:
        result_output = "Agent not found"
    
    result = {"output": result_output, "status": "completed"}
    mgr.collect_result(task_id, result)
    
    # Direct response
    response_msg = comm_hub.send_message(
        MessageType.DIRECT_RESPONSE, f"{r.department}_dept", "user",
        result.get("output", "Task completed"), task_id=task_id
    )
    
    return {
        "status": "completed",
        "task_id": task_id,
        "department": r.department,
        "agent": selected_agent,
        "result": result,
        "analysis": analysis
    }

# ============================================================
# CHAT WITH AGENT (personal)
# ============================================================

@app.post("/api/chat/agent")
async def chat_with_agent(r: AgentChatR):
    """Chat directly with a specific agent"""
    agent = agent_executor.get_agent(r.agent_name)
    if not agent:
        raise HTTPException(404, f"Agent '{r.agent_name}' not found")
    
    task_context = r.task_context or "General inquiry"
    task_data = {
        "id": "chat_" + str(uuid.uuid4())[:8],
        "title": "Agent Chat",
        "description": r.message,
        "type": "general",
        "context": task_context
    }
    
    result = agent_executor.execute_task(r.agent_name, task_data)
    
    return {
        "agent": agent["name"],
        "role": agent["role"],
        "department": agent["department"],
        "response": result.get("output", ""),
        "steps_executed": result.get("steps_executed", []),
        "tools_used": result.get("tools_used", [])
    }

# --- CEO Chat (USER ONLY) ---
@app.post("/api/chat/ceo")
async def chat_ceo(r: ChatR):
    k, m = dcfg("ceo")
    CEO_SYS = """You are Atlas, CEO of a digital agency. Talk to the user like a friend - natural Hinglish conversation.
When someone asks for a project, suggest the right department and explain what can be done.
Keep it casual, friendly. Use simple words - no jargon.

Your departments:
- Website (Lead: Amit): Website banana, landing pages, web apps, full-stack development
- SEO (Lead: Kavita): Google ranking, SEO, keyword research, analytics
- Marketing (Lead: Neha): Digital marketing, ads, campaigns, email marketing
- Social Media (Lead: Rohan): Content creation, reels, posts, social media management"""
    msgs = [{"role":"system","content":CEO_SYS}]
    if r.history: msgs.extend(r.history[-8:])
    msgs.append({"role":"user","content":r.message})
    resp = await ai(msgs, k, m)
    log("ceo_chat",{"msg":r.message[:50]})
    return {"sender":"Atlas","response":resp}

# --- Agent Chat (with Groq API) ---
@app.post("/api/chat/agent-groq")
async def chat_agent_groq(r: AgentChatR):
    """Chat with any agent using Groq API"""
    agent = agent_executor.get_agent(r.agent_name)
    if not agent:
        raise HTTPException(404, f"Agent '{r.agent_name}' not found")
    
    k, m = dcfg(r.agent_name)
    
    system_prompt = agent.get("system_prompt", f"You are {r.agent_name}, {agent.get('role', 'an agent')}.")
    msgs = [{"role":"system","content":system_prompt}]
    if r.history: msgs.extend(r.history[-8:])
    msgs.append({"role":"user","content":r.message})
    resp = await ai(msgs, k, m)
    log("agent_chat",{"agent":r.agent_name,"msg":r.message[:50]})
    return {"sender":agent["name"],"response":resp}

# --- Department Chat (INTERNAL WORK) ---
@app.post("/api/chat/dept")
async def chat_dept(r: DeptR):
    k, m = dcfg(r.department)
    DEPT_SYS = {
        "web": "You are Sara, Web Department Coordinator. You manage 8 agents: Maya (UI), Riya (Frontend), Aryan (Backend), Dev (API), Kavita (SEO), Vikram (Performance), Kira (QA). Talk to user in natural Hinglish. Assign tasks to right agent. Friendly, professional tone.",
        "seo": "You are Kavita, SEO Department Lead. Aap Google ranking, keyword research, SEO optimization, aur analytics mein expert ho. Natural Hinglish mein baat karo - tracking ranking, traffic analysis, growth. Friendly and helpful tone.",
        "marketing": "You are Neha, Marketing Department Lead. Digital marketing, ads, campaigns, email marketing funnels mein expert ho. Natural Hinglish mein baat karo - jaise ek experienced marketer apne client se baat karta hai. Practical advice do.",
        "social_media": "You are Rohan, Social Media Department Lead. Content creation, reels, posts, social media management mein expert ho. Trendy Hinglish mein baat karo - creative aur energetic vibe. Engaging suggestions do."
    }
    prompt = DEPT_SYS.get(r.department, f"You are {r.department} manager. Baat karo natural Hinglish mein - jaise dost se baat karte ho.")
    msgs = [{"role":"system","content":prompt}]
    if r.history: msgs.extend(r.history[-8:])
    msgs.append({"role":"user","content":r.message})
    resp = await ai(msgs, k, m)
    log("dept_chat",{"dept":r.department,"msg":r.message[:50]})
    return {"sender":r.department.capitalize(),"response":resp}

# --- Tasks ---
@app.post("/api/tasks")
async def create_task(r: TaskR):
    t = ld("tasks")
    if "active" not in t: t["active"] = []
    task = {"id":str(uuid.uuid4())[:8],"title":r.title,"desc":r.description,"dept":r.department,
            "assignee":r.assignee,"project":r.project_id,"status":"pending","created":datetime.now().isoformat()}
    t["active"].append(task)
    sv("tasks", t)
    log("task_created", task)
    return task

@app.get("/api/tasks")
async def get_tasks():
    return ld("tasks")

@app.post("/api/tasks/{tid}/done")
async def done_task(tid: str):
    t = ld("tasks")
    for i,x in enumerate(t.get("active",[])):
        if x["id"]==tid:
            x["status"]="done"; x["done_at"]=datetime.now().isoformat()
            if "done" not in t: t["done"]=[]
            t["done"].append(t["active"].pop(i))
            sv("tasks",t); log("task_done",x)
            return x
    raise HTTPException(404,"Not found")

@app.delete("/api/tasks/{tid}")
async def delete_task(tid: str):
    t = ld("tasks")
    t["active"]=[x for x in t.get("active",[]) if x["id"]!=tid]
    sv("tasks",t); log("task_deleted",{"id":tid})
    return {"ok":True}

# --- Projects ---
@app.post("/api/projects")
async def create_project(r: ProjR):
    p = ld("projects")
    if "e" not in p: p["e"]=[]
    proj = {"id":str(uuid.uuid4())[:8],"name":r.name,"members":r.members,"desc":r.description,
            "chat":[],"tasks":[],"created":datetime.now().isoformat()}
    p["e"].append(proj)
    sv("projects",p); log("project_created",proj)
    return proj

@app.get("/api/projects")
async def get_projects():
    return ld("projects")

@app.get("/api/projects/{pid}")
async def get_project(pid: str):
    p = ld("projects")
    for x in p.get("e",[]):
        if x["id"]==pid: return x
    raise HTTPException(404,"Not found")

# --- Events ---
@app.post("/api/events")
async def create_event(r: EventR):
    e = ld("events")
    if "e" not in e: e["e"]=[]
    ev = {"id":str(uuid.uuid4())[:8],"event":r.event,"from":r.from_dept,"to":r.to_dept,"data":r.data,"time":datetime.now().isoformat()}
    e["e"].append(ev)
    sv("events",e); log("event_created",ev)
    return ev

@app.get("/api/events")
async def get_events():
    return ld("events")

# --- Communication Stats ---
@app.get("/api/communication/stats")
async def comm_stats():
    return comm_hub.get_communication_stats()

@app.get("/api/communication/messages/{task_id}")
async def comm_messages(task_id: str):
    return comm_hub.get_task_messages(task_id)

@app.get("/api/communication/hierarchy")
async def comm_hierarchy():
    return {
        "rules": {
            "ceo_to_dept": "CEO → Department (task assignment)",
            "dept_to_agent": "Department → Agent (execution)",
            "agent_to_dept": "Agent → Department (result)",
            "dept_to_ceo": "Department → CEO (final output)",
            "direct_mode": "User → Department (direct, no CEO)",
            "prohibited": ["CEO ↔ Agent direct", "Random chat"]
        },
        "total_messages": len(comm_hub.messages),
        "message_log_keys": list(comm_hub.message_log.keys())
    }

# --- Logs ---
@app.get("/api/logs")
async def get_logs():
    return ld("logs")

# --- Settings ---
@app.get("/api/settings")
async def get_settings():
    return cfgs()

@app.post("/api/settings")
async def save_settings(c: Dict[str,Dict[str,str]]):
    with open(SETTINGS,"w") as f: json.dump(c,f,indent=2)
    log("settings_saved"); return {"ok":True}

class TestR(BaseModel):
    api_key: str
    model: str

@app.post("/api/settings/{d}/test")
async def test_setting(d: str, r: TestR):
    resp = await ai([{"role":"user","content":"Say OK in one word"}], r.api_key, r.model)
    if resp.startswith("["): return {"ok":False,"error":resp}
    return {"ok":True,"response":resp}

# --- Skills ---
@app.get("/api/skills")
async def get_skills():
    return ld("skills")

@app.post("/api/skills/init")
async def init_skills():
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from skills import init_default_skills
    data = init_default_skills()
    sv("skills", data)
    return data

# ============================================================
# WEB DEPARTMENT ROUTES
# ============================================================

@app.get("/api/web-department")
async def get_web_dept_status():
    """Get web department status with all agents"""
    return web_dept.get_status()

@app.get("/api/web-department/agents")
async def get_web_dept_agents():
    """Get all web department agents"""
    return web_dept.get_all_agents()

@app.get("/api/web-department/agents/{agent_key}")
async def get_web_dept_agent(agent_key: str):
    """Get a specific web department agent"""
    agent = web_dept.get_agent(agent_key)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_key}' not found")
    return agent.get_status()

class WebTaskR(BaseModel):
    task: str
    description: str
    task_type: str = "general"
    priority: str = "medium"

class BrainTaskR(BaseModel):
    title: str
    description: str
    use_ai: bool = True
    history: Optional[List[Dict[str,str]]] = []

@app.post("/api/web-department/assign")
async def assign_web_task(r: WebTaskR):
    """Assign task to web department (coordinator distributes)"""
    task = {
        "id": str(uuid.uuid4())[:8],
        "task": r.task,
        "description": r.description,
        "type": r.task_type,
        "priority": r.priority
    }
    result = web_dept.assign_task(task)
    return result

class DeptChatR(BaseModel):
    message: str
    history: Optional[List[Dict[str,str]]] = []

class WebMessageR(BaseModel):
    from_agent: str
    to_agent: str
    task: str

@app.post("/api/web-department/message")
async def send_web_message(r: WebMessageR):
    """Send structured message between web agents"""
    return web_dept.send_message(r.from_agent, r.to_agent, r.task)

@app.get("/api/web-department/tools")
async def get_tools():
    """Get all available tools"""
    tools_file = os.path.join(os.path.dirname(__file__), "tools.json")
    if os.path.exists(tools_file):
        with open(tools_file) as f:
            return json.load(f)
    return {"tools": []}

@app.get("/api/web-department/agents/{agent_key}/profile")
async def get_agent_profile(agent_key: str):
    """Get full agent profile with skills, tools, system prompt"""
    agent = web_dept.get_agent(agent_key)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_key}' not found")
    return {
        "name": agent.name,
        "role": agent.role,
        "department": agent.department,
        "skills": agent.skills,
        "tools": agent.tools,
        "system_prompt": agent.system_prompt,
        "execution_steps": agent.execution_steps,
        "status": agent.status,
        "workload": agent.workload,
        "tasks_completed": len(agent.task_history),
        "message_history": agent.message_history
    }

@app.post("/api/web-department/chat")
async def dept_free_chat(r: DeptChatR):
    """Free thinking chat with Web Department (Coordinator)"""
    coordinator = web_dept.get_agent("coordinator")
    if not coordinator:
        return {"error": "Coordinator not found"}
    msgs = [{"role": "system", "content": coordinator.system_prompt}]
    if r.history:
        msgs.extend(r.history[-10:])
    msgs.append({"role": "user", "content": r.message})
    resp = await ai(msgs)
    return {"sender": coordinator.name, "response": resp}


# ============================================================
# BRAIN-POWERED WEB DEPARTMENT ROUTES (The "Dimag" 🧠) - DISABLED
# ============================================================
# Brain routes temporarily disabled - using individual agent files now

# ============================================================
# WEB DEPARTMENT - INDIVIDUAL AGENT CHAT ENDPOINTS (Groq API Connected)
# ============================================================

@app.post("/api/web-department/chat/{agent_key}")
async def chat_with_web_agent(agent_key: str, r: DeptChatR):
    """Chat with any specific web department agent using Groq API"""
    agent = web_dept.get_agent(agent_key)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_key}' not found")
    
    result = await web_dept.chat_with_agent(agent_key, r.message, r.history)
    if "error" in result:
        return {"sender": "System", "response": result["error"]}
    return {"sender": result["sender"], "response": result["response"]}

@app.get("/api/web-department/agents-list")
async def list_web_agents():
    """Get all web department agents with status"""
    return {
        "agents": [
            {"key": "coordinator", "name": "Sara", "role": "Coordinator"},
            {"key": "ui_designer", "name": "Maya", "role": "UI Designer"},
            {"key": "frontend", "name": "Riya", "role": "Frontend Developer"},
            {"key": "backend", "name": "Aryan", "role": "Backend Developer"},
            {"key": "api_manager", "name": "Dev", "role": "API Manager"},
            {"key": "seo", "name": "Kavita", "role": "SEO Agent"},
            {"key": "performance", "name": "Vikram", "role": "Performance Agent"},
            {"key": "qa", "name": "Kira", "role": "QA Tester"}
        ]
    }

@app.get("/api/web-department/agent-files/{agent_key}")
async def get_agent_files(agent_key: str):
    """Get all md files (skills.md, system.md) for an agent"""
    return web_dept.get_agent_files(agent_key)

@app.get("/api/web-department/agent-files/{agent_key}/{filename}")
async def get_agent_file(agent_key: str, filename: str):
    """Get specific file content for an agent"""
    result = web_dept.get_agent_file_content(agent_key, filename)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
