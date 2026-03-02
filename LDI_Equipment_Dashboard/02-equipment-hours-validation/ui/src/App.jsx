import { Navigate, Route, Routes } from 'react-router-dom'

import AppLayout from './components/AppLayout.jsx'
import OverviewPage from './pages/OverviewPage.jsx'
import ProvisionalPage from './pages/ProvisionalPage.jsx'
import ExceptionsPage from './pages/ExceptionsPage.jsx'
import ApprovalFlowPage from './pages/ApprovalFlowPage.jsx'
import InspectionsPage from './pages/InspectionsPage.jsx'
import TelematicsPage from './pages/TelematicsPage.jsx'
import EquipmentDrilldownPage from './pages/EquipmentDrilldownPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Navigate to="/overview" replace />} />
        <Route path="/overview" element={<OverviewPage />} />
        <Route path="/provisional" element={<ProvisionalPage />} />
        <Route path="/exceptions" element={<ExceptionsPage />} />
        <Route path="/approval-flow" element={<ApprovalFlowPage />} />
        <Route path="/inspections" element={<InspectionsPage />} />
        <Route path="/telematics" element={<TelematicsPage />} />
        <Route path="/equipment" element={<EquipmentDrilldownPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/overview" replace />} />
    </Routes>
  )
}
