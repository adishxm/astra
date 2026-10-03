import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';
import ErrorBanner from '../common/ErrorBanner';
import { useHealth } from '../../hooks/useHealth';
import { getErrorMessage } from '../../api/client';
import './AppLayout.css';

export default function AppLayout() {
  const { error, refetch } = useHealth();

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <Header />

      <div className="app-shell__body">
        <Sidebar />

        <main id="main-content" className="app-shell__main" tabIndex={-1}>
          {error && (
            <div className="app-shell__alert-container">
              <ErrorBanner
                title="Engine Unreachable"
                message={
                  error.kind === 'network'
                    ? 'Unable to connect to ASTRA engine'
                    : getErrorMessage(error)
                }
                onRetry={refetch}
              />
            </div>
          )}

          <div className="app-shell__content">
            <Outlet />
          </div>
        </main>
      </div>

      <Footer />
    </div>
  );
}
