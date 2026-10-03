import { Link } from 'react-router-dom';
import { usePageTitle } from '../hooks/usePageTitle';
import Button from '../components/common/Button';

export default function NotFoundPage() {
  usePageTitle('Page Not Found');

  return (
    <div id="not-found-page" className="page-content" style={{ textAlign: 'center', padding: 'var(--space-3xl) var(--space-lg)' }}>
      <h1>404 - Page Not Found</h1>
      <p style={{ color: 'var(--text-muted)', margin: 'var(--space-md) 0 var(--space-xl) 0' }}>
        The requested view or resource does not exist in the ASTRA console.
      </p>
      <Button as={Link} to="/" variant="primary">
        Return to Dashboard
      </Button>
    </div>
  );
}
