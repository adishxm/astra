import { useEffect } from 'react';

export default function DashboardPage() {
  useEffect(() => {
    document.title = 'Dashboard | ASTRA';
  }, []);

  return (
    <main id="dashboard-page" style={{ padding: '2rem' }}>
      <h1>Dashboard</h1>
    </main>
  );
}
