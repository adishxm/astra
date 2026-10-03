import { useEffect } from 'react';

export default function ScanPage() {
  useEffect(() => {
    document.title = 'New Scan | ASTRA';
  }, []);

  return (
    <main id="scan-page" style={{ padding: '2rem' }}>
      <h1>New Scan</h1>
    </main>
  );
}
