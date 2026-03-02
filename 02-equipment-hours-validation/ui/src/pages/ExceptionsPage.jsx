import { useEffect, useState } from 'react'

import DataTable from '../components/DataTable.jsx'
import { apiGet } from '../components/api.js'

export default function ExceptionsPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')

    apiGet('/api/dashboard/exceptions')
      .then((data) => {
        if (!active) return
        setRows(Array.isArray(data) ? data : [])
      })
      .catch((e) => {
        if (!active) return
        setError(e.message || String(e))
      })
      .finally(() => {
        if (!active) return
        setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-slate-900">Exceptions Queue</h1>
        <p className="mt-1 text-sm text-slate-600">Open exceptions generated from reconciliation flags.</p>
      </div>

      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</div>
      ) : null}

      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-slate-800">Open exceptions</div>
        <div className="text-xs text-slate-500">{loading ? 'Loading...' : `${rows.length} rows`}</div>
      </div>

      <DataTable rows={rows} />
    </div>
  )
}
