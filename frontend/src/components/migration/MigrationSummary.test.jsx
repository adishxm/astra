import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect } from 'vitest';
import MigrationSummary from './MigrationSummary';

describe('MigrationSummary', () => {
  const mockTasks = [
    {
      task_id: 'mig-1',
      asset_id: 'md5-1',
      current_algorithm: 'MD5',
      priority: 'CRITICAL',
      target_pqc_algorithm: 'SHA-256 (NIST FIPS 180-4)',
      target_hybrid_algorithm: null,
      status: 'OPEN',
    },
    {
      task_id: 'mig-2',
      asset_id: 'rsa-1',
      current_algorithm: 'RSA-2048',
      priority: 'HIGH',
      target_pqc_algorithm: 'ML-KEM-768 (FIPS 203)',
      target_hybrid_algorithm: 'Hybrid X25519 + ML-KEM-768',
      status: 'IN_REVIEW',
    },
    {
      task_id: 'mig-3',
      asset_id: 'aes-1',
      current_algorithm: 'AES-256',
      priority: 'LOW',
      target_pqc_algorithm: 'N/A - Review with Cryptographer',
      target_hybrid_algorithm: null,
      status: 'ACCEPTED',
    },
  ];

  it('renders total tasks and affected assets count correctly', () => {
    render(<MigrationSummary tasks={mockTasks} scan={{ target_name: 'test-repo.zip' }} />);

    expect(screen.getByTestId('total-migration-tasks')).toHaveTextContent('3');
    expect(screen.getByTestId('affected-assets-subtext')).toHaveTextContent(/Across 3 affected assets/i);
  });

  it('renders urgent migration pathways (Critical + High)', () => {
    render(<MigrationSummary tasks={mockTasks} />);

    expect(screen.getByTestId('urgent-migration-tasks')).toHaveTextContent('2');
    expect(screen.getByText(/1 Critical • 1 High priority/i)).toBeInTheDocument();
  });

  it('renders PQC target candidates count', () => {
    render(<MigrationSummary tasks={mockTasks} />);

    expect(screen.getByTestId('pqc-targets-count')).toHaveTextContent('2');
  });

  it('displays truthfulness and no automatic remediation notice', () => {
    render(<MigrationSummary tasks={mockTasks} scan={{ target_name: 'secure_service.zip' }} />);

    expect(screen.getByLabelText('Advisory Notice')).toBeInTheDocument();
    expect(screen.getByText(/No Automatic Code Remediation/i)).toBeInTheDocument();
    expect(screen.getByText(/secure_service.zip/i)).toBeInTheDocument();
  });

  it('handles empty tasks array gracefully without crashing', () => {
    render(<MigrationSummary tasks={[]} />);

    expect(screen.getByTestId('total-migration-tasks')).toHaveTextContent('0');
    expect(screen.getByTestId('urgent-migration-tasks')).toHaveTextContent('0');
  });
});
