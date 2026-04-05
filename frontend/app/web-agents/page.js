'use client'
import { useState, useEffect } from 'react'

const API = 'http://localhost:8000'

const AGENT_KEYS = ['coordinator', 'ui_designer', 'frontend', 'backend', 'api_manager', 'seo', 'performance', 'qa']

const agentConfig = {
  coordinator: { icon: '📋', color: 'from-red-500 to-red-600', name: 'Sara', role: 'Coordinator' },
  ui_designer: { icon: '🎨', color: 'from-pink-500 to-rose-500', name: 'Maya', role: 'UI Designer' },
  frontend: { icon: '💻', color: 'from-emerald-500 to-green-500', name: 'Riya', role: 'Frontend Developer' },
  backend: { icon: '⚙️', color: 'from-blue-500 to-indigo-500', name: 'Aryan', role: 'Backend Developer' },
  api_manager: { icon: '🔌', color: 'from-purple-500 to-violet-500', name: 'Dev', role: 'API Manager' },
  seo: { icon: '🔍', color: 'from-amber-500 to-orange-500', name: 'Kavita', role: 'SEO Agent' },
  performance: { icon: '⚡', color: 'from-yellow-500 to-amber-500', name: 'Vikram', role: 'Performance Agent' },
  qa: { icon: '🧪', color: 'from-cyan-500 to-teal-500', name: 'Kira', role: 'QA Tester' }
}

