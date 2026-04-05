'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'

const API = 'http://localhost:8000'

export default function DashboardPage() {
  const [ov, setOv] = useState(null)
  const [tasks, setTasks] = useState({active:[], done:[]})
  const [projects, setProjects] = useState({e:[]})
  const [logs, setLogs] = useState({e:[]})
  const [sidebar, setSidebar] = useState(true)

  useEffect(() => { load(); const t = setInterval(load, 15000); return () => clearInterval(t); }, [])

  const load = async () => {
    try {
      const [o,t,p,l] = await Promise.all([
        fetch(API+'/api/overview').then(r=>r.json()).catch(()=>null),
        fetch(API+'/api/tasks').then(r=>r.json()).catch(()=>({active:[],done:[]})),
        fetch(API+'/api/projects').then(r=>r.json()).catch(()=>({e:[]})),
        fetch(API+'/api/logs').then(r=>r.json()).catch(()=>({e:[]}))
      ])
      if(o) setOv(o); setTasks(t); setProjects(p); setLogs(l);
    } catch(e) {}
  }

  const depts = [
    { name: 'web', icon: '💻', lead: 'Sara + Team', desc: '8 specialized agents for website dev', agents: 8 },
    { name: 'seo', icon: '🔍', lead: 'Kavita', desc: 'Google ranking, traffic, growth tracking', agents: 2 },
    { name: 'marketing', icon: '📢', lead: 'Neha', desc: 'Digital marketing, ads, campaigns', agents: 2 },
    { name: 'social_media', icon: '📱', lead: 'Rohan', desc: 'Content creation, reels, social media', agents: 2 }
  ]

  return (
    <div className="flex h-screen bg-[#212121] text-white">
      {/* Sidebar */}
      <div className={`${sidebar ? 'w-64' : 'w-14'} bg-[#171717] border-r border-[#2f2f2f] flex flex-col transition-all`}>
        <div className="p-3 flex items-center gap-2 border-b border-[#2f2f2f]">
          <div className="w-7 h-7 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg flex items-center justify-center font-bold text-xs">A</div>
          {sidebar && <span className="font-semibold text-sm">AI Agency v5</span>}
        </div>
        <nav className="p-1.5 space-y-0.5 flex-1 overflow-auto">
          <Link href="/ceo-chat" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
            <span>🧠</span>{sidebar && <span>CEO Chat</span>}
          </Link>
          <Link href="/dashboard" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm bg-[#2f2f2f] text-white">
            <span>📊</span>{sidebar && <span>Dashboard</span>}
          </Link>
          {sidebar && <div className="px-2.5 pt-3 pb-1 text-[10px] text-[#8e8e8e] uppercase tracking-wider font-medium">Departments</div>}
          {depts.map(d => (
            <Link key={d.name} href={`/?dept=${d.name}`} className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
              <span>{d.icon}</span>{sidebar && <span className="capitalize">{d.name}</span>}
            </Link>
          ))}
          {sidebar && <div className="px-2.5 pt-3 pb-1 text-[10px] text-[#8e8e8e] uppercase tracking-wider font-medium">System</div>}
          <Link href="/tasks" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
            <span>📋</span>{sidebar && <span>Tasks</span>}
            {sidebar && tasks.active?.length > 0 && <span className="ml-auto bg-[#3f3f3f] text-[10px] px-1.5 py-0.5 rounded-full">{tasks.active.length}</span>}
          </Link>
          <Link href="/projects" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
            <span>📁</span>{sidebar && <span>Projects</span>}
            {sidebar && projects.e?.length > 0 && <span className="ml-auto bg-[#3f3f3f] text-[10px] px-1.5 py-0.5 rounded-full">{projects.e.length}</span>}
          </Link>
          <Link href="/agents" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
            <span>🤖</span>{sidebar && <span>Agents</span>}
          </Link>
          <Link href="/settings" className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-[#b4b4b4] hover:bg-[#2f2f2f]">
            <span>⚙️</span>{sidebar && <span>Settings</span>}
          </Link>
        </nav>
        <button onClick={() => setSidebar(!sidebar)} className="p-2 border-t border-[#2f2f2f] text-[#8e8e8e] hover:text-white text-xs text-center">
          {sidebar ? '◀' : '▶'}
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="px-5 py-5">
          <div className="mb-6">
            <h1 className="text-2xl font-bold mb-1">📊 Dashboard</h1>
            <p className="text-[10px] text-[#8e8e8e]">AI Agency overview - Departments, tasks, agents</p>
          </div>
          
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4">
              <h3 className="text-sm font-medium mb-3">Recent Tasks</h3>
              {tasks.active?.slice(-5).reverse().map((t, i) => (
                <div key={i} className="bg-[#2f2f2f] rounded-lg p-2 mb-2 text-[11px]">
                  <div className="font-medium">{t.title}</div>
                  <div className="text-[#8e8e8e]">{t.desc}</div>
                </div>
              ))}
              {!tasks.active?.length && <p className="text-[#666] text-[11px]">No active tasks</p>}
            </div>
            <div className="bg-[#171717] border border-[#2f2f2f] rounded-xl p-4">
              <h3 className="text-sm font-medium mb-3">Recent Projects</h3>
              {projects.e?.slice(-5).reverse().map((p, i) => (
                <div key={i} className="bg-[#2f2f2f] rounded-lg p-2 mb-2 text-[11px]">
                  <div className="font-medium">{p.name}</div>
                  <div className="text-[#8e8e8e]">{p.members?.length || 0} members</div>
                </div>
              ))}
              {!projects.e?.length && <p className="text-[#666] text-[11px]">No projects yet</p>}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-medium text-[#8e8e8e] mb-3 uppercase">Recent Activity</h2>
            <div className="bg-[#171717] border border-[#2f2f2f] rounded-xl overflow-hidden">
              {logs.e?.slice(-10).reverse().map((l, i) => (
                <div key={i} className="px-4 py-2 border-b border-[#2f2f2f] text-[11px] flex gap-3">
                  <span className="text-[#666] whitespace-nowrap">{new Date(l.t).toLocaleTimeString()}</span>
                  <span className="text-emerald-400">{l.ev}</span>
                </div>
              ))}
              {!logs.e?.length && <p className="text-[#666] text-[11px] p-4">No logs yet</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}