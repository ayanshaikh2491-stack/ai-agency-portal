'use client';
import { useState, useEffect, useRef } from 'react';
// Use relative URLs for API (handled by Next.js rewrites in next.config.mjs)
// In production, set NEXT_PUBLIC_API_URL in Vercel environment variables
const API = process.env.NEXT_PUBLIC_API_URL ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '') : '';

export default function Home() {
  const [view, setView] = useState('ceo');
  const [dept, setDept] = useState(null);
  const [sidebar, setSidebar] = useState(true);

  // Chats
  const [ceoMsgs, setCeoMsgs] = useState([]);
  const [ceoIn, setCeoIn] = useState('');
  const [ceoBusy, setCeoBusy] = useState(false);

  const [deptMsgs, setDeptMsgs] = useState([]);
  const [deptIn, setDeptIn] = useState('');
  const [deptBusy, setDeptBusy] = useState(false);

  // Data
  const [ov, setOv] = useState(null);
  const [tasks, setTasks] = useState({ active: [], done: [] });
  const [projects, setProjects] = useState({ e: [] });
  const [logs, setLogs] = useState({ e: [] });
  const [curProj, setCurProj] = useState(null);
  const [projChat, setProjChat] = useState([]);
  const [projIn, setProjIn] = useState('');
  const [projUser, setProjUser] = useState('User');
  const [newProj, setNewProj] = useState(false);
  const [newProjName, setNewProjName] = useState('');

  // Department & Agents
  const [deptInfo, setDeptInfo] = useState(null);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentDetail, setAgentDetail] = useState(null);

  const ceoRef = useRef(null);
  const deptRef = useRef(null);
  const projRef = useRef(null);

  useEffect(() => { load(); loadDepts(); const t = setInterval(load, 15000); return () => clearInterval(t); }, []);
  useEffect(() => { ceoRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [ceoMsgs]);
  useEffect(() => { deptRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [deptMsgs]);
  useEffect(() => { projRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [projChat]);

  const load = async () => {
    try {
      const [o, t, p, l] = await Promise.all([
        fetch(API + '/api/overview').then(r => r.json()).catch(() => null),
        fetch(API + '/api/tasks').then(r => r.json()).catch(() => ({ active: [], done: [] })),
        fetch(API + '/api/projects').then(r => r.json()).catch(() => ({ e: [] })),
        fetch(API + '/api/logs').then(r => r.json()).catch(() => ({ e: [] }))
      ]);
      if (o) setOv(o); setTasks(t); setProjects(p); setLogs(l);
    } catch (e) { }
  };

  const loadDepts = async () => {
    try {
      const a = await fetch(API + '/api/agents').then(r => r.json()).catch(() => []);
      setAgents(a);
    } catch (e) { }
  };

  const openDept = async (d) => {
    setDept(d);
    setView('dept');
    setDeptMsgs([]);
    setSelectedAgent(null);
    setAgentDetail(null);
    try {
      const info = await fetch(API + `/api/departments/${d}`).then(r => r.json()).catch(() => null);
      setDeptInfo(info);
    } catch (e) { }
  };

  const openAgent = async (agentId) => {
    setSelectedAgent(agentId);
    try {
      const detail = await fetch(API + `/api/agents/${agentId}`).then(r => r.json()).catch(() => null);
      setAgentDetail(detail);
    } catch (e) { }
  };

  const getDeptAgents = (deptKey) => {
    return agents.filter(a => a.dept === deptKey);
  };

  const sendCeo = async () => {
    if (!ceoIn.trim() || ceoBusy) return;
    const msg = ceoIn; setCeoIn(''); setCeoBusy(true);
    setCeoMsgs(p => [...p, { role: 'user', content: msg, sender: 'You' }]);
    try {
      const hist = ceoMsgs.slice(-8).map(m => ({ role: m.sender === 'You' ? 'user' : 'assistant', content: m.content }));
      const r = await fetch(API + '/api/chat/ceo', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg, history: hist }) });
      if (r.ok) { const d = await r.json(); setCeoMsgs(p => [...p, { role: 'assistant', content: d.response, sender: d.sender }]); }
      else setCeoMsgs(p => [...p, { role: 'assistant', content: 'Connection error', sender: 'System' }]);
    } catch (e) { setCeoMsgs(p => [...p, { role: 'assistant', content: 'Failed to connect', sender: 'System' }]); }
    setCeoBusy(false);
  };

  const sendDept = async () => {
    if (!deptIn.trim() || !dept || deptBusy) return;
    const msg = deptIn; setDeptIn(''); setDeptBusy(true);
    setDeptMsgs(p => [...p, { role: 'user', content: msg, sender: 'You' }]);
    try {
      const hist = deptMsgs.slice(-8).map(m => ({ role: m.sender === 'You' ? 'user' : 'assistant', content: m.content }));
      const r = await fetch(API + '/api/chat/dept', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ department: dept, message: msg, history: hist }) });
      if (r.ok) { const d = await r.json(); setDeptMsgs(p => [...p, { role: 'assistant', content: d.response, sender: d.sender }]); }
      else setDeptMsgs(p => [...p, { role: 'assistant', content: 'Connection error', sender: 'System' }]);
    } catch (e) { setDeptMsgs(p => [...p, { role: 'assistant', content: 'Failed to connect', sender: 'System' }]); }
    setDeptBusy(false);
  };

  const createTask = async (title, desc, department) => {
    try {
      await fetch(API + '/api/tasks', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title, description: desc, department }) });
      load();
    } catch (e) { }
  };

  const createProject = async () => {
    if (!newProjName.trim()) return;
    try {
      const r = await fetch(API + '/api/projects', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: newProjName, members: [projUser], description: '' }) });
      if (r.ok) { const p = await r.json(); setCurProj(p.id); setProjChat([]); setNewProj(false); setNewProjName(''); load(); }
    } catch (e) { }
  };

  const sendProjChat = async () => {
    if (!projIn.trim() || !curProj) return;
    const msg = projIn; setProjIn('');
    setProjChat(p => [...p, { user: projUser, msg: msg, time: new Date().toISOString() }]);
    try {
      await fetch(`${API}/api/projects/${curProj}/chat?message=${encodeURIComponent(msg)}&user=${encodeURIComponent(projUser)}`, { method: 'POST' });
    } catch (e) { }
  };

  const aiTasks = async () => {
    if (!curProj) return;
    try {
      const r = await fetch(API + '/api/projects/' + curProj + '/ai-tasks', { method: 'POST' });
      if (r.ok) { const d = await r.json(); load(); }
    } catch (e) { }
  };

  const depts = [
    { name: 'web', icon: '💻', lead: 'Sara + Team', desc: '8 specialized agents for website dev', agents: 8 },
    { name: 'seo', icon: '🔍', lead: 'Kavita', desc: 'Google ranking, traffic, growth tracking', agents: 2 },
    { name: 'marketing', icon: '📢', lead: 'Neha', desc: 'Digital marketing, ads, campaigns', agents: 2 },
    { name: 'social_media', icon: '📱', lead: 'Rohan', desc: 'Content creation, reels, social media', agents: 2 }
  ];

  // Web department state
  const [webAgents, setWebAgents] = useState([]);
  const [selectedWebAgent, setSelectedWebAgent] = useState(null);
  const [webAgentProfile, setWebAgentProfile] = useState(null);
  const [webChatMsgs, setWebChatMsgs] = useState([]);
  const [webChatIn, setWebChatIn] = useState('');
  const [webChatBusy, setWebChatBusy] = useState(false);
  const [showDeptProfile, setShowDeptProfile] = useState(false);
  const [showAgentProfile, setShowAgentProfile] = useState(false);
  const [webTaskIn, setWebTaskIn] = useState('');
  const [webTaskResult, setWebTaskResult] = useState(null);

  // Brain state
  const [brainMode, setBrainMode] = useState('execute'); // 'analyze' or 'execute'
  const [brainThinking, setBrainThinking] = useState(false);
  const [brainResult, setBrainResult] = useState(null);
  const [brainTaskTitle, setBrainTaskTitle] = useState('');
  const [brainTaskDesc, setBrainTaskDesc] = useState('');
  const [showBrainPanel, setShowBrainPanel] = useState(false);

  useEffect(() => { loadWebAgents(); }, []);
  useEffect(() => { if (view === 'dept' && dept === 'web') loadWebAgents(); }, [view, dept]);

  const loadWebAgents = async () => {
    try {
      const res = await fetch(API + '/api/web-department/agents');
      if (res.ok) setWebAgents(await res.json());
    } catch (e) { }
  };

  const openWebAgentProfile = async (key) => {
    try {
      const res = await fetch(`${API}/api/web-department/agents/${key}/profile`);
      if (res.ok) {
        setWebAgentProfile(await res.json());
        setShowAgentProfile(true);
      }
    } catch (e) { }
  };

  const sendWebChat = async () => {
    if (!webChatIn.trim() || webChatBusy) return;
    const msg = webChatIn; setWebChatIn(''); setWebChatBusy(true);
    setWebChatMsgs(p => [...p, { role: 'user', content: msg, sender: 'You' }]);
    try {
      const hist = webChatMsgs.slice(-8).map(m => ({ role: m.sender === 'You' ? 'user' : 'assistant', content: m.content }));
      const res = await fetch(`${API}/api/web-department/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: hist })
      });
      if (res.ok) {
        const d = await res.json();
        setWebChatMsgs(p => [...p, { role: 'assistant', content: d.response, sender: d.sender }]);
      }
    } catch (e) { setWebChatMsgs(p => [...p, { role: 'assistant', content: 'Connection error', sender: 'System' }]); }
    setWebChatBusy(false);
  };

  const assignWebTask = async () => {
    if (!webTaskIn.trim()) return;
    try {
      const res = await fetch(`${API}/api/web-department/assign`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: 'Web Task', description: webTaskIn, task_type: 'web', priority: 'medium' })
      });
      if (res.ok) { setWebTaskResult(await res.json()); setWebTaskIn(''); }
    } catch (e) { }
  };

  // Brain functions
  const runBrainAnalyze = async () => {
    if (!brainTaskTitle.trim()) return;
    setBrainThinking(true);
    try {
      const res = await fetch(`${API}/api/web-department/brain/analyze`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: brainTaskTitle, description: brainTaskDesc, use_ai: true })
      });
      if (res.ok) setBrainResult(await res.json());
    } catch (e) { }
    setBrainThinking(false);
  };

  const runBrainExecute = async () => {
    if (!brainTaskTitle.trim()) return;
    setBrainThinking(true);
    setBrainResult(null);
    try {
      const res = await fetch(`${API}/api/web-department/brain/execute`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: brainTaskTitle, description: brainTaskDesc, use_ai: true })
      });
      if (res.ok) setBrainResult(await res.json());
    } catch (e) { }
    setBrainThinking(false);
  };

  return (
    <div className="flex h-screen bg-[#212121] text-white">
      {/* Sidebar */}
      <div className={`${sidebar ? 'w-64' : 'w-14'} bg-[#171717] border-r border-[#2f2f2f] flex flex-col transition-all`}>
        <div className="p-3 flex items-center gap-2 border-b border-[#2f2f2f]">
          <div className="w-7 h-7 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center font-bold text-xs">A</div>
          {sidebar && <span className="font-semibold text-sm">AI Agency v5</span>}
        </div>
        <nav className="p-1.5 space-y-0.5 flex-1 overflow-auto">
          <button onClick={() => setView('ceo')} className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm ${view === 'ceo' ? 'bg-[#2f2f2f] text-white' : 'text-[#b4b4b4] hover:bg-[#2f2f2f]'}`}>
            <span>🧠</span>{sidebar && <span>CEO Chat</span>}
          </button>
          {sidebar && <div className="px-2.5 pt-3 pb-1 text-[10px] text-[#8e8e8e] uppercase tracking-wider font-medium">Departments</div>}
          {depts.map(d => (
            <button key={d.name} onClick={() => openDept(d.name)} className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm ${view === 'dept' && dept === d.name ? 'bg-[#2f2f2f] text-white' : 'text-[#b4b4b4] hover:bg-[#2f2f2f]'}`}>
              <span>{d.icon}</span>{sidebar && <span className="capitalize">{d.name}</span>}
            </button>
          ))}
          {sidebar && <div className="px-2.5 pt-3 pb-1 text-[10px] text-[#8e8e8e] uppercase tracking-wider font-medium">System</div>}
          <button onClick={() => { setView('tasks'); load() }} className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm ${view === 'tasks' ? 'bg-[#2f2f2f] text-white' : 'text-[#b4b4b4] hover:bg-[#2f2f2f]'}`}>
            <span>📋</span>{sidebar && <span>Tasks</span>}
            {sidebar && tasks.active?.length > 0 && <span className="ml-auto bg-[#3f3f3f] text-[10px] px-1.5 py-0.5 rounded-full">{tasks.active.length}</span>}
          </button>
          <button onClick={() => { setView('projects'); load() }} className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm ${view === 'projects' ? 'bg-[#2f2f2f] text-white' : 'text-[#b4b4b4] hover:bg-[#2f2f2f]'}`}>
            <span>📁</span>{sidebar && <span>Projects</span>}
            {sidebar && projects.e?.length > 0 && <span className="ml-auto bg-[#3f3f3f] text-[10px] px-1.5 py-0.5 rounded-full">{projects.e.length}</span>}
          </button>
          <button onClick={() => { setView('logs'); load() }} className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm ${view === 'logs' ? 'bg-[#2f2f2f] text-white' : 'text-[#b4b4b4] hover:bg-[#2f2f2f]'}`}>
            <span>📝</span>{sidebar && <span>Logs</span>}
          </button>
          <a href="/agents" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
            <span>🤖</span>{sidebar && <span>Agents</span>}
          </a>
          <a href="/settings" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
            <span>⚙️</span>{sidebar && <span>Settings</span>}
          </a>
        </nav>
        <button onClick={() => setSidebar(!sidebar)} className="p-2 border-t border-[#2f2f2f] text-[#8e8e8e] hover:text-white text-xs text-center">
          {sidebar ? '◀' : '▶'}
        </button>
      </div>

      {/* Main */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Dashboard (Overview) */}
        {view === 'ceo' && (
          <div className="flex-1 overflow-auto px-5 py-5">
            {/* Dashboard Header */}
            <div className="mb-6">
              <h1 className="text-2xl font-bold mb-1">📊 Dashboard</h1>
              <p className="text-[10px] text-[#8e8e8e]">AI Agency overview - Departments, tasks, agents</p>
            </div>
            {/* Stats Grid */}
            {ov && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-emerald-400">{ov.agents || 0}</div>
                  <div className="text-[10px] text-[#8e8e8e] mt-1 uppercase">Agents</div>
                </div>
                <div className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-blue-400">{ov.departments?.length || 0}</div>
                  <div className="text-[10px] text-[#8e8e8e] mt-1 uppercase">Departments</div>
                </div>
                <div className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-yellow-400">{tasks.active?.length || 0}</div>
                  <div className="text-[10px] text-[#8e8e8e] mt-1 uppercase">Active Tasks</div>
                </div>
                <div className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-purple-400">{projects.e?.length || 0}</div>
                  <div className="text-[10px] text-[#8e8e8e] mt-1 uppercase">Projects</div>
                </div>
              </div>
            )}
            {/* Department Status */}
            {ov?.department_status && (
              <div className="mb-6">
                <h2 className="text-sm font-medium text-[#8e8e8e] mb-3 uppercase">Department Status</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(ov.department_status).map(([key, dept]) => (
                    <div key={key} className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium capitalize">{key}</span>
                        <span className="text-[10px] bg-emerald-900/30 text-emerald-400 px-2 py-0.5 rounded-full">{dept.agents} agents</span>
                      </div>
                      <div className="text-[11px] text-[#8e8e8e]">Active: {dept.active_tasks} | Done: {dept.completed_tasks}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Quick Actions */}
            <div className="mt-2">
              <h2 className="text-sm font-medium text-[#8e8e8e] mb-3 uppercase">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <button onClick={() => setView('projects')} className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4 text-left hover:border-[#5f5f5f] transition-colors">
                  <div className="text-lg mb-1">📁</div>
                  <div className="font-medium text-sm">Create New Project</div>
                  <div className="text-[11px] text-[#8e8e8e]">Setup team, assign tasks</div>
                </button>
                <button onClick={() => setView('tasks')} className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4 text-left hover:border-[#5f5f5f] transition-colors">
                  <div className="text-lg mb-1">📋</div>
                  <div className="font-medium text-sm">View Tasks</div>
                  <div className="text-[11px] text-[#8e8e8e]">Track ongoing work</div>
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* CEO Chat */}
        {view === 'ceo' && (
          <div className="mt-6 border-t border-[#2f2f2f] pt-5">
            <div className="px-5 py-3 bg-[#171717] rounded-xl border border-[#2f2f2f] mb-3">
              <h2 className="text-base font-semibold">🧠 CEO Atlas</h2>
              <p className="text-[10px] text-[#8e8e8e]">Task batlo, department ko assign karega</p>
            </div>
            <div className="px-5 py-3 space-y-3 max-h-[400px] overflow-auto">
              {ceoMsgs.length === 0 && (
                <div className="flex items-center justify-center h-full"><div className="text-center">
                  <div className="text-4xl mb-3">🧠</div>
                  <p className="text-[#8e8e8e] text-sm">CEO Atlas se baat karo</p>
                </div></div>
              )}
              {ceoMsgs.map((m, i) => (
                <div key={i} className={`flex ${m.sender === 'You' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] rounded-2xl px-3.5 py-2 text-[13px] ${m.sender === 'You' ? 'bg-[#2f2f2f]' : 'bg-[#1a3a2a] text-[#e0e0e0]'}`}>
                    <div className="text-[10px] font-medium mb-0.5 opacity-60">{m.sender}</div>
                    <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
                  </div>
                </div>
              ))}
              {ceoBusy && <div className="flex justify-start"><div className="bg-[#1a3a2a] rounded-2xl px-4 py-2.5"><div className="flex gap-1.5"><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce"></div><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce" style={{ animationDelay: '.15s' }}></div><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce" style={{ animationDelay: '.3s' }}></div></div></div></div>}
              <div ref={ceoRef}></div>
            </div>
            <div className="px-5 py-3 border-t border-[#2f2f2f] bg-[#171717] rounded-b-xl">
              <div className="flex gap-2">
                <input value={ceoIn} onChange={e => setCeoIn(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendCeo()} placeholder="Task likho..." className="flex-1 bg-[#2f2f2f] border border-[#3f3f3f] rounded-xl px-3.5 py-2.5 text-[13px] text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#5f5f5f]" disabled={ceoBusy} />
                <button onClick={sendCeo} className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl text-[13px] font-medium" disabled={ceoBusy}>Send</button>
              </div>
            </div>
          </div>
        )}

        {/* Department View */}
        {view === 'dept' && dept && (
          <div className="flex h-full">
            {/* Department Main Area */}
            <div className="flex-1 flex flex-col">
              {/* Department Profile Header */}
              {deptInfo && (
                <div className="px-5 py-4 border-b border-[#2f2f2f] bg-[#171717]">
                  <div className="flex items-start gap-4">
                    <div className="text-4xl">{deptInfo.icon}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h1 className="text-lg font-bold capitalize">{deptInfo.name} Department</h1>
                        <span className="bg-emerald-600/20 text-emerald-400 text-[10px] px-2 py-0.5 rounded-full font-medium">{deptInfo.agent_count} Agents</span>
                      </div>
                      <p className="text-[11px] text-[#8e8e8e] mt-0.5">{deptInfo.desc}</p>
                      <p className="text-[10px] text-[#666] mt-1">Lead: {deptInfo.lead}</p>
                    </div>
                  </div>
                  {/* Agents Row */}
                  <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
                    {(deptInfo.agents || []).map(a => (
                      <button key={a.id} onClick={() => openAgent(a.id)} className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[11px] transition-all ${selectedAgent === a.id ? 'bg-emerald-600 text-white' : 'bg-[#2f2f2f] hover:bg-[#3f3f3f] text-[#b4b4b4]'}`}>
                        <span>{a.emoji}</span>
                        <span>{a.name}</span>
                        <span className="text-[9px] opacity-60">({a.role})</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Agent Detail Panel */}
              {agentDetail ? (
                <div className="flex-1 overflow-auto px-5 py-5">
                  <div className="max-w-3xl mx-auto">
                    <button onClick={() => setAgentDetail(null)} className="text-[#8e8e8e] hover:text-white text-[11px] mb-4 flex items-center gap-1">← Back to Chat</button>
                    <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-5">
                      {/* Agent Header */}
                      <div className="flex items-center gap-4 mb-5">
                        <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center text-2xl">{agentDetail.emoji}</div>
                        <div>
                          <h2 className="text-xl font-bold">{agentDetail.name}</h2>
                          <p className="text-[11px] text-[#8e8e8e]">{agentDetail.role} • {agentDetail.department_name} Department</p>
                          <span className="inline-block mt-1 bg-emerald-600/20 text-emerald-400 text-[10px] px-2 py-0.5 rounded-full">{agentDetail.status}</span>
                        </div>
                      </div>

                      {/* Bio */}
                      <div className="mb-5">
                        <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-1">Bio</h3>
                        <p className="text-[13px] text-[#b4b4b4]">{agentDetail.bio}</p>
                      </div>

                      {/* Skills */}
                      <div className="mb-5">
                        <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">Skills</h3>
                        <div className="flex flex-wrap gap-1.5">
                          {agentDetail.skills.map((s, i) => (
                            <span key={i} className="bg-[#2f2f2f] text-[#e0e0e0] text-[11px] px-2.5 py-1 rounded-lg">{s}</span>
                          ))}
                        </div>
                      </div>

                      {/* Capabilities */}
                      <div className="mb-5">
                        <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">Capabilities</h3>
                        <div className="flex flex-wrap gap-1.5">
                          {agentDetail.capabilities.map((c, i) => (
                            <span key={i} className="bg-blue-600/15 text-blue-400 text-[11px] px-2.5 py-1 rounded-lg">{c}</span>
                          ))}
                        </div>
                      </div>

                      {/* Tech Stack */}
                      <div className="mb-5">
                        <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">Tech Stack</h3>
                        <div className="flex flex-wrap gap-1.5">
                          {agentDetail.tech_stack.map((t, i) => (
                            <span key={i} className="bg-purple-600/15 text-purple-400 text-[11px] px-2.5 py-1 rounded-lg font-mono">{t}</span>
                          ))}
                        </div>
                      </div>

                      {/* System Prompt */}
                      <div>
                        <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">System Prompt</h3>
                        <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[#2f2f2f]">
                          <pre className="text-[11px] text-[#8e8e8e] whitespace-pre-wrap font-mono">{agentDetail.system_prompt}</pre>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* Department Chat */
                <div className="flex flex-col h-full">
                  {/* Dept Profile Button */}
                  <div className="px-5 py-2 border-b border-[#2f2f2f]">
                    <button onClick={() => {
                      if(dept === 'web') { setShowDeptProfile(true); }
                    }} className="text-[11px] text-[#8e8e8e] hover:text-emerald-400 flex items-center gap-1">
                      👁️ View Department Profile
                    </button>
                  </div>
                  {/* Web Dept Chat */}
                  {dept === 'web' ? (
                    <>
                    <div className="flex flex-col h-full">
                      {/* Brain Toggle Button */}
                      <div className="px-5 py-2 border-b border-[#2f2f2f] flex items-center justify-between bg-[#0d2818]">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">🧠</span>
                          <span className="text-[11px] text-[#b4b4b4]">Web Department Brain</span>
                        </div>
                        <div className="flex gap-1">
                          <button onClick={() => setShowBrainPanel(!showBrainPanel)} className={`text-[10px] px-3 py-1 rounded-lg font-medium ${showBrainPanel ? 'bg-emerald-600 text-white' : 'bg-[#2f2f2f] text-[#b4b4b4] hover:text-white'}`}>
                            {showBrainPanel ? 'Hide Brain' : 'Show Brain'}
                          </button>
                        </div>
                      </div>
                      {/* Web Agents Row */}
                      <div className="px-5 py-2 border-b border-[#2f2f2f] flex gap-2 overflow-x-auto">
                        {webAgents.map((a, i) => (
                          <button key={a.id} onClick={() => openWebAgentProfile(['ui_designer','frontend_developer','backend_developer','api_manager','seo','performance','qa_tester','coordinator'][i])} className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-[11px] flex items-center gap-1.5 ${selectedWebAgent === a.id ? 'bg-emerald-600 text-white' : 'bg-[#1a3a2a] text-[#ccc] hover:bg-[#2a4a3a]'}`}>
                            <span>{['🎨','💻','⚙️','🔌','🔍','⚡','🧪','📋'][i]}</span>
                            <span>{a.name}</span>
                            <span className={`w-1.5 h-1.5 rounded-full ${a.status === 'active' ? 'bg-emerald-400' : 'bg-yellow-400'}`}></span>
                          </button>
                        ))}
                      </div>
                      {/* Web Chat Messages */}
                      <div className="flex-1 overflow-auto px-5 py-3 space-y-3">
                        {webChatMsgs.length === 0 && (
                          <div className="flex items-center justify-center h-full"><div className="text-center">
                            <div className="text-4xl mb-3">🤖</div>
                            <p className="text-[#8e8e8e] text-sm">Web Department se baat karo</p>
                            <p className="text-[#666] text-[11px] mt-1">8 agents ready to help</p>
                          </div></div>
                        )}
                        {webChatMsgs.map((m, i) => (
                          <div key={i} className={`flex ${m.sender === 'You' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[70%] rounded-2xl px-3.5 py-2 text-[13px] ${m.sender === 'You' ? 'bg-[#2f2f2f]' : 'bg-[#1a3a2a] text-[#e0e0e0]'}`}>
                              <div className="text-[10px] font-medium mb-0.5 opacity-60">{m.sender}</div>
                              <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
                            </div>
                          </div>
                        ))}
                        {webChatBusy && <div className="flex justify-start"><div className="bg-[#1a3a2a] rounded-2xl px-4 py-2.5"><div className="flex gap-1.5"><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce"></div><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce" style={{animationDelay:'.15s'}}></div><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce" style={{animationDelay:'.3s'}}></div></div></div></div>}
                      </div>
                      {/* Web Task Input */}
                      <div className="px-5 py-2 border-t border-[#2f2f2f] bg-[#171717]">
                        {webTaskResult && <div className="mb-2 text-[10px] text-emerald-400">✅ Task #{webTaskResult.task_id} assigned</div>}
                        <div className="flex gap-2 mb-2">
                          <input value={webTaskIn} onChange={e => setWebTaskIn(e.target.value)} onKeyDown={e => e.key === 'Enter' && assignWebTask()} placeholder="Task assign karo web department ko..." className="flex-1 bg-[#1a3a2a] border border-[#2a4a3a] rounded-lg px-3 py-1.5 text-[11px] text-white placeholder-[#8e8e8e] focus:outline-none"/>
                          <button onClick={assignWebTask} className="bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-[11px] font-medium">Assign</button>
                        </div>
                      </div>
                      {/* Web Chat Input */}
                      <div className="px-5 py-3 border-t border-[#2f2f2f] bg-[#171717]">
                        <div className="flex gap-2">
                          <input value={webChatIn} onChange={e => setWebChatIn(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendWebChat()} placeholder="Web Department se baat karo..." className="flex-1 bg-[#2f2f2f] border border-[#3f3f3f] rounded-xl px-3.5 py-2.5 text-[13px] text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#5f5f5f]" disabled={webChatBusy}/>
                          <button onClick={sendWebChat} className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl text-[13px] font-medium" disabled={webChatBusy}>Send</button>
                        </div>
                      </div>
                    </div>

                    {/* Brain Panel */}
                    {showBrainPanel && (
                      <div className="w-96 bg-[#0d2818] border-l border-[#2f2f2f] flex flex-col overflow-auto">
                        <div className="px-4 py-3 border-b border-[#2f2f2f]">
                          <h3 className="text-sm font-bold text-emerald-400">🧠 Brain Panel</h3>
                          <p className="text-[10px] text-[#8e8e8e]">Sochta hai, plan banata hai, execute karta hai</p>
                        </div>
                        {/* Mode Toggle */}
                        <div className="px-4 py-2 flex gap-1">
                          <button onClick={() => setBrainMode('analyze')} className={`flex-1 text-[10px] py-1.5 rounded-lg font-medium ${brainMode === 'analyze' ? 'bg-emerald-600 text-white' : 'bg-[#1a3a2a] text-[#b4b4b4]'}`}>
                            🔍 Analyze Only
                          </button>
                          <button onClick={() => setBrainMode('execute')} className={`flex-1 text-[10px] py-1.5 rounded-lg font-medium ${brainMode === 'execute' ? 'bg-emerald-600 text-white' : 'bg-[#1a3a2a] text-[#b4b4b4]'}`}>
                            🚀 Execute
                          </button>
                        </div>
                        {/* Task Input */}
                        <div className="px-4 py-2 space-y-2">
                          <input value={brainTaskTitle} onChange={e => setBrainTaskTitle(e.target.value)} placeholder="Task title..." className="w-full bg-[#1a3a2a] border border-[#2a4a3a] rounded-lg px-3 py-2 text-[11px] text-white placeholder-[#666] focus:outline-none focus:border-emerald-600" />
                          <textarea value={brainTaskDesc} onChange={e => setBrainTaskDesc(e.target.value)} placeholder="Task description - kya banana hai..." className="w-full bg-[#1a3a2a] border border-[#2a4a3a] rounded-lg px-3 py-2 text-[11px] text-white placeholder-[#666] focus:outline-none focus:border-emerald-600 resize-none h-20" />
                          <button
                            onClick={() => brainMode === 'analyze' ? runBrainAnalyze() : runBrainExecute()}
                            disabled={brainThinking || !brainTaskTitle.trim()}
                            className={`w-full py-2 rounded-lg text-[11px] font-bold ${brainThinking ? 'bg-[#2f2f2f] text-[#666]' : 'bg-emerald-600 hover:bg-emerald-500 text-white'}`}>
                            {brainThinking ? '🧠 Thinking...' : brainMode === 'analyze' ? '🔍 Analyze Task' : '🚀 Execute Task'}
                          </button>
                        </div>
                        {/* Brain Result */}
                        <div className="flex-1 overflow-auto px-4 py-2">
                          {brainResult && (
                            <div className="space-y-2">
                              {/* Analysis Summary */}
                              {brainResult.analysis_summary && (
                                <div className="bg-[#1a3a2a] rounded-lg p-3">
                                  <h4 className="text-[10px] font-semibold text-emerald-400 mb-2">📊 Analysis</h4>
                                  <div className="grid grid-cols-2 gap-1.5 text-[9px]">
                                    <div className="text-[#8e8e8e]">Types:</div>
                                    <div className="text-white">{(brainResult.analysis_summary.detected_types || []).join(', ')}</div>
                                    <div className="text-[#8e8e8e]">Complexity:</div>
                                    <div className="text-white capitalize">{brainResult.analysis_summary.complexity}</div>
                                    <div className="text-[#8e8e8e]">Effort:</div>
                                    <div className="text-white">{brainResult.analysis_summary.effort}</div>
                                  </div>
                                </div>
                              )}
                              {/* Workflow */}
                              {brainResult.workflow && (
                                <div className="bg-[#1a3a2a] rounded-lg p-3">
                                  <h4 className="text-[10px] font-semibold text-emerald-400 mb-2">🔄 Workflow</h4>
                                  <div className="flex flex-wrap gap-1">
                                    {brainResult.workflow.map((agentKey, i) => {
                                      const iconMap = { coordinator: '📋', ui_designer: '🎨', frontend_developer: '💻', backend_developer: '⚙️', api_manager: '🔌', seo: '🔍', performance: '⚡', qa_tester: '🧪' };
                                      const isLast = i === brainResult.workflow.length - 1;
                                      return (
                                        <span key={i} className="inline-flex items-center gap-1">
                                          <span className="bg-[#2a4a3a] text-[10px] px-2 py-1 rounded-full">{iconMap[agentKey] || '👤'} {agentKey}</span>
                                          {!isLast && <span className="text-[#666]">→</span>}
                                        </span>
                                      );
                                    })}
                                  </div>
                                </div>
                              )}
                              {/* Execution Steps Result */}
                              {brainResult.execution_results && (
                                <div className="space-y-1.5">
                                  <h4 className="text-[10px] font-semibold text-emerald-400">📝 Execution Results</h4>
                                  {brainResult.execution_results.map((step) => (
                                    <div key={step.step} className="bg-[#171717] rounded-lg p-3 border border-[#2f2f2f]">
                                      <div className="flex items-center justify-between mb-1">
                                        <span className="text-[10px] font-medium text-white">Step {step.step}: {step.title}</span>
                                        <span className="text-[9px] bg-emerald-900/30 text-emerald-400 px-2 py-0.5 rounded-full">{step.quality_score}%</span>
                                      </div>
                                      <p className="text-[9px] text-[#8e8e8e] mb-1">Agent: {step.agent_name}</p>
                                      {step.output_preview && (
                                        <pre className="text-[9px] text-[#b4b4b4] font-mono whitespace-pre-wrap break-all max-h-20 overflow-auto bg-[#0d0d0d] rounded p-2">
                                          {step.output_preview}
                                        </pre>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              )}
                              {/* Full Output */}
                              {brainResult.full_output && (
                                <div className="bg-[#171717] rounded-lg p-3 border border-[#2f2f2f]">
                                  <h4 className="text-[10px] font-semibold text-emerald-400 mb-2">📄 Full Output</h4>
                                  <pre className="text-[10px] text-[#b4b4b4] font-mono whitespace-pre-wrap break-all max-h-60 overflow-auto">
                                    {brainResult.full_output}
                                  </pre>
                                </div>
                              )}
                            </div>
                          )}

                          {/* Empty Brain */}
                          {!brainResult && !brainThinking && (
                            <div className="text-center py-8">
                              <div className="text-3xl mb-3">🧠</div>
                              <p className="text-[#8e8e8e] text-[11px]">Task likho aur Brain se sochne do</p>
                              <p className="text-[#666] text-[9px] mt-1">Analyze ya Execute mode chuno</p>
                            </div>
                          )}

                          {/* Thinking Animation */}
                          {brainThinking && (
                            <div className="text-center py-8">
                              <div className="text-4xl animate-bounce mb-3">🧠</div>
                              <p className="text-[#8e8e8e] text-[11px] animate-pulse">Brain soch raha hai...</p>
                              <p className="text-[#666] text-[9px] mt-1">Analyzing → Planning → Executing</p>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    </>
                  ) : (
                    /* Other Departments - Original Chat */
                    <div className="flex flex-col h-full">
                      <div className="flex-1 overflow-auto px-5 py-3 space-y-3">
                        {deptMsgs.length === 0 && (
                          <div className="flex items-center justify-center h-full"><div className="text-center">
                            <div className="text-4xl mb-3">{deptInfo?.icon || '💬'}</div>
                            <p className="text-[#8e8e8e] text-sm capitalize">{dept} Department se baat karo</p>
                            <p className="text-[#666] text-[11px] mt-1">Lead: {deptInfo?.lead} • {deptInfo?.agent_count || 0} Agents</p>
                          </div></div>
                        )}
                        {deptMsgs.map((m, i) => (
                          <div key={i} className={`flex ${m.sender === 'You' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[70%] rounded-2xl px-3.5 py-2 text-[13px] ${m.sender === 'You' ? 'bg-[#2f2f2f]' : 'bg-[#1a2a3a] text-[#e0e0e0]'}`}>
                              <div className="text-[10px] font-medium mb-0.5 opacity-60">{m.sender}</div>
                              <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
                            </div>
                          </div>
                        ))}
                        {deptBusy && <div className="flex justify-start"><div className="bg-[#1a2a3a] rounded-2xl px-4 py-2.5"><div className="flex gap-1.5"><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce"></div><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce" style={{animationDelay:'.15s'}}></div><div className="w-1.5 h-1.5 bg-[#8e8e8e] rounded-full animate-bounce" style={{animationDelay:'.3s'}}></div></div></div></div>}
                        <div ref={deptRef}></div>
                      </div>
                      <div className="px-5 py-3 border-t border-[#2f2f2f] bg-[#171717]">
                        <div className="flex gap-2">
                          <input value={deptIn} onChange={e => setDeptIn(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendDept()} placeholder={`${dept} department se pucho...`} className="flex-1 bg-[#2f2f2f] border border-[#3f3f3f] rounded-xl px-3.5 py-2.5 text-[13px] text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#5f5f5f]" disabled={deptBusy}/>
                          <button onClick={sendDept} className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl text-[13px] font-medium" disabled={deptBusy}>Send</button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Department Profile Modal */}
              {showDeptProfile && dept === 'web' && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                  <div className="bg-[#171717] border border-[#2f2f2f] rounded-2xl w-full max-w-lg mx-4 max-h-[80vh] overflow-auto">
                    <div className="p-5 border-b border-[#2f2f2f] flex items-center justify-between">
                      <h2 className="text-lg font-bold">💻 Web Department Profile</h2>
                      <button onClick={() => setShowDeptProfile(false)} className="text-[#8e8e8e] hover:text-white">✕</button>
                    </div>
                    <div className="p-5">
                      <p className="text-[11px] text-[#8e8e8e] mb-4">8 specialized agents working together to build amazing web experiences</p>
                      <div className="space-y-2">
                        {webAgents.map((a, i) => (
                          <div key={a.id} className="bg-[#1a3a2a] rounded-lg p-3 flex items-center gap-3">
                            <div className="text-xl">{['🎨','💻','⚙️','🔌','🔍','⚡','🧪','📋'][i]}</div>
                            <div className="flex-1">
                              <div className="font-medium text-sm">{a.name}</div>
                              <div className="text-[10px] text-[#8e8e8e]">{a.role}</div>
                            </div>
                            <div className="flex gap-1 flex-wrap justify-end">
                              {a.skills.slice(0,2).map((s,j) => (<span key={j} className="bg-[#2a4a3a] text-[#8e8e8e] text-[9px] px-1.5 py-0.5 rounded">{s}</span>))}
                            </div>
                            <button onClick={() => openWebAgentProfile(['ui_designer','frontend_developer','backend_developer','api_manager','seo','performance','qa_tester','coordinator'][i])} className="text-[10px] text-emerald-400 hover:text-emerald-300">Profile →</button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Agent Profile Modal */}
              {showAgentProfile && webAgentProfile && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                  <div className="bg-[#171717] border border-[#2f2f2f] rounded-2xl w-full max-w-lg mx-4 max-h-[80vh] overflow-auto">
                    <div className="p-5 border-b border-[#2f2f2f] flex items-center justify-between">
                      <h2 className="text-lg font-bold">{webAgentProfile.name} - {webAgentProfile.role}</h2>
                      <button onClick={() => setShowAgentProfile(false)} className="text-[#8e8e8e] hover:text-white">✕</button>
                    </div>
                    <div className="p-5 space-y-4">
                      <div><h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase mb-1">Status</h3><span className={`text-xs px-2 py-1 rounded-full ${webAgentProfile.status === 'active' ? 'bg-emerald-900/30 text-emerald-400' : 'bg-yellow-900/30 text-yellow-400'}`}>{webAgentProfile.status}</span></div>
                      <div><h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase mb-1">Skills</h3><div className="flex flex-wrap gap-1">{webAgentProfile.skills.map((s,i)=>(<span key={i} className="bg-[#2f2f2f] text-[#b4b4b4] text-xs px-2 py-1 rounded">{s}</span>))}</div></div>
                      <div><h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase mb-1">Tools</h3><div className="flex flex-wrap gap-1">{webAgentProfile.tools.map((t,i)=>(<span key={i} className="bg-purple-900/30 text-purple-400 text-xs px-2 py-1 rounded">{t}</span>))}</div></div>
                      <div><h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase mb-1">System Prompt</h3><div className="bg-[#1a1a1a] rounded-lg p-3 text-[11px] text-[#8e8e8e] whitespace-pre-wrap font-mono leading-relaxed max-h-40 overflow-auto">{webAgentProfile.system_prompt}</div></div>
                      <div><h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase mb-1">Execution Steps</h3>{webAgentProfile.execution_steps.map((s,i)=>(<div key={i} className="text-[11px] text-[#8e8e8e] py-0.5">{s}</div>))}</div>
                      <div className="grid grid-cols-2 gap-3"><div className="bg-[#1a3a2a] rounded-lg p-3 text-center"><div className="text-xl font-bold">{webAgentProfile.tasks_completed}</div><div className="text-[10px] text-[#8e8e8e]">Tasks</div></div><div className="bg-[#1a3a2a] rounded-lg p-3 text-center"><div className="text-xl font-bold">{webAgentProfile.workload}</div><div className="text-[10px] text-[#8e8e8e]">Workload</div></div></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tasks */}
        {view === 'tasks' && (
          <div className="flex-1 overflow-auto px-5 py-5">
            <h1 className="text-lg font-semibold mb-5">📋 Tasks</h1>
            <div className="grid grid-cols-2 gap-5">
              <div><h2 className="text-[10px] font-medium text-[#8e8e8e] mb-2 uppercase tracking-wider">Active ({tasks.active?.length || 0})</h2>
                <div className="space-y-1.5">{tasks.active?.map((t, i) => (<div key={i} className="bg-[#2f2f2f] rounded-lg p-3 border border-[#3f3f3f]"><div className="text-[13px] font-medium">{t.title}</div><div className="text-[11px] text-[#8e8e8e] mt-0.5">{t.desc}</div><div className="flex items-center justify-between mt-2"><span className="text-[10px] bg-[#3f3f3f] px-1.5 py-0.5 rounded capitalize">{t.dept}</span><span className="text-[10px] text-[#666]">{t.status}</span></div></div>))}{!tasks.active?.length && <p className="text-[#666] text-[13px]">No active tasks</p>}</div>
              </div>
              <div><h2 className="text-[10px] font-medium text-[#8e8e8e] mb-2 uppercase tracking-wider">Done ({tasks.done?.length || 0})</h2>
                <div className="space-y-1.5">{tasks.done?.map((t, i) => (<div key={i} className="bg-[#1a2a1a] rounded-lg p-3 border border-[#2a3a2a] opacity-70"><div className="text-[13px] font-medium line-through">{t.title}</div><div className="text-[11px] text-[#666] mt-0.5">{t.desc}</div></div>))}{!tasks.done?.length && <p className="text-[#666] text-[13px]">No completed tasks</p>}</div>
              </div>
            </div>
          </div>
        )}

        {/* Projects */}
        {view === 'projects' && (
          <div className="flex-1 overflow-auto px-5 py-5">
            <div className="flex items-center justify-between mb-5">
              <h1 className="text-lg font-semibold">📁 Projects</h1>
              <button onClick={() => setNewProj(true)} className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-[13px] font-medium">+ New Project</button>
            </div>
            {newProj && (
              <div className="bg-[#2f2f2f] rounded-xl p-4 border border-[#3f3f3f] mb-4">
                <div className="flex gap-2">
                  <input value={newProjName} onChange={e => setNewProjName(e.target.value)} placeholder="Project name..." className="flex-1 bg-[#171717] border border-[#3f3f3f] rounded-lg px-3 py-2 text-[13px] text-white placeholder-[#8e8e8e] focus:outline-none" />
                  <button onClick={createProject} className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-[13px]">Create</button>
                  <button onClick={() => setNewProj(false)} className="bg-[#3f3f3f] text-white px-4 py-2 rounded-lg text-[13px]">Cancel</button>
                </div>
                <div className="mt-2 flex gap-2 items-center">
                  <span className="text-[11px] text-[#8e8e8e]">Your name:</span>
                  <input value={projUser} onChange={e => setProjUser(e.target.value)} className="bg-[#171717] border border-[#3f3f3f] rounded px-2 py-1 text-[11px] text-white w-32 focus:outline-none" />
                </div>
              </div>
            )}
            {!curProj ? (
              <div className="grid grid-cols-2 gap-4">{projects.e?.map(p => (
                <div key={p.id} onClick={() => { setCurProj(p.id); setProjChat(p.chat || []) }} className="bg-[#2f2f2f] rounded-xl p-4 border border-[#3f3f3f] cursor-pointer hover:border-[#5f5f5f] transition-colors">
                  <div className="text-[13px] font-medium">{p.name}</div>
                  <div className="text-[11px] text-[#8e8e8e] mt-1">{p.members?.length || 0} members</div>
                  <div className="text-[10px] text-[#666] mt-1">{p.chat?.length || 0} messages</div>
                </div>
              ))}{!projects.e?.length && <p className="text-[#666] text-[13px] col-span-2 text-center py-8">No projects yet</p>}</div>
            ) : (
              <div className="flex flex-col h-[calc(100vh-180px)]">
                {(() => { const pr = projects.e?.find(x => x.id === curProj); return (<>
                  <div className="flex items-center justify-between mb-3">
                    <div><h2 className="text-base font-semibold">{pr?.name}</h2><p className="text-[10px] text-[#8e8e8e]">{pr?.members?.length || 0} members</p></div>
                    <div className="flex gap-2">
                      <button onClick={aiTasks} className="bg-purple-600 hover:bg-purple-500 text-white px-3 py-1.5 rounded-lg text-[11px]">🤖 AI Create Tasks</button>
                      <button onClick={() => { setCurProj(null); setProjChat([]) }} className="bg-[#3f3f3f] text-white px-3 py-1.5 rounded-lg text-[11px]">Back</button>
                    </div>
                  </div>
                  <div className="flex-1 overflow-auto bg-[#171717] rounded-xl border border-[#2f2f2f] p-3 space-y-2 mb-3">
                    {projChat?.map((c, i) => (<div key={i} className={`flex ${c.user === projUser ? 'justify-end' : 'justify-start'}`}><div className={`max-w-[70%] rounded-xl px-3 py-2 text-[13px] ${c.user === projUser ? 'bg-[#2f2f2f]' : 'bg-[#1a2a3a]'}`}><div className="text-[10px] font-medium mb-0.5 opacity-60">{c.user}</div><div>{c.msg}</div></div></div>))}
                    {!projChat?.length && <p className="text-[#666] text-center py-8 text-[13px]">Start chatting. AI will create tasks from this chat.</p>}
                    <div ref={projRef}></div>
                  </div>
                  <div className="flex gap-2">
                    <input value={projIn} onChange={e => setProjIn(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendProjChat()} placeholder="Type message..." className="flex-1 bg-[#2f2f2f] border border-[#3f3f3f] rounded-xl px-3.5 py-2.5 text-[13px] text-white placeholder-[#8e8e8e] focus:outline-none" />
                    <button onClick={sendProjChat} className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl text-[13px] font-medium">Send</button>
                  </div>
                </>); })()}
              </div>
            )}
          </div>
        )}

        {/* Logs */}
        {view === 'logs' && (
          <div className="flex-1 overflow-auto px-5 py-5">
            <h1 className="text-lg font-semibold mb-5">📝 System Logs</h1>
            <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] overflow-hidden">
              <div className="max-h-[500px] overflow-auto">{logs.e?.slice().reverse().map((l, i) => (
                <div key={i} className="px-3 py-1.5 border-b border-[#2f2f2f] text-[11px] font-mono flex gap-3">
                  <span className="text-[#666] whitespace-nowrap">{new Date(l.t).toLocaleTimeString()}</span>
                  <span className="text-emerald-400">{l.ev}</span>
                  <span className="text-[#8e8e8e] truncate">{JSON.stringify(l.d)}</span>
                </div>
              ))}{!logs.e?.length && <p className="text-[#666] text-center py-8 text-[13px]">No logs</p>}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}