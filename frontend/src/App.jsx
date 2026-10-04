import React, { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import AppLayout from './components/layout/AppLayout';
import ErrorBoundary from './components/common/ErrorBoundary';
import DashboardPage from './pages/DashboardPage';
import ScanPage from './pages/ScanPage';
import ScanDetailPage from './pages/ScanDetailPage';
import FindingsPage from './pages/FindingsPage';
import RiskPage from './pages/RiskPage';
import CbomPage from './pages/CbomPage';
import MigrationPage from './pages/MigrationPage';
import NotFoundPage from './pages/NotFoundPage';

const DevStyleGuide = import.meta.env.DEV
  ? lazy(() => import('./dev/StyleGuide'))
  : null;

export default function App() {
  return (
    <ErrorBoundary>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--bg-surface)',
            color: 'var(--text-main)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            fontFamily: 'var(--font-sans)',
            boxShadow: 'var(--shadow-elevated)',
          },
        }}
      />
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/scan" element={<ScanPage />} />
          <Route path="/scans/:scanId" element={<ScanDetailPage />} />
          <Route path="/findings" element={<FindingsPage />} />
          <Route path="/cbom" element={<CbomPage />} />
          <Route path="/risk" element={<RiskPage />} />
          <Route path="/migration" element={<MigrationPage />} />
          <Route path="/roadmap" element={<MigrationPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>

        {import.meta.env.DEV && DevStyleGuide && (
          <Route
            path="/__styleguide"
            element={
              <Suspense fallback={<div style={{ padding: '2rem' }}>Loading Style Guide...</div>}>
                <DevStyleGuide />
              </Suspense>
            }
          />
        )}
      </Routes>
    </ErrorBoundary>
  );
}
