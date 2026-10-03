import { useParams } from 'react-router-dom';
import { usePageTitle } from '../hooks/usePageTitle';

export default function ScanDetailPage() {
  const { scanId } = useParams();
  usePageTitle(`Scan ${scanId || 'Details'}`);

  return (
    <div id="scan-detail-page" className="page-content">
      <h1>Scan Details</h1>
      <p style={{ color: 'var(--text-muted)', marginTop: 'var(--space-sm)' }}>
        Viewing analysis results for scan ID: <code>{scanId}</code>
      </p>
    </div>
  );
}
