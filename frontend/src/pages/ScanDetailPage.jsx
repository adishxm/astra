import { useEffect } from 'react';
import { useParams } from 'react-router-dom';

export default function ScanDetailPage() {
  const { scanId } = useParams();

  useEffect(() => {
    document.title = `Scan Detail ${scanId || ''} | ASTRA`;
  }, [scanId]);

  return (
    <main id="scan-detail-page" style={{ padding: '2rem' }}>
      <h1>Scan Detail: {scanId}</h1>
    </main>
  );
}
