"""AI Agency Portal v7.0 - Real Execution Engine"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx, os, json, asyncio, uuid
from dotenv import load_dotenv
load_dotenv()

# Import the new engine
from engine import AgencyEngine, call_groq, AGENT_REGISTRY, GROQ_API_URL

# Initialize the main engine
engine = AgencyEngine()

app = FastAPI(title="AI Agency Portal v7.0", version="7.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Config ---
API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# --- Legacy AI Call (for routes that still need it) ---
GROQ_MODELS = ["llama-3.1-8b-instant", "llama3-8b-8192", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]

async def ai(msgs, key=None, mdl=None, max_tokens=1024):
    """Legacy AI call with fallback - uses engine's Groq call"""
    return await call_groq(msgs, key, mdl, max_tokens)

# ============================================================
# REQUEST MODELS
# ============================================================

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

class AgentChatR(BaseModel):
    agent_name: str
    message: str
    history: Optional[List[Dict[str,str]]] = []
    task_context: Optional[str] = None

class EngineRequest(BaseModel):
    message: str
    project_id: Optional[str] = None

class TestR(BaseModel):
    api_key: str
    model: str

# ============================================================
# MEMORY (legacy JSON store for backwards compat)
# ============================================================
MEM = os.path.join(os.path.dirname(__file__), "memory")
os.makedirs(MEM, exist_ok=True)
SETTINGS = os.path.join(os.path.dirname(__file__), "settings.json")

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

def cfgs():
    if os.path.exists(SETTINGS):
        with open(SETTINGS) as f: return json.load(f)
    return {}

def dcfg(d):
    c = cfgs()
    x = c.get(d, {})
    return x.get("api_key", API_KEY), x.get("model", MODEL)

# ============================================================
# ROOT & OVERVIEW
# ============================================================

@app.get("/")
async def root():
    overview = engine.get_overview()
    return {
        "name": "AI Agency Portal v7.0",
        "status": "running",
        "system": "real_execution_engine",
        "departments": overview.get("departments", []),
        "agents": overview.get("total_agents", 0),
        "skills_loaded": overview.get("skills_loaded", 0),
        "flow": "CEO -> Reception -> Department -> Agents -> Response"
    }

@app.get("/api/overview")
async def overview():
    """Get system overview from engine"""
    return engine.get_overview()

# ============================================================
# CHAT ROUTES
# ============================================================

@app.post("/api/chat/ceo")
async def chat_ceo(r: ChatR):
    """CEO chat - analyzes request, creates tasks, assigns to departments"""
    k, m = dcfg("ceo")
    CEO_SYS = """You are Atlas, CEO of a digital agency. Talk to the user like a friend - natural Hinglish conversation.
When someone asks for a project, suggest the right department and explain what can be done.
Keep it casual, friendly. Use simple words - no jargon.

Your departments:
- Website (Web Dept): Website banana, landing pages, web apps, full-stack development
- SEO: Google ranking, SEO, keyword research, analytics
- Marketing: Digital marketing, ads, campaigns, email marketing
- Social Media: Content creation, reels, posts, social media management"""
    msgs = [{"role":"system","content":CEO_SYS}]
    if r.history: msgs.extend(r.history[-8:])
    msgs.append({"role":"user","content":r.message})
    resp = await ai(msgs, k, m)
    log("ceo_chat",{"msg":r.message[:50]})
    return {"sender":"Atlas","response":resp}

@app.post("/api/chat/dept")
async def chat_dept(r: DeptR):
    """Department chat"""
    k, m = dcfg(r.department)
    prompt = f"You are the {r.department} department of an AI agency. Help the user with their request. Be professional and helpful."
    msgs = [{"role":"system","content":prompt}]
    if r.history: msgs.extend(r.history[-8:])
    msgs.append({"role":"user","content":r.message})
    resp = await ai(msgs, k, m)
    log("dept_chat",{"dept":r.department,"msg":r.message[:50]})
    return {"sender":r.department.capitalize(),"response":resp}

