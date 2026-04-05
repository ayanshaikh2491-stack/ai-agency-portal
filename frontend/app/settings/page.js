'use client'
import { useState, useEffect } from 'react'

const departments = ['ceo', 'website', 'qa', 'marketing', 'devops', 'product', 'data', 'security', 'hr']
const deptNames = {
  ceo: 'Atlas (CEO)',
  website: 'Amit (Website)',
  qa: 'Sneha (QA)',
  marketing: 'Kavita (Marketing)',
  devops: 'Vikram (DevOps)',
  product: 'Neha (Product)',
  data: 'Arjun (Data)',
  security: 'Deepak (Security)',
  hr: 'Pooja (HR)'
}

export default function SettingsPage() {
  const [configs, setConfigs] = useState({})
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [testing, setTesting] = useState(null)
  const [testResult, setTestResult] = useState('')

  useEffect(() => {
    fetchConfigs()
  }, [])

  const fetchConfigs = async () => {
    const res = await fetch('http://localhost:8000/api/settings')
    const data = await res.json()
    setConfigs(data)
  }

  const updateConfig = (dept, field, value) => {
    setConfigs(prev => ({
      ...prev,
      [dept]: { ...(prev[dept] || {}), [field]: value }
    }))
  }

  const saveAll = async () => {
    setLoading(true)
    setSaved(false)
    await fetch('http://localhost:8000/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configs)
    })
    setLoading(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const testConfig = async (dept) => {
    setTesting(dept)
    setTestResult('')
    const cfg = configs[dept] || {}
    if (!cfg.api_key || !cfg.model) {
      setTestResult('❌ API Key aur Model dono chahiye')
      setTesting(null)
      return
    }
    const res = await fetch(`http://localhost:8000/api/settings/${dept}/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: cfg.api_key, model: cfg.model })
    })
    const data = await res.json()
    setTestResult(data.ok ? `✅ ${dept} working! Response: ${data.response?.substring(0, 100)}...` : `❌ Error: ${data.error}`)
    setTesting(null)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">⚙️ AI Settings</h1>
        <p className="text-gray-400 mb-8">Har department ke liye apna API Key aur Model set karo</p>

        {saved && (
          <div className="bg-green-900/50 border border-green-500 text-green-300 p-3 rounded-lg mb-6">
            ✅ Settings saved successfully!
          </div>
        )}

        {testResult && (
          <div className="bg-blue-900/50 border border-blue-500 text-blue-300 p-3 rounded-lg mb-6">
            {testResult}
          </div>
        )}

        <div className="space-y-6">
          {departments.map(dept => {
            const cfg = configs[dept] || { api_key: '', model: '' }
            return (
              <div key={dept} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">{deptNames[dept]}</h2>
                  <button
                    onClick={() => testConfig(dept)}
                    disabled={testing === dept}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm disabled:opacity-50"
                  >
                    {testing === dept ? 'Testing...' : '🧪 Test'}
                  </button>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">API Key</label>
                    <input
                      type="password"
                      value={cfg.api_key || ''}
                      onChange={e => updateConfig(dept, 'api_key', e.target.value)}
                      placeholder="sk-or-v1-..."
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Model</label>
                    <input
                      type="text"
                      value={cfg.model || ''}
                      onChange={e => updateConfig(dept, 'model', e.target.value)}
                      placeholder="qwen/qwen3.6-plus:free"
                      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
                    />
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Free models: qwen/qwen3.6-plus:free, google/gemma-2-9b-it:free, meta-llama/llama-3.1-8b-instruct:free
                </p>
              </div>
            )
          })}
        </div>

        <button
          onClick={saveAll}
          disabled={loading}
          className="mt-6 w-full py-3 bg-green-600 hover:bg-green-700 rounded-xl font-semibold disabled:opacity-50"
        >
          {loading ? 'Saving...' : '💾 Save All Settings'}
        </button>
      </div>
    </div>
  )
}