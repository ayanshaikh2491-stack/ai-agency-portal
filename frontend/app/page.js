'use client';
import { useState, useEffect, useRef } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL ? process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '') : '';

export default function Home() {
  const [view, setView] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  // System state
  const [overview, setOverview] = useState(null);
  const [agents, setAgents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [tasks, setTasks] = useState({ active: [], done: [] });
  const [projects, setProjects] = useState({ e: [] });
  const [logs, setLogs] = useState({ e: [] });
  const [errors, setErrors] = useState([]);

  // CEO input & project creation
  const [ceoInput, setCeoInput] = useState('');
  const [ceoBusy, setCeoBusy] = useState(false);
  const [ceoHistory, setCeoHistory] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);
  const [projectTasks, setProjectTasks] = useState([]);

  // Agent tracking
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentDetail, setAgentDetail] = useState(null);
  const [selectedDept, setSelectedDept] = useState(null);
  const [deptDetail, setDeptDetail] = useState(null);

  // Execution tracking
  const [executionQueue, setExecutionQueue] = useState([]);
  const [runningTasks, setRunningTasks] = useState([]);
  const [selectedTask, setSelectedTask] = useState(null);

  // Polling interval (5s for live updates)
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [ov, ag, dp, tk, pj, lg] = await Promise.all([
        fetch(API + '/api/overview').then(r => r.json()).catch(() => null),
        fetch(API + '/api/agents').then(r => r.json()).catch(() => []),
        fetch(API + '/api/departments').then(r => r.json()).catch(() => []),
        fetch(API + '/api/tasks').then(r => r.json()).catch(() => ({ active: [], done: [] })),
        fetch(API + '/api/projects').then(r => r.json()).catch(() => ({ e: [] })),
        fetch(API + '/api/logs').then(r => r.json()).catch(() => ({ e: [] }))
      ]);
      if (ov) setOverview(ov);
      setAgents(Array.isArray(ag) ? ag : []);
      setDepartments(Array.isArray(dp) ? dp : []);
      setTasks(tk || { active: [], done: [] });
      setProjects(pj || { e: [] });
      setLogs(lg || { e: [] });
      setLoading(false);

      // Update running tasks
      setRunningTasks((tk?.active || []).filter(t => t.status === 'running'));
      // Extract errors from logs
      const errs = (lg?.e || []).filter(l => l.ev?.includes('error') || l.ev?.includes('failed')).slice(-10);
      setErrors(errs);

    } catch (e) {
      setLoading(false);
    }
  };

  // CEO Chat - creates structured tasks & projects
  const sendCeo = async () => {
    if (!ceoInput.trim() || ceoBusy) return;
    const msg = ceoInput;
    setCeoInput('');
    setCeoBusy(true);

    const userMsg = { role: 'user', content: msg, sender: 'You' };
    setCeoHistory(prev => [...prev, userMsg]);

    try {
      const hist = ceoHistory.slice(-8).map(m => ({ role: m.sender === 'You' ? 'user' : 'assistant', content: m.content }));

      // Step 1: Get CEO analysis of the request
      const analysisRes = await fetch(API + '/api/chat/ceo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: `Analyze this request and tell me what needs to be done, which departments to assign, and what the project should include: ${msg}`, history: hist })
      });

      if (!analysisRes.ok) throw new Error('Failed to connect');

      const analysisData = await analysisRes.json();
      const aiResponse = analysisData.response;

      // Step 2: Create a project from the request
      const projectName = msg.slice(0, 50) + (msg.length > 50 ? '...' : '');
      const projectRes = await fetch(API + '/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: projectName, members: ['User'], description: msg })
      });

      let project = null;
      if (projectRes.ok) {
        project = await projectRes.json();
        setCurrentProject(project);
      }

      // Step 3: Create tasks for relevant departments
      const deptMapping = {
        'website': 'web', 'web': 'web', 'site': 'web', 'landing': 'web',
        'seo': 'seo', 'ranking': 'seo', 'google': 'seo',
        'marketing': 'marketing', 'ads': 'marketing', 'campaign': 'marketing',
        'social': 'social_media', 'content': 'social_media', 'reels': 'social_media'
      };

      const lowerMsg = msg.toLowerCase();
      const detectedDepts = Object.entries(deptMapping)
        .filter(([key]) => lowerMsg.includes(key))
        .map(([, value]) => value);

      if (detectedDepts.length > 0) {
        for (const dept of detectedDepts) {
          const taskTitle = `${msg.slice(0, 40)} [${dept}]`;

          // Create task
          await fetch(API + '/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              title: taskTitle,
              description: msg,
              department: dept,
              project_id: project?.id
            })
          });

          // Assign to department via flow
          await fetch(API + `/api/flow/ceo-to-dept/${dept}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              title: taskTitle,
              description: msg,
              department: dept,
              project_id: project?.id
            })
          });
        }

        // Add system message about task creation
        const sysMsg = {
          role: 'assistant',
          content: `✅ Request understood. Created project "${projectName}" and assigned tasks to: ${detectedDepts.join(', ')}. Track progress in the Tasks or Dashboard tab.`,
          sender: 'System'
        };
        setCeoHistory(prev => [...prev, { ...analysisData }, sysMsg]);
      } else {
        setCeoHistory(prev => [...prev, analysisData]);
      }

      // Reload data
      loadData();
    } catch (e) {
      console.error('CEO Error:', e);
      setCeoHistory(prev => [...prev, {
        role: 'assistant',
        content: `Error: Could not connect. Make sure backend is running and GROQ_API_KEY is set.`,
        sender: 'System'
      }]);
    }

    setCeoBusy(false);
  };

  const navItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'ceo', icon: '🎯', label: 'CEO Atlas' },
    { id: 'tasks', icon: '📋', label: 'Tasks' },
    { id: 'projects', icon: '📁', label: 'Projects' },
    { id: 'agents', icon: '🤖', label: 'Agents' },
    { id: 'logs', icon: '📝', label: 'Logs' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#1a1a1a] flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-pulse">🤖</div>
          <p className="text-[#8e8e8e]">Loading AI Agency System...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1a1a1a] flex">
      {/* Sidebar */}
      <div className="w-16 min-h-screen bg-[#111] flex flex-col items-center py-4 border-r border-[#2f2f2f]">
        <div className="text-xl mb-6">🏢</div>
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setView(item.id)}
            title={item.label}
            className={`w-10 h-10 rounded-lg mb-2 flex items-center justify-center transition-all ${view === item.id ? 'bg-emerald-600' : 'hover:bg-[#2f2f2f]'}`}
          >
            <span>{item.icon}</span>
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Top Bar - System Status */}
        <div className="h-12 bg-[#111] border-b border-[#2f2f2f] flex items-center px-5 justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-sm font-semibold capitalize">{navItems.find(n => n.id === view)?.icon} {navItems.find(n => n.id === view)?.label}</h1>
            {overview && (
              <div className="flex items-center gap-4 text-[10px] text-[#8e8e8e]">
                <span className="flex items-center gap-1">🤖 {overview.agents || 0} Agents</span>
                <span className="flex items-center gap-1">📋 {overview.active_tasks || 0} Tasks</span>
                <span className="flex items-center gap-1">📁 {overview.projects || 0} Projects</span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  System Running
                </span>
              </div>
            )}
          </div>
          <div className="text-[10px] text-[#666]">v6.0 — AI Agency Portal</div>
        </div>

        {/* Dashboard */}
        {view === 'dashboard' && <DashboardView overview={overview} agents={agents} departments={departments} tasks={tasks} projects={projects} runningTasks={runningTasks} errors={errors} logs={logs} onView={setView} />}

        {/* CEO Atlas */}
        {view === 'ceo' && (
          <CEOView
            ceoInput={ceoInput}
            setCeoInput={setCeoInput}
            ceoBusy={ceoBusy}
            ceoHistory={ceoHistory}
            ceoHistoryRef={null}
            sendCeo={sendCeo}
            currentProject={currentProject}
          />
        )}

        {/* Tasks */}
        {view === 'tasks' && <TasksView tasks={tasks} selectedTask={selectedTask} setSelectedTask={setSelectedTask} />}

        {/* Projects */}
        {view === 'projects' && <ProjectsView projects={projects} currentProject={currentProject} setCurrentProject={setCurrentProject} />}

        {/* Agents */}
        {view === 'agents' && <AgentsView agents={agents} departments={departments} selectedAgent={selectedAgent} setSelectedAgent={setSelectedAgent} selectedDept={selectedDept} setSelectedDept={setSelectedDept} agentDetail={agentDetail} setAgentDetail={setAgentDetail} deptDetail={deptDetail} setDeptDetail={setDeptDetail} />}

        {/* Logs */}
        {view === 'logs' && <LogsView logs={logs} errors={errors} />}
      </div>
    </div>
  );
}

// ============================================================
// SUB-COMPONENTS
// ============================================================

function DashboardView({ overview, agents, departments, tasks, projects, runningTasks, errors, logs, onView }) {
  return (
    <div className="flex-1 overflow-auto px-5 py-5 space-y-5">
      {/* Status Cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard icon="🤖" label="Total Agents" value={overview?.agents || 0} color="emerald" />
        <StatCard icon="📋" label="Active Tasks" value={tasks.active?.length || 0} color="blue" />
        <StatCard icon="✅" label="Completed" value={tasks.done?.length || 0} color="green" />
        <StatCard icon="📁" label="Projects" value={projects.e?.length || 0} color="purple" />
      </div>

      {/* Running Tasks & Errors */}
      <div className="grid grid-cols-2 gap-5">
        {/* Running Tasks */}
        <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
          <h2 className="text-sm font-semibold mb-3">⚡ Running Tasks</h2>
          {runningTasks.length > 0 ? (
            <div className="space-y-2">
              {runningTasks.map((t, i) => (
                <div key={i} className="bg-[#1a2a3a] rounded-lg p-3 border border-[#2a3a4a]">
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] font-medium truncate flex-1">{t.title}</span>
                    <span className="ml-2 text-[10px] bg-blue-600/20 text-blue-400 px-2 py-0.5 rounded-full animate-pulse">Running</span>
                  </div>
                  <div className="text-[10px] text-[#8e8e8e] mt-1 capitalize">{t.department || t.dept}</div>
                  <div className="w-full bg-[#2f2f2f] h-1 rounded-full mt-2">
                    <div className="bg-blue-500 h-1 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[#666] text-[13px] py-4 text-center">No tasks running</p>
          )}
        </div>

        {/* Errors */}
        <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
          <h2 className="text-sm font-semibold mb-3">🚨 Errors</h2>
          {errors.length > 0 ? (
            <div className="space-y-2">
              {errors.map((e, i) => (
                <div key={i} className="bg-[#2a1a1a] rounded-lg p-3 border border-[#3a2a2a]">
                  <div className="text-[10px] text-red-400 font-mono">{e.ev}</div>
                  <div className="text-[10px] text-[#8e8e8e] mt-1 font-mono truncate">{JSON.stringify(e.d)}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[#666] text-[13px] py-4 text-center">No errors</p>
          )}
        </div>
      </div>

      {/* Departments Overview */}
      <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
        <h2 className="text-sm font-semibold mb-3">🏢 Departments</h2>
        <div className="grid grid-cols-4 gap-3">
          {departments.map((d, i) => (
            <button key={i} onClick={() => onView('agents')} className="bg-[#1a2a1a] rounded-lg p-3 border border-[#2a3a2a] hover:border-emerald-600 transition-colors text-left">
              <div className="text-2xl mb-1">{d.icon || d.emoji || '📋'}</div>
              <div className="text-[13px] font-medium capitalize">{d.name}</div>
              <div className="text-[10px] text-[#8e8e8e] mt-0.5">{d.agent_count || d.agents?.length || 0} Agents</div>
              <div className="text-[9px] text-[#666] mt-1 truncate">{d.desc || d.description || ''}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Activity (Logs) */}
      <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
        <h2 className="text-sm font-semibold mb-3">📜 Recent Activity</h2>
        <div className="space-y-1 max-h-48 overflow-auto">
          {(logs.e || []).slice().reverse().slice(0, 15).map((l, i) => (
            <div key={i} className="flex items-center gap-3 text-[10px] font-mono py-1 px-2 hover:bg-[#2f2f2f] rounded">
              <span className="text-[#666] w-20">{new Date(l.t).toLocaleTimeString()}</span>
              <span className="text-emerald-400 w-28">{l.ev}</span>
              <span className="text-[#8e8e8e] truncate flex-1">{JSON.stringify(l.d).slice(0, 60)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CEOView({ ceoInput, setCeoInput, ceoBusy, ceoHistory, ceoHistoryRef, sendCeo, currentProject }) {
  const scrollRef = useRef(null);
  useEffect(() => { scrollRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [ceoHistory]);

  return (
    <div className="flex-1 flex flex-col">
      {/* System Status Bar */}
      <div className="px-5 py-3 border-b border-[#2f2f2f] bg-[#0d2818]">
        <div className="flex items-center gap-3">
          <span className="text-lg">🎯</span>
          <div>
            <h2 className="text-sm font-semibold">CEO Atlas — Task Controller</h2>
            <p className="text-[10px] text-[#8e8e8e]">Describe what you need. Atlas will analyze, create project, assign tasks to departments.</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-auto px-5 py-5 space-y-3">
        {ceoHistory.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-5xl mb-4">🎯</div>
              <p className="text-[#b4b4b4] text-sm">Tell Atlas what you need to build</p>
              <div className="mt-4 text-[11px] text-[#666] space-y-1">
                <p>Examples:</p>
                <p className="text-[#8e8e8e]">"Banao ek e-commerce website for clothing"</p>
                <p className="text-[#8e8e8e]">"SEO optimize karo meri website"</p>
                <p className="text-[#8e8e8e]">"Marketing campaign chahiye product launch ke liye"</p>
              </div>
            </div>
          </div>
        )}
        {ceoHistory.map((m, i) => (
          <div key={i} className={`flex ${m.sender === 'You' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-[13px] ${
              m.sender === 'System' ? 'bg-[#1a3a1a] border border-emerald-600/30 text-emerald-400' :
              m.sender === 'You' ? 'bg-[#2f2f2f]' : 'bg-[#0d2818] text-[#e0e0e0]'
            }`}>
              <div className="text-[10px] font-medium mb-1 opacity-60">{m.sender}</div>
              <div className="whitespace-pre-wrap leading-relaxed">{m.content || m.response}</div>
            </div>
          </div>
        ))}
        {ceoBusy && (
          <div className="flex justify-start">
            <div className="bg-[#0d2818] rounded-2xl px-5 py-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                <span className="text-[11px] text-[#8e8e8e]">Atlas is analyzing and creating tasks...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef}></div>
      </div>

      {/* Input */}
      <div className="px-5 py-4 border-t border-[#2f2f2f] bg-[#171717]">
        <div className="flex gap-2">
          <textarea
            value={ceoInput}
            onChange={e => setCeoInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendCeo(); } }}
            placeholder="Describe your project or task..."
            className="flex-1 bg-[#2f2f2f] border border-[#3f3f3f] rounded-xl px-4 py-3 text-[13px] text-white placeholder-[#8e8e8e] focus:outline-none focus:border-emerald-600 resize-none h-12"
            disabled={ceoBusy}
          />
          <button
            onClick={sendCeo}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-xl text-[13px] font-medium disabled:opacity-50"
            disabled={ceoBusy}
          >
            🚀 Execute
          </button>
        </div>
      </div>
    </div>
  );
}

function TasksView({ tasks, selectedTask, setSelectedTask }) {
  return (
    <div className="flex-1 overflow-auto px-5 py-5">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-semibold">📋 Tasks</h1>
        <div className="text-[10px] text-[#8e8e8e]">
          {tasks.active?.length || 0} Active · {tasks.done?.length || 0} Done
        </div>
      </div>

      <div className="grid grid-cols-2 gap-5">
        {/* Active Tasks */}
        <div>
          <h2 className="text-[10px] font-medium text-[#8e8e8e] mb-3 uppercase tracking-wider">⚡ Active Tasks</h2>
          <div className="space-y-2">
            {tasks.active?.map((t, i) => (
              <div
                key={i}
                onClick={() => setSelectedTask(selectedTask === i ? null : i)}
                className={`rounded-lg p-3 border cursor-pointer transition-all ${
                  t.status === 'running' ? 'bg-[#1a2a3a] border-blue-600/30' :
                  'bg-[#2f2f2f] border-[#3f3f3f] hover:border-[#5f5f5f]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-medium truncate flex-1">{t.title}</span>
                  <span className={`ml-2 text-[9px] px-2 py-0.5 rounded-full ${
                    t.status === 'running' ? 'bg-blue-600/20 text-blue-400 animate-pulse' :
                    t.status === 'done' ? 'bg-emerald-600/20 text-emerald-400' :
                    'bg-[#3f3f3f] text-[#8e8e8e]'
                  }`}>{t.status || 'pending'}</span>
                </div>
                {t.description && <div className="text-[10px] text-[#8e8e8e] mt-1 truncate">{t.description}</div>}
                {t.department && <div className="text-[9px] text-[#666] mt-1 capitalize">Dept: {t.department}</div>}
                {selectedTask === i && (
                  <div className="mt-3 pt-3 border-t border-[#3f3f3f] text-[10px] space-y-1">
                    {Object.entries(t).filter(([k]) => !['id','title'].includes(k)).slice(0, 5).map(([k, v]) => (
                      <div key={k} className="flex gap-2">
                        <span className="text-[#8e8e8e] w-24">{k}:</span>
                        <span className="text-white truncate">{typeof v === 'object' ? JSON.stringify(v).slice(0, 50) : String(v)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {!tasks.active?.length && <p className="text-[#666] text-[13px] py-4 text-center">No active tasks. Use CEO Atlas to create tasks.</p>}
          </div>
        </div>

        {/* Done Tasks */}
        <div>
          <h2 className="text-[10px] font-medium text-[#8e8e8e] mb-3 uppercase tracking-wider">✅ Completed</h2>
          <div className="space-y-2">
            {tasks.done?.map((t, i) => (
              <div key={i} className="bg-[#1a2a1a] rounded-lg p-3 border border-[#2a3a2a] opacity-70">
                <div className="text-[13px] font-medium line-through">{t.title}</div>
                {t.description && <div className="text-[11px] text-[#666] mt-0.5">{t.description}</div>}
              </div>
            ))}
            {!tasks.done?.length && <p className="text-[#666] text-[13px] py-4 text-center">No completed tasks yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

function ProjectsView({ projects, currentProject, setCurrentProject }) {
  return (
    <div className="flex-1 overflow-auto px-5 py-5">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-semibold">📁 Projects</h1>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {projects.e?.map(p => (
          <div
            key={p.id}
            onClick={() => setCurrentProject(currentProject === p.id ? null : p.id)}
            className="bg-[#2f2f2f] rounded-xl p-4 border border-[#3f3f3f] cursor-pointer hover:border-emerald-600 transition-colors"
          >
            <div className="text-[13px] font-medium mb-1 truncate">{p.name}</div>
            <div className="text-[10px] text-[#8e8e8e]">{p.members?.length || 0} members</div>
            <div className="text-[10px] text-[#666] mt-1">{p.chat?.length || 0} messages</div>
            <div className="text-[9px] text-[#666] mt-1">{new Date(p.created).toLocaleDateString()}</div>
            {currentProject === p.id && p.desc && (
              <div className="mt-3 pt-3 border-t border-[#3f3f3f]">
                <p className="text-[10px] text-[#b4b4b4]">{p.desc}</p>
              </div>
            )}
          </div>
        ))}
        {!projects.e?.length && (
          <div className="col-span-3 text-center py-12">
            <div className="text-4xl mb-3">📁</div>
            <p className="text-[#8e8e8e] text-sm">No projects yet</p>
            <p className="text-[#666] text-[11px] mt-1">Use CEO Atlas to create your first project</p>
          </div>
        )}
      </div>
    </div>
  );
}

function AgentsView({ agents, departments, selectedAgent, setSelectedAgent, selectedDept, setSelectedDept, agentDetail, setAgentDetail, deptDetail, setDeptDetail }) {
  return (
    <div className="flex-1 overflow-auto px-5 py-5">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-semibold">🤖 Agents</h1>
        <div className="text-[10px] text-[#8e8e8e]">{agents.length || 0} Total Agents</div>
      </div>

      {/* Department Tabs */}
      <div className="flex gap-2 mb-5 overflow-x-auto">
        <button
          onClick={() => { setSelectedDept(null); setDeptDetail(null); }}
          className={`px-3 py-1.5 rounded-lg text-[11px] font-medium whitespace-nowrap ${!selectedDept ? 'bg-emerald-600 text-white' : 'bg-[#2f2f2f] text-[#b4b4b4] hover:bg-[#3f3f3f]'}`}
        >
          All Agents
        </button>
        {departments.map((d, i) => (
          <button
            key={i}
            onClick={() => { setSelectedDept(d.name); setDeptDetail(null); }}
            className={`px-3 py-1.5 rounded-lg text-[11px] font-medium whitespace-nowrap capitalize ${selectedDept === d.name ? 'bg-emerald-600 text-white' : 'bg-[#2f2f2f] text-[#b4b4b4] hover:bg-[#3f3f3f]'}`}
          >
            {d.icon || d.emoji} {d.name} ({d.agent_count || d.agents?.length || 0})
          </button>
        ))}
      </div>

      {/* Agent Detail Modal */}
      {agentDetail ? (
        <div className="max-w-2xl mx-auto">
          <button onClick={() => setAgentDetail(null)} className="text-[#8e8e8e] hover:text-white text-[11px] mb-4 flex items-center gap-1">← Back to Agents</button>
          <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-5">
            <div className="flex items-center gap-4 mb-5">
              <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center text-2xl">{agentDetail.emoji}</div>
              <div>
                <h2 className="text-xl font-bold">{agentDetail.name}</h2>
                <p className="text-[11px] text-[#8e8e8e]">{agentDetail.role} • {agentDetail.department} Department</p>
                <span className={`inline-block mt-1 text-[10px] px-2 py-0.5 rounded-full ${agentDetail.status === 'active' ? 'bg-emerald-600/20 text-emerald-400' : 'bg-yellow-600/20 text-yellow-400'}`}>{agentDetail.status}</span>
              </div>
            </div>

            {agentDetail.bio && (
              <div className="mb-5">
                <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-1">Bio</h3>
                <p className="text-[13px] text-[#b4b4b4]">{agentDetail.bio}</p>
              </div>
            )}

            {agentDetail.skills?.length > 0 && (
              <div className="mb-5">
                <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">Skills</h3>
                <div className="flex flex-wrap gap-1.5">
                  {agentDetail.skills.map((s, i) => (
                    <span key={i} className="bg-[#2f2f2f] text-[#e0e0e0] text-[11px] px-2.5 py-1 rounded-lg">{s}</span>
                  ))}
                </div>
              </div>
            )}

            {agentDetail.capabilities?.length > 0 && (
              <div className="mb-5">
                <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">Capabilities</h3>
                <div className="flex flex-wrap gap-1.5">
                  {agentDetail.capabilities.map((c, i) => (
                    <span key={i} className="bg-blue-600/15 text-blue-400 text-[11px] px-2.5 py-1 rounded-lg">{c}</span>
                  ))}
                </div>
              </div>
            )}

            {agentDetail.tech_stack?.length > 0 && (
              <div className="mb-5">
                <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">Tech Stack</h3>
                <div className="flex flex-wrap gap-1.5">
                  {agentDetail.tech_stack.map((t, i) => (
                    <span key={i} className="bg-purple-600/15 text-purple-400 text-[11px] px-2.5 py-1 rounded-lg font-mono">{t}</span>
                  ))}
                </div>
              </div>
            )}

            {agentDetail.system_prompt && (
              <div>
                <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">System Prompt</h3>
                <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[#2f2f2f]">
                  <pre className="text-[11px] text-[#8e8e8e] whitespace-pre-wrap font-mono">{agentDetail.system_prompt}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Agent Grid */
        <div className="grid grid-cols-4 gap-3">
          {agents
            .filter(a => !selectedDept || a.department === selectedDept)
            .map((a, i) => (
              <div
                key={i}
                onClick={() => { setSelectedAgent(selectedAgent === (a.name || a.id) ? null : (a.name || a.id)); }}
                className={`bg-[#171717] rounded-xl border p-4 cursor-pointer transition-all ${
                  selectedAgent === (a.name || a.id) ? 'border-emerald-600' : 'border-[#2f2f2f] hover:border-[#4f4f4f]'
                }`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-2xl">{a.emoji || '🤖'}</div>
                  <div>
                    <div className="text-[13px] font-medium truncate">{a.name || a.id}</div>
                    <div className="text-[10px] text-[#8e8e8e] capitalize">{a.role || a.department}</div>
                  </div>
                </div>
                {a.status && (
                  <div className="flex items-center gap-1 mb-2">
                    <span className={`w-2 h-2 rounded-full ${a.status === 'active' ? 'bg-emerald-400' : 'bg-yellow-400'}`}></span>
                    <span className="text-[9px] text-[#8e8e8e] capitalize">{a.status}</span>
                  </div>
                )}
                {selectedAgent === (a.name || a.id) && (
                  <button
                    onClick={(e) => { e.stopPropagation(); setAgentDetail(a); }}
                    className="mt-2 text-[10px] text-emerald-400 hover:text-emerald-300"
                  >
                    View Full Profile →
                  </button>
                )}
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}

function LogsView({ logs, errors }) {
  return (
    <div className="flex-1 overflow-auto px-5 py-5">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-lg font-semibold">📝 System Logs</h1>
        <div className="text-[10px] text-[#8e8e8e]">{logs.e?.length || 0} entries</div>
      </div>

      <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] overflow-hidden">
        <div className="max-h-[600px] overflow-auto">
          {(logs.e || []).slice().reverse().map((l, i) => (
            <div key={i} className="px-4 py-2 border-b border-[#2f2f2f] text-[10px] font-mono flex gap-3 hover:bg-[#1f1f1f]">
              <span className="text-[#666] w-20 flex-shrink-0">{new Date(l.t).toLocaleTimeString()}</span>
              <span className={`w-36 flex-shrink-0 ${l.ev?.includes('error') || l.ev?.includes('failed') ? 'text-red-400' : 'text-emerald-400'}`}>{l.ev}</span>
              <span className="text-[#8e8e8e] truncate">{JSON.stringify(l.d)}</span>
            </div>
          ))}
          {!logs.e?.length && <p className="text-[#666] text-center py-8 text-[13px]">No logs yet. Start using the system to generate logs.</p>}
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }) {
  const colors = { emerald: 'from-emerald-500/10', blue: 'from-blue-500/10', green: 'from-green-500/10', purple: 'from-purple-500/10' };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} bg-[#171717] rounded-xl border border-[#2f2f2f] p-4`}>
      <div className="text-2xl mb-2">{icon}</div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="text-[10px] text-[#8e8e8e] mt-0.5">{label}</div>
    </div>
  );
}