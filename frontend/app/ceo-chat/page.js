'use client'
import { useState, useRef, useEffect } from 'react'

const API = 'http://localhost:8000'

export default function CeoChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({behavior:'smooth'}); }, [messages])

  const send = async () => {
    if (!input.trim() || busy) return
    const text = input; setInput(''); setBusy(true)
    setMessages(p => [...p, { role:'user', content:text, sender:'You' }])
    try {
      const hist = messages.slice(-8).map(m => ({role: m.sender==='You'?'user':'assistant', content:m.content}))
      const r = await fetch(API+'/api/chat/ceo', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({message:text, history:hist})
      })
      if(r.ok) { const d = await r.json(); setMessages(p => [...p, {role:'assistant', content:d.response, sender:d.sender}]); }
    } catch(e) { setMessages(p => [...p, {role:'assistant', content:'Connection error', sender:'System'}]); }
    setBusy(false)
  }

  return (
    <div className="flex h-screen bg-[#1a1a1a] text-white">
      <div className="flex-1 flex flex-col">
        <div className="px-5 py-3 border-b border-[#2f2f2f] bg-[#171717]">
          <h1 className="text-base font-semibold">🧠 CEO Atlas</h1>
          <p className="text-[10px] text-[#888]">Task batlo, department ko assign karega</p>
        </div>
        
        <div className="flex-1 overflow-auto px-5 py-3 space-y-3">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-4xl mb-3">🧠</div>
                <p className="text-[#888] text-sm">CEO Atlas se baat karo</p>
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.sender==='You'?'justify-end':'justify-start'}`}>
              <div className={`max-w-[70%] rounded-2xl px-3.5 py-2 text-[13px] ${m.sender==='You'?'bg-[#2f2f2f]':'bg-[#1a3a2a] text-[#e0e0e0]'}`}>
                <div className="text-[10px] font-medium mb-0.5 opacity-60">{m.sender}</div>
                <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>
              </div>
            </div>
          ))}
          {busy && <div className="flex justify-start"><div className="bg-[#1a3a2a] rounded-2xl px-4 py-2.5"><div className="flex gap-1.5"><div className="w-1.5 h-1.5 bg-[#888] rounded-full animate-bounce"></div><div className="w-1.5 h-1.5 bg-[#888] rounded-full animate-bounce" style={{animationDelay:'.15s'}}></div><div className="w-1.5 h-1.5 bg-[#888] rounded-full animate-bounce" style={{animationDelay:'.3s'}}></div></div></div></div>}
          <div ref={endRef}></div>
        </div>

        <div className="px-5 py-3 border-t border-[#2f2f2f] bg-[#171717]">
          <div className="flex gap-2">
            <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key==='Enter' && send()} placeholder="Task likho..." className="flex-1 bg-[#2f2f2f] border border-[#3f3f3f] rounded-xl px-3.5 py-2.5 text-[13px] text-white placeholder-[#888] focus:outline-none focus:border-[#5f5f5f]" disabled={busy}/>
            <button onClick={send} className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-xl text-[13px] font-medium" disabled={busy}>Send</button>
          </div>
        </div>
      </div>
    </div>
  )
}