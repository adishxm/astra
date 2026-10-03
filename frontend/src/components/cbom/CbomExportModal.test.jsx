import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import CbomExportModal from './CbomExportModal';
import * as useApiModule from '../../hooks/useApi';

describe('CbomExportModal', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  const mockExportData = {
    bomFormat: 'CycloneDX',
    specVersion: '1.6',
    serialNumber: 'urn:uuid:scan-cf529d73',
    version: 1,
    components: [
      {
        type: 'cryptographic-asset',
        name: 'RSA-2048-rsa-2048',
        cryptoProperties: {
          assetType: 'algorithm',
          algorithmProperties: {
            name: 'RSA-2048',
            parameterSetIdentifier: '2048',
            executionEnvironment: 'software-plain-ram',
          },
        },
      },
    ],
  };

  it('renders nothing when closed', () => {
    const { container } = render(
      <CbomExportModal open={false} scanId="scan-cf529d73" onClose={() => {}} />
    );
    expect(container).toBeEmptyDOMElement();
  });

  it('renders loading spinner when export is loading', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: vi.fn(),
    });

    render(
      <CbomExportModal open={true} scanId="scan-cf529d73" onClose={() => {}} />
    );

    expect(screen.getByTestId('export-loading')).toBeInTheDocument();
  });

  it('renders JSON preview and download button on success', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: mockExportData,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(
      <CbomExportModal open={true} scanId="scan-cf529d73" archiveName="test.zip" onClose={() => {}} />
    );

    expect(screen.getByText('Export CycloneDX 1.6 CBOM')).toBeInTheDocument();
    expect(screen.getByTestId('export-json-preview')).toBeInTheDocument();
    expect(screen.getByTestId('download-cbom-btn')).toBeInTheDocument();
  });

  it('calls onClose on cancel button click', () => {
    vi.spyOn(useApiModule, 'useApi').mockReturnValue({
      data: mockExportData,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });

    const handleClose = vi.fn();
    render(
      <CbomExportModal open={true} scanId="scan-cf529d73" onClose={handleClose} />
    );

    const cancelBtn = screen.getByRole('button', { name: /Close export dialog/i });
    fireEvent.click(cancelBtn);

    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
