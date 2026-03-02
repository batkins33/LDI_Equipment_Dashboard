import { useEffect, useMemo, useState } from 'react'

import DataTable from '../components/DataTable.jsx'
import KpiCard from '../components/KpiCard.jsx'
import { apiGet } from '../components/api.js'

export default function OverviewPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')

    apiGet('/api/dashboard/overview')
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

  const kpis = useMemo(() => {
    if (!rows || rows.length === 0) {
      return {
        equipmentDays: 0,
        exceptionDays: 0,
        avgConfidence: 0,
        totalFlags: 0
      }
    }
    const latest = rows[0]
    return {
      equipmentDays: latest.equipment_days ?? 0,
      exceptionDays: latest.exception_days ?? 0,
      avgConfidence: latest.avg_confidence ?? 0,
      totalFlags: latest.total_flags ?? 0
    }
  }, [rows])

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-slate-900">Executive Overview</h1>
        <p className="mt-1 text-sm text-slate-600">Daily rollup from reconciliation results.</p>
      </div>

      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</div>
      ) : null}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Equipment-days" value={kpis.equipmentDays} />
        <KpiCard label="Exception-days" value={kpis.exceptionDays} />
        <KpiCard label="Avg confidence" value={kpis.avgConfidence} />
        <KpiCard label="Total flags" value={kpis.totalFlags} />
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-slate-800">Overview rows</div>
        <div className="text-xs text-slate-500">{loading ? 'Loading...' : `${rows.length} rows`}</div>
      </div>

      <DataTable rows={rows} />
    </div>
  )
}
