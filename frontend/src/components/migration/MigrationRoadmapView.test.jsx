import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import MigrationRoadmapView, { getTaskPhase } from './MigrationRoadmapView';

describe('MigrationRoadmapView', () => {
  const mockTasks = [
    {
      task_id: 'mig-1',
      asset_id: 'md5-1',
      current_algorithm: 'MD5',
      purpose: 'HASHING',
      relative_path: 'crypto.py',
      priority: 'CRITICAL',
      target_pqc_algorithm: 'SHA-256',
    },
    {
      task_id: 'mig-2',
      asset_id: 'tls-1',
      current_algorithm: 'TLSv1.2',
      purpose: 'PROTOCOL',
      relative_path: 'nginx.conf',
      priority: 'MEDIUM',
      target_pqc_algorithm: 'TLSv1.3 with ML-KEM',
    },
    {
      task_id: 'mig-3',
      asset_id: 'app-rsa-1',
      current_algorithm: 'RSA-2048',
      purpose: 'ASYMMETRIC',
      relative_path: 'auth_handler.py',
      priority: 'HIGH',
      target_pqc_algorithm: 'ML-KEM-768',
    },
  ];

  it('correctly partitions tasks into 3 distinct phases', () => {
    render(<MigrationRoadmapView tasks={mockTasks} />);

    expect(screen.getByTestId('migration-phase-1')).toBeInTheDocument();
    expect(screen.getByTestId('migration-phase-2')).toBeInTheDocument();
    expect(screen.getByTestId('migration-phase-3')).toBeInTheDocument();

    expect(screen.getByText('MD5')).toBeInTheDocument();
    expect(screen.getByText('TLSv1.2')).toBeInTheDocument();
    expect(screen.getByText('RSA-2048')).toBeInTheDocument();
  });

  it('triggers onSelectTask when clicking a phase task card or pressing Enter', () => {
    const handleSelect = vi.fn();
    render(<MigrationRoadmapView tasks={mockTasks} onSelectTask={handleSelect} />);

    const taskCard = screen.getByTestId('phase-task-mig-1');
    fireEvent.click(taskCard);

    expect(handleSelect).toHaveBeenCalledTimes(1);
    expect(handleSelect).toHaveBeenCalledWith(
      expect.objectContaining({
        task_id: 'mig-1',
        current_algorithm: 'MD5',
      })
    );

    fireEvent.keyDown(taskCard, { key: 'Enter', code: 'Enter' });
    expect(handleSelect).toHaveBeenCalledTimes(2);
  });

  it('getTaskPhase helper accurately categorizes libraries, configs, and application code', () => {
    expect(getTaskPhase({ purpose: 'CRYPTOGRAPHIC_LIBRARY', relative_path: 'package.json' })).toBe(1);
    expect(getTaskPhase({ current_algorithm: 'MD5', relative_path: 'util.py' })).toBe(1);
    expect(getTaskPhase({ purpose: 'CIPHER_SUITE', relative_path: 'nginx.conf' })).toBe(2);
    expect(getTaskPhase({ purpose: 'KEY_EXCHANGE', relative_path: 'server.yaml' })).toBe(2);
    expect(getTaskPhase({ current_algorithm: 'ECDSA', purpose: 'SIGNATURE', relative_path: 'sign.py' })).toBe(3);
  });

  it('returns null when tasks array is empty', () => {
    const { container } = render(<MigrationRoadmapView tasks={[]} />);
    expect(container.firstChild).toBeNull();
  });
});
