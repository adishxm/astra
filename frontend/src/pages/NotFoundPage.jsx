import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, Home, ArrowLeft } from 'lucide-react';
import { usePageTitle } from '../hooks/usePageTitle';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import './NotFoundPage.css';

export default function NotFoundPage() {
  usePageTitle('Page Not Found');

  return (
    <div id="not-found-page" className="page-content not-found-container">
      <Card className="not-found-card" role="region" aria-label="Page not found notice">
        <div className="not-found-icon-wrap" aria-hidden="true">
          <ShieldAlert size={48} className="not-found-icon" />
        </div>
        <Badge tone="warning" className="not-found-badge">
          HTTP 404
        </Badge>
        <h1 className="not-found-title">Resource Not Found</h1>
        <p className="not-found-description">
          The cryptographic view or artifact endpoint you requested does not exist in the ASTRA console.
        </p>
        <div className="not-found-actions">
          <Button as={Link} to="/" variant="primary" icon={<Home size={16} />}>
            Return to Dashboard
          </Button>
          <Button
            type="button"
            variant="secondary"
            icon={<ArrowLeft size={16} />}
            onClick={() => window.history.back()}
          >
            Go Back
          </Button>
        </div>
      </Card>
    </div>
  );
}
