import { usePageTitle } from '../hooks/usePageTitle';

export default function FindingsPage() {
  usePageTitle('Findings');

  return (
    <div id="findings-page" className="page-content">
      <h1>Cryptographic Findings</h1>
      <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
        Identified cryptographic algorithms, key lengths, certificates, and compliance findings.
      </p>
    </div>
  );
}
