import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import MigrationDetailModal from './MigrationDetailModal';

describe('MigrationDetailModal', () => {
  const mockTask = {
    task_id: 'mig-task-101',
    asset_id: 'rsa-2048-crypto_service.py-22',
    relative_path: 'crypto_service.py',
    start_line: 22,
    current_algorithm: 'RSA-2048',
    purpose: 'ASYMMETRIC',
    priority: 'HIGH',
    composite_risk_score: 66.3,
    target_pqc_algorithm: 'ML-KEM-768 (KEX) or ML-DSA-65 (Signatures)',
    target_hybrid_algorithm: 'Hybrid X25519 + ML-KEM-768',
    dated_standard_ref: 'NIST FIPS 203 & 204 (Aug 2024)',
    compatibility_gaps: [
      'Public key expands to 1184 bytes',
      'Ciphertext size expands to 1088 bytes',
    ],
    recommended_action: 'Plan upgrade to ML-KEM-768 for encryption/KEX and ML-DSA-65 for digital signatures',
    review_owner: 'Security Architecture & Crypto Team',
    status: 'IN_REVIEW',
    operational_benchmarking_caveat: 'Requires deployment-specific benchmarking for latency and packet fragmentation before migration.',
    reason_codes: ['RC_HIGH_COMPOSITE_RISK', 'MOSCA_DEADLINE_PASSED'],
  };

  function renderWithRouter(ui) {
    return render(<MemoryRouter>{ui}</MemoryRouter>);
  }

  it('renders modal with transition banner, action plan, and caveats when open is true', () => {
    renderWithRouter(
      <MigrationDetailModal task={mockTask} open={true} onClose={vi.fn()} scanId="scan-cf529d73" />
    );

    expect(screen.getByTestId('migration-detail-modal-body')).toBeInTheDocument();
    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.getByText(/ML-KEM-768 \(KEX\) or ML-DSA-65 \(Signatures\)/i)).toBeInTheDocument();

    expect(screen.getByText(/Plan upgrade to ML-KEM-768/i)).toBeInTheDocument();
    expect(screen.getByText(/Hybrid X25519 \+ ML-KEM-768/i)).toBeInTheDocument();

    expect(screen.getByText(/Public key expands to 1184 bytes/i)).toBeInTheDocument();
    expect(screen.getByText(/Ciphertext size expands to 1088 bytes/i)).toBeInTheDocument();
  });

  it('renders cross-reference navigation links for Risk, CBOM, and Evidence', () => {
    renderWithRouter(
      <MigrationDetailModal task={mockTask} open={true} onClose={vi.fn()} scanId="scan-cf529d73" />
    );

    expect(screen.getByText('Risk Assessment')).toBeInTheDocument();
    expect(screen.getByText('CBOM Inventory')).toBeInTheDocument();
    expect(screen.getByText('Source Evidence')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    renderWithRouter(
      <MigrationDetailModal task={mockTask} open={true} onClose={handleClose} />
    );

    const closeBtn = screen.getByRole('button', { name: /Close migration recommendation modal/i });
    fireEvent.click(closeBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('returns null when task is null or open is false', () => {
    const { container: c1 } = renderWithRouter(
      <MigrationDetailModal task={null} open={true} onClose={vi.fn()} />
    );
    expect(c1.firstChild).toBeNull();

    const { container: c2 } = renderWithRouter(
      <MigrationDetailModal task={mockTask} open={false} onClose={vi.fn()} />
    );
    expect(c2.firstChild).toBeNull();
  });
});
