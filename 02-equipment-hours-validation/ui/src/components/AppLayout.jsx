import { NavLink, Outlet } from 'react-router-dom'

const navItems = [
  { to: '/overview', label: 'Executive Overview' },
  { to: '/provisional', label: 'Yesterday Provisional' },
  { to: '/exceptions', label: 'Exceptions Queue' },
  { to: '/approval-flow', label: 'Approval Flow' },
  { to: '/inspections', label: 'Inspections Compliance' },
  { to: '/telematics', label: 'Telematics Health' },
  { to: '/equipment', label: 'Equipment Drilldown' }
]

function NavItem({ to, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        [
          'block rounded-md px-3 py-2 text-sm font-medium transition',
          isActive
            ? 'bg-slate-900 text-white'
            : 'text-slate-700 hover:bg-slate-200 hover:text-slate-900'
        ].join(' ')
      }
    >
      {label}
    </NavLink>
  )
}

export default function AppLayout() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div>
            <div className="text-sm font-semibold text-slate-900">Equipment Hours Validation</div>
            <div className="text-xs text-slate-500">POC Dashboard</div>
          </div>
          <div className="text-xs text-slate-500">API: {import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'}</div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 md:grid-cols-[240px_1fr]">
        <aside className="rounded-lg border border-slate-200 bg-white p-3">
          <nav className="space-y-1">
            {navItems.map((i) => (
              <NavItem key={i.to} to={i.to} label={i.label} />
            ))}
          </nav>
        </aside>

        <main className="rounded-lg border border-slate-200 bg-white p-5">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
