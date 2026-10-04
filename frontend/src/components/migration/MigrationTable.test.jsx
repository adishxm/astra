import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import MigrationTable from './MigrationTable';

describe('MigrationTable', () => {
  function renderWithRouter(ui) {
    return render(<MemoryRouter>{ui}</MemoryRouter>);
  }
  const mockTasks = [
    {
      task_id: 'mig-1',
      asset_id: 'md5-1',
      current_algorithm: 'MD5',
      purpose: 'HASHING',
      relative_path: 'crypto_service.py',
      start_line: 42,
      priority: 'CRITICAL',
      composite_risk_score: 76.3,
      target_pqc_algorithm: 'SHA-256 (NIST FIPS 180-4)',
      target_hybrid_algorithm: null,
      dated_standard_ref: 'NIST FIPS 180-4',
      status: 'OPEN',
      compatibility_gaps: ['Digest expansion to 256 bits'],
    },
    {
      task_id: 'mig-2',
      asset_id: 'rsa-1',
      current_algorithm: 'RSA-2048',
      purpose: 'ASYMMETRIC',
      relative_path: 'auth.py',
      start_line: 18,
      priority: 'HIGH',
      composite_risk_score: 66.3,
      target_pqc_algorithm: 'ML-KEM-768 (KEX)',
      target_hybrid_algorithm: 'Hybrid X25519 + ML-KEM-768',
      dated_standard_ref: 'NIST FIPS 203 (Aug 2024)',
      status: 'IN_REVIEW',
      compatibility_gaps: ['Public key size expands to 1184 bytes'],
    },
    {
      task_id: 'mig-3',
      asset_id: 'aes-1',
      current_algorithm: 'AES-256',
      purpose: 'ENCRYPTION',
      relative_path: 'storage.py',
      start_line: 90,
      priority: 'LOW',
      composite_risk_score: 27.0,
      target_pqc_algorithm: 'N/A - Review with Cryptographer',
      target_hybrid_algorithm: null,
      dated_standard_ref: 'NIST IR 8547',
      status: 'ACCEPTED',
      compatibility_gaps: [],
    },
  ];

  it('renders table headers and task rows accurately', () => {
    renderWithRouter(<MigrationTable tasks={mockTasks} />);

    expect(screen.getByText('MD5')).toBeInTheDocument();
    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.getByText('AES-256')).toBeInTheDocument();

    expect(screen.getByText(/SHA-256 \(NIST FIPS 180-4\)/i)).toBeInTheDocument();
    expect(screen.getByText(/ML-KEM-768 \(KEX\)/i)).toBeInTheDocument();

    expect(screen.getAllByText(/CRITICAL/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/HIGH/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/LOW/i).length).toBeGreaterThanOrEqual(1);
  });

  it('filters recommendations by search query', () => {
    renderWithRouter(<MigrationTable tasks={mockTasks} />);

    const searchInput = screen.getByTestId('migration-search-input');
    fireEvent.change(searchInput, { target: { value: 'auth.py' } });

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.queryByText('MD5')).not.toBeInTheDocument();
  });

  it('filters recommendations by priority / urgency filter', () => {
    renderWithRouter(<MigrationTable tasks={mockTasks} />);

    const urgencySelect = screen.getByTestId('migration-urgency-filter');
    fireEvent.change(urgencySelect, { target: { value: 'CRITICAL' } });

    expect(screen.getByText('MD5')).toBeInTheDocument();
    expect(screen.queryByText('RSA-2048')).not.toBeInTheDocument();
    expect(screen.queryByText('AES-256')).not.toBeInTheDocument();
  });

  it('filters recommendations by status filter', () => {
    renderWithRouter(<MigrationTable tasks={mockTasks} />);

    const statusSelect = screen.getByTestId('migration-status-filter');
    fireEvent.change(statusSelect, { target: { value: 'IN_REVIEW' } });

    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
    expect(screen.queryByText('MD5')).not.toBeInTheDocument();
  });

  it('sorts recommendation rows when clicking sortable column headers', () => {
    renderWithRouter(<MigrationTable tasks={mockTasks} />);

    const currentAlgoSortBtn = screen.getByRole('button', { name: /Current Algorithm & Migration Target/i });
    fireEvent.click(currentAlgoSortBtn);

    const rows = screen.getAllByRole('button', { name: /^Inspect recommendation for/i });
    expect(rows.length).toBe(3);
  });

  it('triggers onSelectTask when inspect button or table row is activated', () => {
    const handleSelect = vi.fn();
    renderWithRouter(<MigrationTable tasks={mockTasks} onSelectTask={handleSelect} />);

    const inspectBtns = screen.getAllByRole('button', { name: /Inspect.*recommendation/i });
    fireEvent.click(inspectBtns[0]);

    expect(handleSelect).toHaveBeenCalledTimes(1);

    const row = screen.getByTestId('migration-row-mig-1');
    fireEvent.keyDown(row, { key: 'Enter', code: 'Enter' });
    expect(handleSelect).toHaveBeenCalledTimes(2);
  });

  it('displays empty state with reset filters button when search finds no matches', () => {
    renderWithRouter(<MigrationTable tasks={mockTasks} />);

    const searchInput = screen.getByTestId('migration-search-input');
    fireEvent.change(searchInput, { target: { value: 'NON_EXISTENT_QUERY' } });

    expect(screen.getByText(/No Migration Recommendations Match Criteria/i)).toBeInTheDocument();

    const resetBtn = screen.getByRole('button', { name: /Reset Filters/i });
    fireEvent.click(resetBtn);

    expect(screen.getByText('MD5')).toBeInTheDocument();
  });
});