@app.post("/api/chat/agent-groq")
async def chat_agent_groq(r: AgentChatR):
    """Chat with a specific agent for task execution"""
    all_agents = engine.get_all_agents_info()
    agent = next((a for a in all_agents if a.get("name","").lower() == r.agent_name.lower() or a.get("id","").lower() == r.agent_name.lower()), None)
    if not agent:
        # Fallback: try by key
        for dept, agents in AGENT_REGISTRY.items():
            if r.agent_name.lower() in agents:
                agent_info = agents[r.agent_name.lower()]
                agent = {"id": r.agent_name.lower(), "name": agent_info["name"], "department": dept, "system_prompt": agent_info["system_prompt"]}
                break
    if not agent:
        raise HTTPException(404, f"Agent '{r.agent_name}' not found")

    k, m = dcfg(agent.get("department", ""))
    system_prompt = agent.get("system_prompt", f"You are {agent.get('name', r.agent_name)}.")
    msgs = [{"role":"system","content":system_prompt}]
    if r.history: msgs.extend(r.history[-8:])
    msgs.append({"role":"user","content":r.message})
    resp = await ai(msgs, k, m)
    log("agent_chat",{"agent":r.agent_name,"msg":r.message[:50]})
    return {"sender":agent["name"],"response":resp}

# ============================================================
# ENGINE ROUTES - Real Execution System
# ============================================================

@app.post("/api/engine/process")
async def engine_process(r: EngineRequest):
    """
    Main engine endpoint: CEO sends request -> system processes -> returns result
    Flow: CEO -> Reception -> Department -> Agents -> Response
    """
    result = await engine.process_ceo_request(r.message, r.project_id)
    return result

@app.get("/api/engine/overview")
async def engine_overview():
    return engine.get_overview()

@app.get("/api/engine/agents")
async def engine_agents():
    return engine.get_all_agents_info()

@app.get("/api/engine/departments")
async def engine_departments():
    return engine.get_department_info()

@app.get("/api/engine/tasks/active")
async def engine_active_tasks():
    return engine.get_active_tasks()

@app.get("/api/engine/tasks/completed")
async def engine_completed_tasks():
    return engine.get_completed_tasks()

@app.get("/api/engine/logs")
async def engine_logs():
    return engine.get_system_logs()

@app.get("/api/engine/errors")
async def engine_errors():
    return engine.get_errors()

@app.get("/api/engine/skills")
async def engine_skills():
    return engine.get_skills()

@app.get("/api/engine/task/{task_id}")
async def engine_task_detail(task_id: str):
    task = engine.get_task_details(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

# ============================================================
# AGENTS ROUTES (from engine)
# ============================================================

@app.get("/api/agents")
async def agents():
    """Get all agents with details from engine"""
    return engine.get_all_agents_info()

@app.get("/api/agents/{name}")
async def get_agent(name: str):
    """Get specific agent details"""
    all_agents = engine.get_all_agents_info()
    agent = next((a for a in all_agents if a.get("name","").lower() == name.lower() or a.get("id","").lower() == name.lower()), None)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent

@app.get("/api/agents/department/{dept}")
async def get_dept_agents(dept: str):
    """Get agents in a specific department"""
    dept_info = engine.get_department_info()
    for d in dept_info:
        if d["name"].lower() == dept.lower():
            return d["agents"]
    raise HTTPException(404, f"Department '{dept}' not found")

@app.get("/api/departments")
async def depts():
    """Get all departments"""
    return engine.get_department_info()

# ============================================================
# TASKS ROUTES
# ============================================================

@app.post("/api/tasks")
async def create_task(r: TaskR):
    """Create a task (legacy route, also stores in engine)"""
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
    """Get all tasks"""
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

# ============================================================
# PROJECTS ROUTES
# ============================================================

@app.post("/api/projects")
async def create_project(r: ProjR):
    """Create a new project"""
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

# ============================================================
# SETTINGS ROUTES
# ============================================================

@app.get("/api/settings")
async def get_settings():
    return cfgs()

@app.post("/api/settings")
async def save_settings(c: Dict[str,Dict[str,str]]):
    with open(SETTINGS,"w") as f: json.dump(c,f,indent=2)
    log("settings_saved"); return {"ok":True}

@app.post("/api/settings/{d}/test")
async def test_setting(d: str, r: TestR):
    resp = await ai([{"role":"user","content":"Say OK in one word"}], r.api_key, r.model)
    if resp.startswith("["): return {"ok":False,"error":resp}
    return {"ok":True,"response":resp}

# ============================================================
# SKILLS ROUTES
# ============================================================

@app.get("/api/skills")
async def get_skills():
    """Get all skills from engine"""
    return engine.get_skills()

@app.post("/api/skills/init")
async def init_skills():
    """Initialize skills (already done on engine startup)"""
    return engine.get_skills()

# ============================================================
# LOGS ROUTES
# ============================================================

@app.get("/api/logs")
async def get_logs():
    return ld("logs")

# ============================================================
# EVENTS ROUTES
# ============================================================

class EventR(BaseModel):
    event: str
    from_dept: str
    to_dept: str
    data: Dict = {}

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

# ============================================================
# ROOT
# ============================================================

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)