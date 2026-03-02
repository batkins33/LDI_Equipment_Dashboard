function formatCell(value) {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') return value
  return String(value)
}

export default function DataTable({ rows }) {
  const safeRows = Array.isArray(rows) ? rows : []
  const columns = safeRows.length > 0 ? Object.keys(safeRows[0]) : []

  if (columns.length === 0) {
    return (
      <div className="rounded-md border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        No data
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((c) => (
              <th
                key={c}
                className="whitespace-nowrap px-3 py-2 text-left text-xs font-semibold text-slate-700"
              >
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {safeRows.map((r, idx) => (
            <tr key={idx} className="hover:bg-slate-50">
              {columns.map((c) => (
                <td key={c} className="whitespace-nowrap px-3 py-2 text-xs text-slate-700">
                  {formatCell(r[c])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
