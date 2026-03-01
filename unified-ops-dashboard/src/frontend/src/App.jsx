import React, { useEffect, useState } from 'react'

const API = 'http://127.0.0.1:8081'

function Card({ title, children }) {
  return (
    <div style={{ border: '1px solid #ddd', borderRadius: 12, padding: 16, marginBottom: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 8 }}>{title}</div>
      {children}
    </div>
  )
}

export default function App() {
  const [health, setHealth] = useState(null)

  useEffect(() => {
    fetch(`${API}/health`).then(r => r.json()).then(setHealth).catch(() => setHealth({ status: 'error' }))
  }, [])

  return (
    <div style={{ maxWidth: 980, margin: '24px auto', fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif' }}>
      <h1>Unified Ops Dashboard (Mock MVP)</h1>
      <p style={{ color: '#444' }}>
        Phase 0 scaffolding: systems connectivity + job binding + mappings + report runs + audit log.
      </p>

      <Card title="Systems">
        <div>Backend health: <b>{health ? health.status : 'checking...'}</b></div>
        <ul>
          <li>ACC: <code>/mock/acc/*</code></li>
          <li>Procore: <code>/mock/procore/*</code></li>
          <li>HCSS: <code>/mock/hcss/*</code></li>
          <li>Canonical: <code>/api/*</code></li>
        </ul>
      </Card>

      <Card title="Next build steps">
        <ol>
          <li>Implement the 5-screen UI (Systems, Jobs, Mappings, Reports, Audit Log).</li>
          <li>Swap in real DB persistence (SQLite/Postgres/SQL Server).</li>
          <li>Replace fixtures with real connectors.</li>
          <li>Add Playwright UAT flows for job-binding + report generation.</li>
        </ol>
      </Card>
    </div>
  )
}
