import React, { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import ScanPage from './pages/ScanPage';
import ScanDetailPage from './pages/ScanDetailPage';
import FindingsPage from './pages/FindingsPage';
import NotFoundPage from './pages/NotFoundPage';

const DevStyleGuide = import.meta.env.DEV
  ? lazy(() => import('./dev/StyleGuide'))
  : null;

export default function App() {
  return (
    <div className="app-root">
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/scan" element={<ScanPage />} />
        <Route path="/scans/:scanId" element={<ScanDetailPage />} />
        <Route path="/findings" element={<FindingsPage />} />
        {import.meta.env.DEV && DevStyleGuide && (
          <Route
            path="/__styleguide"
            element={
              <Suspense fallback={<div>Loading Style Guide...</div>}>
                <DevStyleGuide />
              </Suspense>
            }
          />
        )}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  );
}
