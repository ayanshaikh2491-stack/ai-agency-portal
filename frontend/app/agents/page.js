'use client';
import { useState, useEffect, useRef } from 'react';
const API = 'http://localhost:8000';

export default function AgentsPage() {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentDetail, setAgentDetail] = useState(null);
  const [chatMsgs, setChatMsgs] = useState([]);
  const [chatIn, setChatIn] = useState('');
  const [busy, setBusy] = useState(false);
  const [filter, setFilter] = useState('all');
  const chatRef = useRef(null);

  useEffect(() => { load(); }, []);
  useEffect(() => { chatRef.current?.scrollIntoView({behavior:'smooth'}); }, [chatMsgs]);

  const load = async () => {
    try {
      const a = await fetch(API+'/api/agents').then(r=>r.json()).catch(()=>[]);
      setAgents(a);
    } catch(e) {}
  };

  const openAgent = async (id) => {
    setSelectedAgent(id);
    setChatMsgs([]);
    setChatIn('');
    try {
      const d = await fetch(API+`/api/agents/${id}`).then(r=>r.json()).catch(()=>null);
      setAgentDetail(d);
    } catch(e) {}
  };

  const sendChat = async () => {
    if(!chatIn.trim()||busy||!selectedAgent) return;
    const msg=chatIn; setChatIn(''); setBusy(true);
    setChatMsgs(p=>[...p,{role:'user',content:msg,sender:'You'}]);
    try {
      const hist=chatMsgs.slice(-8).map(m=>({role:m.sender==='You'?'user':'assistant',content:m.content}));
      const r=await fetch(API+`/api/chat/agent/${selectedAgent}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg,history:hist})});
      if(r.ok){const d=await r.json();setChatMsgs(p=>[...p,{role:'assistant',content:d.response,sender:d.sender}]);}
      else setChatMsgs(p=>[...p,{role:'assistant',content:'Connection error',sender:'System'}]);
    } catch(e){setChatMsgs(p=>[...p,{role:'assistant',content:'Failed to connect',sender:'System'}]);}
    setBusy(false);
  };

  const depts = [...new Set(agents.map(a=>a.dept))];
  const filtered = filter==='all' ? agents : agents.filter(a=>a.dept===filter);

  const deptColors = {
    development:'from-blue-500 to-cyan-500',
    creative:'from-pink-500 to-rose-500',
    marketing:'from-orange-500 to-amber-500',
    qa:'from-green-500 to-emerald-500',
    devops:'from-purple-500 to-violet-500',
    product:'from-indigo-500 to-blue-500',
    data:'from-teal-500 to-cyan-500',
    security:'from-red-500 to-rose-500',
    hr:'from-yellow-500 to-orange-500'
  };

  const deptIcons = {
    development:'💻',creative:'🎨',marketing:'📢',qa:'🧪',devops:'🚀',
    product:'📋',data:'📊',security:'🔒',hr:'👥'
  };

  return (
    <div className="flex h-screen bg-[#212121] text-white">
      {/* Agent List Sidebar */}
      <div className="w-72 bg-[#171717] border-r border-[#2f2f2f] flex flex-col">
        <div className="p-4 border-b border-[#2f2f2f]">
          <h1 className="text-base font-bold mb-1">🤖 Agents</h1>
          <p className="text-[10px] text-[#8e8e8e]">{agents.length} agents across {depts.length} departments</p>
        </div>
        
        {/* Filter */}
        <div className="p-2 border-b border-[#2f2f2f]">
          <div className="flex gap-1 overflow-x-auto pb-1">
            <button onClick={()=>setFilter('all')} className={`text-[10px] px-2 py-1 rounded-full whitespace-nowrap ${filter==='all'?'bg-emerald-600 text-white':'bg-[#2f2f2f] text-[#8e8e8e]'}`}>All</button>
            {depts.map(d=>(
              <button key={d} onClick={()=>setFilter(d)} className={`text-[10px] px-2 py-1 rounded-full whitespace-nowrap capitalize ${filter===d?'bg-emerald-600 text-white':'bg-[#2f2f2f] text-[#8e8e8e]'}`}>{d}</button>
            ))}
          </div>
        </div>
        
        {/* Agent List */}
        <div className="flex-1 overflow-auto p-2 space-y-1">
          {filtered.map(a=>(
            <button key={a.id} onClick={()=>openAgent(a.id)} className={`w-full flex items-center gap-3 p-2.5 rounded-lg text-left transition-all ${selectedAgent===a.id?'bg-[#2f2f2f] border border-[#3f3f3f]':'hover:bg-[#1f1f1f] border border-transparent'}`}>
              <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${deptColors[a.dept]||'from-gray-500 to-gray-600'} flex items-center justify-center text-sm flex-shrink-0`}>{a.emoji}</div>
              <div className="min-w-0 flex-1">
                <div className="text-[12px] font-medium truncate">{a.name}</div>
                <div className="text-[10px] text-[#8e8e8e] truncate">{a.role} • <span className="capitalize">{a.dept}</span></div>
              </div>
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${a.status==='active'?'bg-emerald-400':'bg-gray-500'}`}></div>
            </button>
          ))}
        </div>
      </div>
      
      {/* Main Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {!selectedAgent ? (
          /* No agent selected - show all agents grid */
          <div className="flex-1 overflow-auto px-6 py-6">
            <h2 className="text-lg font-bold mb-5">All Agents</h2>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.map(a=>(
                <button key={a.id} onClick={()=>openAgent(a.id)} className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4 text-left hover:border-[#3f3f3f] transition-all group">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${deptColors[a.dept]||'from-gray-500 to-gray-600'} flex items-center justify-center text-lg`}>{a.emoji}</div>
                    <div>
                      <div className="text-[13px] font-semibold group-hover:text-emerald-400 transition-colors">{a.name}</div>
                      <div className="text-[10px] text-[#8e8e8e]">{a.role}</div>
                    </div>
                  </div>
                  <div className="text-[10px] text-[#666] mb-2 capitalize">{deptIcons[a.dept]} {a.dept} Department</div>
                  <div className="flex flex-wrap gap-1">
                    {a.skills.slice(0,3).map((s,i)=>(
                      <span key={i} className="text-[9px] bg-[#2f2f2f] text-[#b4b4b4] px-1.5 py-0.5 rounded">{s}</span>
                    ))}
                    {a.skills.length>3&&<span className="text-[9px] text-[#666]">+{a.skills.length-3}</span>}
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : agentDetail ? (
          /* Agent Detail + Chat */
          <div className="flex flex-col h-full">
            {/* Agent Profile Header */}
            <div className="px-5 py-3 border-b border-[#2f2f2f] bg-[#171717]">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${deptColors[agentDetail.department]||'from-gray-500 to-gray-600'} flex items-center justify-center text-lg`}>{agentDetail.emoji}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-bold">{agentDetail.name}</h2>
                    <span className="bg-emerald-600/20 text-emerald-400 text-[10px] px-2 py-0.5 rounded-full">{agentDetail.status}</span>
                  </div>
                  <p className="text-[10px] text-[#8e8e8e]">{agentDetail.role} • {agentDetail.department_name} Department</p>
                </div>
                <button onClick={()=>{setSelectedAgent(null);setAgentDetail(null);setChatMsgs([])}} className="text-[#8e8e8e] hover:text-white text-[11px]">✕ Close</button>
              </div>
              {/* Quick Stats */}
              <div className="flex gap-4 mt-2">
                <span className="text-[10px] text-[#666]">{agentDetail.skills.length} Skills</span>
                <span className="text-[10px] text-[#666]">{agentDetail.capabilities.length} Capabilities</span>
                <span className="text-[10px] text-[#666]">{agentDetail.tech_stack.length} Tech Stack</span>
              </div>
            </div>
            
            {/* Agent Info Tabs */}
            <div className="flex-1 overflow-auto px-5 py-4">
              <div className="grid grid-cols-3 gap-4 mb-5">
                {/* Skills */}
                <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
                  <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">🎯 Skills</h3>
                  <div className="space-y-1.5">
                    {agentDetail.skills.map((s,i)=>(
                      <div key={i} className="text-[11px] text-[#e0e0e0] bg-[#2f2f2f] rounded px-2 py-1">{s}</div>
                    ))}
                  </div>
                </div>
                {/* Capabilities */}
                <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
                  <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">⚡ Capabilities</h3>
                  <div className="space-y-1.5">
                    {agentDetail.capabilities.map((c,i)=>(
                      <div key={i} className="text-[11px] text-blue-400 bg-blue-600/10 rounded px-2 py-1 font-mono">{c}</div>
                    ))}
                  </div>
                </div>
                {/* Tech Stack */}
                <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
                  <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">🛠️ Tech Stack</h3>
                  <div className="space-y-1.5">
                    {agentDetail.tech_stack.map((t,i)=>(
                      <div key={i} className="text-[11px] text-purple-400 bg-purple-600/10 rounded px-2 py-1 font-mono">{t}</div>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Bio */}
              <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4 mb-5">
                <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-2">📝 Bio</h3>
                <p className="text-[13px] text-[#b4b4b4]">{agentDetail.bio}</p>
              </div>
              
              {/* Chat with Agent */}
              <div className="bg-[#171717] rounded-xl border border-[#2f2f2f] p-4">
                <h3 className="text-[10px] font-medium text-[#8e8e8e] uppercase tracking-wider mb-3">💬 Chat with {agentDetail.name}</h3>
                <div className="bg-[#1a1a1a] rounded-lg border border-[#2f2f2f] p-3 mb-3 min-h-[200px] max-h-[300px] overflow-auto space-y-2">
                  {chatMsgs.length===0&&<p className="text-[#666] text-center py-8 text-[12px]">Start chatting with {agentDetail.name}...</p>}
                  {chatMsgs.map((m,i)=>(
                    <div key={i} className={`flex ${m.sender==='You'?'justify-end':'justify-start'}`}>
                      <div className={`max-w-[80%] rounded-xl px-3 py-2 text-[12px] ${m.sender==='You'?'bg-[#2f2f2f]':'bg-[#1a2a3a] text-[#e0e0e0]'}`}>
                        <div className="text-[9px] font-medium mb-0.5 opacity-60">{m.sender}</div>
                        <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
                      </div>
                    </div>
                  ))}
                  {busy&&<div className="flex justify-start"><div className="bg-[#1a2a3a] rounded-xl px-3 py-2"><div className="flex gap-1"><div className="w-1 h-1 bg-[#8e8e8e] rounded-full animate-bounce"></div><div className="w-1 h-1 bg-[#8e8e8e] rounded-full animate-bounce" style={{animationDelay:'.15s'}}></div><div className="w-1 h-1 bg-[#8e8e8e] rounded-full animate-bounce" style={{animationDelay:'.3s'}}></div></div></div></div>}
                  <div ref={chatRef}></div>
                </div>
                <div className="flex gap-2">
                  <input value={chatIn} onChange={e=>setChatIn(e.target.value)} onKeyDown={e=>e.key==='Enter'&&sendChat()} placeholder={`Ask ${agentDetail.name} something...`} className="flex-1 bg-[#2f2f2f] border border-[#3f3f3f] rounded-lg px-3 py-2 text-[12px] text-white placeholder-[#8e8e8e] focus:outline-none focus:border-[#5f5f5f]" disabled={busy}/>
                  <button onClick={sendChat} className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-[12px] font-medium" disabled={busy}>Send</button>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