export default function WebAgentsPage() {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [chatMsgs, setChatMsgs] = useState([])
  const [chatInput, setChatInput] = useState('')
  const [chatBusy, setChatBusy] = useState(false)
  const [showFiles, setShowFiles] = useState(false)
  const [agentFiles, setAgentFiles] = useState({})
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileContent, setFileContent] = useState('')
  const [deptStatus, setDeptStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgents()
    loadDeptStatus()
  }, [])

  const loadAgents = async () => {
    try {
      const res = await fetch(`${API}/api/web-department/agents`)
      if (res.ok) setAgents(await res.json())
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const loadDeptStatus = async () => {
    try {
      const res = await fetch(`${API}/api/web-department`)
      if (res.ok) setDeptStatus(await res.json())
    } catch (e) {}
  }

  const openAgent = async (key) => {
    setSelectedAgent(key)
    setChatMsgs([])
    setChatInput('')
    setShowFiles(false)
    setSelectedFile(null)
    setFileContent('')
    await loadAgentFiles(key)
  }

  const loadAgentFiles = async (key) => {
    try {
      const res = await fetch(`${API}/api/web-department/agent-files/${key}`)
      if (res.ok) {
        const data = await res.json()
        setAgentFiles(data.files || {})
      }
    } catch (e) { console.error(e) }
  }

  const openFile = async (key, filename) => {
    try {
      const res = await fetch(`${API}/api/web-department/agent-files/${key}/${filename}`)
      if (res.ok) {
        const data = await res.json()
        setSelectedFile(filename)
        setFileContent(data.content)
      }
    } catch (e) { console.error(e) }
  }

  const sendChat = async () => {
    if (!chatInput.trim() || chatBusy || !selectedAgent) return
    const msg = chatInput
    setChatInput('')
    setChatBusy(true)
    setChatMsgs(p => [...p, { role: 'user', content: msg, sender: 'You' }])
    try {
      const res = await fetch(`${API}/api/web-department/chat/${selectedAgent}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: chatMsgs.slice(-8).map(m => ({ role: m.sender === 'You' ? 'user' : 'assistant', content: m.content })) })
      })
      if (res.ok) {
        const data = await res.json()
        setChatMsgs(p => [...p, { role: 'assistant', content: data.response, sender: data.sender }])
      } else {
        setChatMsgs(p => [...p, { role: 'assistant', content: 'Connection error', sender: 'System' }])
      }
    } catch (e) {
      setChatMsgs(p => [...p, { role: 'assistant', content: 'Failed to connect', sender: 'System' }])
    }
    setChatBusy(false)
  }

  if (loading) return <div className="flex items-center justify-center h-screen bg-gray-950 text-white"><div className="text-center"><div className="text-4xl mb-3">⚡</div><p className="text-gray-400">Loading Web Department...</p></div></div>

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">⚡ Web Department</h1>
          <p className="text-gray-400">8 specialized agents - each with own file, connected to Groq API</p>
          {deptStatus && (
            <div className="grid grid-cols-4 gap-3 mt-4">
              <div className="bg-gray-800 rounded-lg p-3 text-center"><div className="text-xl font-bold">{deptStatus.total_agents}</div><div className="text-xs text-gray-400">Agents</div></div>
              <div className="bg-gray-800 rounded-lg p-3 text-center"><div className="text-xl font-bold">{deptStatus.task_queue}</div><div className="text-xs text-gray-400">Tasks Queued</div></div>
              <div className="bg-gray-800 rounded-lg p-3 text-center"><div className="text-xl font-bold">{deptStatus.completed_tasks}</div><div className="text-xs text-gray-400">Completed</div></div>
              <div className="bg-gray-800 rounded-lg p-3 text-center"><div className="text-xl font-bold">{deptStatus.messages}</div><div className="text-xs text-gray-400">Messages</div></div>
            </div>
          )}
        </div>
      </div>

      {/* All Agents at Top */}
      <div className="max-w-7xl mx-auto p-6">
        <h2 className="text-lg font-semibold mb-3">🤖 All Agents ({agents.length})</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 mb-6">
          {agents.map((agent) => {
            const key = agent.name === 'Sara' ? 'coordinator' : 
                        agent.name === 'Maya' ? 'ui_designer' :
                        agent.name === 'Riya' ? 'frontend' :
                        agent.name === 'Aryan' ? 'backend' :
                        agent.name === 'Dev' ? 'api_manager' :
                        agent.name === 'Kavita' ? 'seo' :
                        agent.name === 'Vikram' ? 'performance' :
                        agent.name === 'Kira' ? 'qa' : 'coordinator'
            const cfg = agentConfig[key] || {}
            const isSelected = selectedAgent === key
            return (
              <button key={key} onClick={() => openAgent(key)} className={`bg-gray-900 border rounded-xl p-4 text-center hover:border-gray-600 transition-all ${isSelected ? 'border-emerald-500 bg-emerald-900/20' : 'border-gray-800'}`}>
                <div className={`w-12 h-12 mx-auto bg-gradient-to-br ${cfg.color || 'from-gray-500 to-gray-600'} rounded-xl flex items-center justify-center text-2xl mb-2`}>{cfg.icon || '🤖'}</div>
                <div className="text-sm font-semibold">{agent.name}</div>
                <div className="text-[10px] text-gray-400">{agent.role}</div>
                <span className={`inline-block mt-1 text-[9px] px-1.5 py-0.5 rounded-full ${agent.status === 'active' ? 'bg-emerald-900/30 text-emerald-400' : 'bg-yellow-900/30 text-yellow-400'}`}>{agent.status}</span>
              </button>
            )
          })}
        </div>

        {/* Chat + Files Area */}
        {selectedAgent && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Chat Section */}
            <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 bg-gradient-to-br ${agentConfig[selectedAgent]?.color || 'from-gray-500 to-gray-600'} rounded-lg flex items-center justify-center text-xl`}>{agentConfig[selectedAgent]?.icon || '🤖'}</div>
                  <div>
                    <h2 className="font-semibold">Chat with {agentConfig[selectedAgent]?.name || selectedAgent}</h2>
                    <p className="text-xs text-gray-400">{agentConfig[selectedAgent]?.role || ''}</p>
                  </div>
                </div>
                <button onClick={() => setShowFiles(!showFiles)} className="text-xs bg-gray-800 hover:bg-gray-700 px-3 py-1.5 rounded-lg">📁 View Files</button>
              </div>
              <div className="bg-gray-950 rounded-lg p-4 mb-4 h-80 overflow-auto space-y-3">
                {chatMsgs.length === 0 && <p className="text-gray-500 text-center py-8 text-sm">Start a conversation with {agentConfig[selectedAgent]?.name}</p>}
                {chatMsgs.map((m, i) => (
                  <div key={i} className={`flex ${m.sender === 'You' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[75%] rounded-xl px-3 py-2 text-sm ${m.sender === 'You' ? 'bg-emerald-600/30 text-emerald-300' : 'bg-gray-800 text-gray-300'}`}>
                      <div className="text-[10px] font-medium mb-1 opacity-60">{m.sender}</div>
                      <div className="whitespace-pre-wrap">{m.content}</div>
                    </div>
                  </div>
                ))}
                {chatBusy && <div className="flex items-center gap-1 text-gray-400"><div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div><div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '.15s'}}></div><div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '.3s'}}></div></div>}
              </div>
              <div className="flex gap-2">
                <input value={chatInput} onChange={e => setChatInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendChat()} placeholder={`Message ${agentConfig[selectedAgent]?.name}...`} className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500" disabled={chatBusy} />
                <button onClick={sendChat} className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-medium" disabled={chatBusy}>Send</button>
              </div>
            </div>

            {/* Files Panel */}
            <div className={`bg-gray-900 border border-gray-800 rounded-xl p-5 ${showFiles ? '' : 'hidden lg:block'}`}>
              <h3 className="font-semibold mb-3">📁 Agent Files</h3>
              <div className="space-y-2 mb-4">
                {Object.keys(agentFiles).map(filename => (
                  <button key={filename} onClick={() => openFile(selectedAgent, filename)} className={`w-full text-left text-sm px-3 py-2 rounded-lg transition-all ${selectedFile === filename ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-600/30' : 'bg-gray-800 hover:bg-gray-700 text-gray-300'}`}>
                    📄 {filename}
                  </button>
                ))}
              </div>
              {selectedFile && fileContent && (
                <div className="bg-gray-950 rounded-lg p-4 max-h-80 overflow-auto">
                  <div className="text-xs text-gray-400 mb-2">{selectedFile}</div>
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">{fileContent}</pre>
                </div>
              )}
              {!selectedFile && <p className="text-gray-500 text-sm text-center py-4">Click a file to view</p>}
            </div>
          </div>
        )}

        {!selectedAgent && (
          <div className="text-center py-16 text-gray-500">
            <div className="text-5xl mb-3">👆</div>
            <p>Select an agent above to start chatting</p>
          </div>
        )}
      </div>
    </div>
  )
}
