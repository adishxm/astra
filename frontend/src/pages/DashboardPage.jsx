import { usePageTitle } from '../hooks/usePageTitle';

export default function DashboardPage() {
  usePageTitle('Dashboard');

  return (
    <div id="dashboard-page" className="page-content">
      <h1>Dashboard</h1>
      <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
        Cryptographic inventory, risk posture, and post-quantum readiness overview.
      </p>
    </div>
  );
}
