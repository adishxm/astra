import React from 'react';
import { useHealth } from '../../hooks/useHealth';
import Badge from '../common/Badge';
import { Shield } from 'lucide-react';
import './Header.css';

export default function Header() {
  const { isHealthy, loading, error } = useHealth();

  let healthStatusVariant = 'unknown';
  let healthStatusText = 'Checking...';

  if (!loading) {
    if (isHealthy) {
      healthStatusVariant = 'safe';
      healthStatusText = 'Engine online';
    } else if (error) {
      healthStatusVariant = 'vulnerable';
      healthStatusText = 'Engine unreachable';
    } else {
      healthStatusVariant = 'unknown';
      healthStatusText = 'Unassessed';
    }
  }

  return (
    <header className="app-header glass-header">
      <div className="app-header__brand">
        <div className="app-header__logo" aria-hidden="true">
          <Shield size={22} className="app-header__icon" />
        </div>
        <div className="app-header__title-group">
          <span className="app-header__title">ASTRA</span>
          <span className="app-header__subtitle">ECDAT</span>
        </div>
      </div>

      <div className="app-header__actions">
        <Badge
          variant={healthStatusVariant}
          live
          aria-label={`ASTRA engine status: ${healthStatusText}`}
        >
          {healthStatusText}
        </Badge>
      </div>
    </header>
  );
}
