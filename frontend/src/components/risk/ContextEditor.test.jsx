import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ContextEditor from './ContextEditor';
import * as apiClient from '../../api/client';

vi.mock('../../api/client', async () => {
  const actual = await vi.importActual('../../api/client');
  return {
    ...actual,
    apiPut: vi.fn(),
  };
});

describe('ContextEditor Component', () => {
  const mockScanId = 'test-scan-123';
  const mockDefaultContext = {
    data_shelf_life_years: 5.0,
    migration_duration_years: 2.0,
    exposure: 3,
    criticality: 3,
    dependency_reach: 1,
    is_user_enriched: false,
    context_source: 'DEFAULT_ASSUMPTION',
  };

  const mockEnrichedContext = {
    data_shelf_life_years: 10.0,
    migration_duration_years: 3.0,
    exposure: 5,
    criticality: 4,
    dependency_reach: 2,
    quantum_threat_horizon_years: 10.0,
    is_user_enriched: true,
    context_source: 'OWNER_SUPPLIED',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders unverified default assumption badge when is_user_enriched is false', () => {
    render(<ContextEditor scanId={mockScanId} context={mockDefaultContext} />);
    expect(screen.getByTestId('context-status-badge')).toHaveTextContent('Unverified / Default Assumption');
    expect(screen.getByTestId('input-shelf-life')).toHaveValue(5);
    expect(screen.getByTestId('input-migration-duration')).toHaveValue(2);
    expect(screen.getByTestId('input-threat-horizon')).toHaveValue(8);
  });

  it('renders neutral owner-provided context badge when is_user_enriched is true', () => {
    render(<ContextEditor scanId={mockScanId} context={mockEnrichedContext} />);
    expect(screen.getByTestId('context-status-badge')).toHaveTextContent('Owner-Provided Context');
    expect(screen.getByTestId('input-shelf-life')).toHaveValue(10);
    expect(screen.getByTestId('input-migration-duration')).toHaveValue(3);
    expect(screen.getByTestId('input-threat-horizon')).toHaveValue(10);
  });

  it('displays error banner when numerical validation fails (out of range)', async () => {
    render(<ContextEditor scanId={mockScanId} context={mockDefaultContext} />);

    const shelfInput = screen.getByTestId('input-shelf-life');
    fireEvent.change(shelfInput, { target: { value: '-5' } });

    const form = screen.getByTestId('context-editor-form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/must be a non-negative number of years/i)).toBeInTheDocument();
    });
    expect(apiClient.apiPut).not.toHaveBeenCalled();
  });

  it('submits valid payload including quantum_threat_horizon_years to API endpoint and calls onSaveSuccess', async () => {
    const onSaveSuccess = vi.fn();
    apiClient.apiPut.mockResolvedValueOnce({
      status: 'updated',
      scan_id: mockScanId,
      context: mockEnrichedContext,
    });

    render(<ContextEditor scanId={mockScanId} context={mockDefaultContext} onSaveSuccess={onSaveSuccess} />);

    fireEvent.change(screen.getByTestId('input-shelf-life'), { target: { value: '12' } });
    fireEvent.change(screen.getByTestId('input-migration-duration'), { target: { value: '4' } });
    fireEvent.change(screen.getByTestId('input-threat-horizon'), { target: { value: '10' } });
    fireEvent.change(screen.getByTestId('select-exposure'), { target: { value: '5' } });
    fireEvent.change(screen.getByTestId('select-criticality'), { target: { value: '4' } });
    fireEvent.change(screen.getByTestId('input-dependency-reach'), { target: { value: '3' } });

    fireEvent.click(screen.getByTestId('save-context-btn'));

    await waitFor(() => {
      expect(apiClient.apiPut).toHaveBeenCalledWith(`/api/v1/scans/${mockScanId}/context`, {
        data_shelf_life_years: 12,
        migration_duration_years: 4,
        exposure: 5,
        criticality: 4,
        dependency_reach: 3,
        quantum_threat_horizon_years: 10,
      });
    });

    await waitFor(() => {
      expect(screen.getByTestId('context-success-banner')).toHaveTextContent('Project context factors saved to server successfully.');
    });

    expect(onSaveSuccess).toHaveBeenCalled();
  });

  it('handles API rejection gracefully', async () => {
    apiClient.apiPut.mockRejectedValueOnce(new Error('Invalid context parameters'));

    render(<ContextEditor scanId={mockScanId} context={mockDefaultContext} />);

    fireEvent.click(screen.getByTestId('save-context-btn'));

    await waitFor(() => {
      expect(screen.getByText(/Invalid context parameters/i)).toBeInTheDocument();
    });
  });
});
