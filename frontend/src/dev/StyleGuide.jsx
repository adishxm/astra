import React, { useState } from 'react';
import {
  Button,
  Card,
  Badge,
  LoadingSpinner,
  ErrorBanner,
  EmptyState,
  TabBar,
  TabPanel,
  Modal,
  Tooltip,
  ProgressRing,
} from '../components/common';
import { Play, Shield, Terminal, Settings } from 'lucide-react';
import './StyleGuide.css';

const COLOR_TOKENS = [
  { name: '--bg-base', value: '#090d16', bg: 'var(--bg-base)' },
  { name: '--bg-surface', value: '#0f172a', bg: 'var(--bg-surface)' },
  { name: '--bg-card', value: 'rgba(30, 41, 59, 0.7)', bg: 'var(--bg-card)' },
  { name: '--primary', value: '#6366f1', bg: 'var(--primary)' },
  { name: '--cyan', value: '#06b6d4', bg: 'var(--cyan)' },
  { name: '--emerald', value: '#10b981', bg: 'var(--emerald)' },
  { name: '--amber', value: '#f59e0b', bg: 'var(--amber)' },
  { name: '--rose', value: '#f43f5e', bg: 'var(--rose)' },
  { name: '--purple', value: '#a855f7', bg: 'var(--purple)' },
];

export default function StyleGuide() {
  const [modalOpen, setModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Shield size={16} /> },
    { id: 'cli', label: 'CLI Tools', icon: <Terminal size={16} />, badge: <Badge variant="info">New</Badge> },
    { id: 'config', label: 'Settings', icon: <Settings size={16} /> },
  ];

  return (
    <div className="styleguide">
      <header className="styleguide__header">
        <h1 className="styleguide__title">ASTRA Design System & Shared Components</h1>
        <p className="styleguide__subtitle">
          Internal Dev-Only Living Style Guide & Token Reference (SIH26164 / Team HEXARK)
        </p>
      </header>

      {/* 1. Color Tokens */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">1. Color Tokens & Swatches</h2>
        <div className="styleguide__grid">
          {COLOR_TOKENS.map((token) => (
            <div key={token.name} className="styleguide__swatch-card">
              <div className="styleguide__swatch" style={{ backgroundColor: token.bg }} />
              <span className="styleguide__swatch-name">{token.name}</span>
              <span className="styleguide__swatch-val">{token.value}</span>
            </div>
          ))}
        </div>
      </section>

      {/* 2. Buttons */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">2. Buttons (Variants, Sizes & States)</h2>
        <div className="styleguide__row">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
        </div>
        <div className="styleguide__row">
          <Button size="sm" variant="primary">Small</Button>
          <Button size="md" variant="primary">Medium</Button>
          <Button size="lg" variant="primary">Large</Button>
          <Button variant="primary" icon={<Play size={16} />}>With Icon</Button>
          <Button variant="primary" loading>Loading</Button>
          <Button variant="primary" disabled>Disabled</Button>
        </div>
      </section>

      {/* 3. Badges */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">3. Badges (Quantum Safety, Urgency, Status)</h2>
        <div className="styleguide__row">
          <Badge variant="safe" />
          <Badge variant="vulnerable" />
          <Badge variant="unknown" />
          <Badge variant="critical" pulse />
          <Badge variant="high" />
          <Badge variant="medium" />
          <Badge variant="low" />
          <Badge variant="info" />
          <Badge variant="pass" />
          <Badge variant="fail" />
        </div>
      </section>

      {/* 4. Cards */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">4. Cards</h2>
        <div className="styleguide__grid">
          <Card title="Default Card">
            <p>Standard card container with subtle border.</p>
          </Card>
          <Card variant="elevated" title="Elevated Card">
            <p>Higher elevation and prominent shadow.</p>
          </Card>
          <Card variant="glass" title="Glass Card">
            <p>Glassmorphic backdrop blur effect.</p>
          </Card>
          <Card
            variant="interactive"
            title="Interactive Card"
            actions={<Button size="sm" variant="ghost">View</Button>}
            onClick={() => alert('Card clicked!')}
          >
            <p>Focusable and clickable with hover glow.</p>
          </Card>
        </div>
      </section>

      {/* 5. Progress Ring */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">5. Progress Ring</h2>
        <div className="styleguide__row">
          <ProgressRing value={25} label="Vulnerable" />
          <ProgressRing value={65} label="Warning" />
          <ProgressRing value={92} label="PQC Ready" />
          <ProgressRing value={100} tone="neutral" label="Neutral" />
        </div>
      </section>

      {/* 6. Tabs */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">6. TabBar & TabPanels</h2>
        <TabBar tabs={tabs} value={activeTab} onChange={setActiveTab} />
        {tabs.map((tab) => (
          <TabPanel key={tab.id} id={tab.id} active={activeTab === tab.id}>
            <p style={{ padding: 'var(--space-md)', color: 'var(--text-muted)' }}>
              Active Tab Content: <strong>{tab.label}</strong>
            </p>
          </TabPanel>
        ))}
      </section>

      {/* 7. LoadingSpinner & ErrorBanner */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">7. Feedback & Status</h2>
        <div className="styleguide__row" style={{ marginBottom: 'var(--space-lg)' }}>
          <LoadingSpinner size="sm" label="Small" />
          <LoadingSpinner size="md" label="Medium" />
          <LoadingSpinner size="lg" elapsedSeconds={12} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
          <ErrorBanner
            title="Engine Unreachable"
            message="Unable to connect to ASTRA engine at 127.0.0.1:8000."
            onRetry={() => alert('Retrying...')}
            onDismiss={() => alert('Dismissed')}
          />
        </div>
      </section>

      {/* 8. Tooltips & Modals */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">8. Overlays (Tooltips & Modal)</h2>
        <div className="styleguide__row">
          <Tooltip content="Tooltip displayed on top" placement="top">
            <Button variant="secondary">Top Tooltip</Button>
          </Tooltip>
          <Tooltip content="Tooltip displayed on bottom" placement="bottom">
            <Button variant="secondary">Bottom Tooltip</Button>
          </Tooltip>
          <Tooltip content="Tooltip displayed on left" placement="left">
            <Button variant="secondary">Left Tooltip</Button>
          </Tooltip>
          <Tooltip content="Tooltip displayed on right" placement="right">
            <Button variant="secondary">Right Tooltip</Button>
          </Tooltip>
          <Button variant="primary" onClick={() => setModalOpen(true)}>
            Open Test Modal
          </Button>
        </div>

        <Modal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          title="Cryptographic Asset Details"
          description="Detailed breakdown of RSA-2048 keypair identified in scan."
        >
          <p style={{ marginBottom: 'var(--space-md)' }}>
            This modal traps keyboard focus, listens for Escape key, closes on backdrop click, and locks body scroll.
          </p>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)' }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button variant="primary" onClick={() => setModalOpen(false)}>Acknowledge</Button>
          </div>
        </Modal>
      </section>

      {/* 9. EmptyState */}
      <section className="styleguide__section">
        <h2 className="styleguide__section-title">9. Empty State</h2>
        <EmptyState
          title="No Findings Recorded"
          message="No vulnerable cryptographic algorithms or weak keys were detected in the target workspace."
          ctaLabel="Run New Scan"
          ctaTo="/scan"
        />
      </section>
    </div>
  );
}
