import { Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import ScanPage from './pages/ScanPage';
import ScanDetailPage from './pages/ScanDetailPage';
import FindingsPage from './pages/FindingsPage';
import NotFoundPage from './pages/NotFoundPage';

export default function App() {
  return (
    <div className="app-root">
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/scans/:scanId" element={<ScanDetailPage />} />
        <Route path="/findings" element={<FindingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  );
}
