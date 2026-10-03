import { useEffect } from 'react';

export default function FindingsPage() {
  useEffect(() => {
    document.title = 'Findings & Inventory | ASTRA';
  }, []);

  return (
    <main id="findings-page" style={{ padding: '2rem' }}>
      <h1>Cryptographic Findings</h1>
    </main>
  );
}
