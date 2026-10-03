import { usePageTitle } from '../hooks/usePageTitle';

export default function ScanPage() {
  usePageTitle('New Scan');

  return (
    <div id="scan-page" className="page-content">
      <h1>New Scan</h1>
      <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
        Upload source code or binary archives for automated cryptographic discovery.
      </p>
    </div>
  );
}
