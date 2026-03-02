import { useEffect, useState } from 'react'

import DataTable from '../components/DataTable.jsx'
import { apiGet } from '../components/api.js'

export default function EquipmentDrilldownPage() {
  const [equipmentId, setEquipmentId] = useState('')
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Load default view unfiltered.
    loadData('')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function loadData(eid) {
    setLoading(true)
    setError('')

    const params = {}
    if (eid) params.equipment_id = eid

    apiGet('/api/dashboard/equipment', params)
      .then((data) => {
        setRows(Array.isArray(data) ? data : [])
      })
      .catch((e) => {
        setError(e.message || String(e))
      })
      .finally(() => {
        setLoading(false)
      })
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-slate-900">Equipment Drilldown</h1>
        <p className="mt-1 text-sm text-slate-600">Filter reconciliation rows for a single piece of equipment.</p>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <div className="w-full sm:max-w-xs">
          <label className="text-xs font-medium text-slate-700">Equipment ID</label>
          <input
            value={equipmentId}
            onChange={(e) => setEquipmentId(e.target.value)}
            placeholder="e.g. 1"
            className="mt-1 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-slate-900"
          />
        </div>
        <button
          onClick={() => loadData(equipmentId)}
          className="inline-flex items-center justify-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Apply filter
        </button>
        <div className="text-xs text-slate-500">{loading ? 'Loading...' : `${rows.length} rows`}</div>
      </div>

      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">{error}</div>
      ) : null}

      <DataTable rows={rows} />
    </div>
  )
}
