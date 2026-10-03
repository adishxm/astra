import { useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  useEffect(() => {
    document.title = '404 Not Found | ASTRA';
  }, []);

  return (
    <main id="not-found-page" style={{ padding: '2rem' }}>
      <h1>404 — Page Not Found</h1>
      <p style={{ marginTop: '1rem' }}>
        <Link to="/" style={{ color: '#6366f1' }}>
          Back to Dashboard
        </Link>
      </p>
    </main>
  );
}
