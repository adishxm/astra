import React from 'react';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="app-footer__content">
        <span className="app-footer__brand">ASTRA &bull; Team HEXARK</span>
        <span className="app-footer__privacy">Runs locally. No telemetry.</span>
      </div>
    </footer>
  );
}
