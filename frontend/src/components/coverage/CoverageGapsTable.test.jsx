import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CoverageGapsTable, { formatBytes } from './CoverageGapsTable';

describe('CoverageGapsTable', () => {
  const sampleManifestFiles = [
    {
      relative_path: 'crypto_service.py',
      size_bytes: 1558,
      sha256: '48111bd8a8e14d8b4fb4ba07f439f8f569d2debb0fff1d9df9d47eb82ce198b7',
      file_extension: '.py',
      is_supported: true,
      skip_reason: null,
    },
    {
      relative_path: 'README.md',
      size_bytes: 1539,
      sha256: '529f856f3308e44d832ff2f4d56faf5a74892e0ea6d271a5fa058a55ead1e9da',
      file_extension: '.md',
      is_supported: false,
      skip_reason: null,
    },
    {
      relative_path: 'unsupported_media.wav',
      size_bytes: 45,
      sha256: '4e43622cf167113961492e4c7d47d0e93285e77dd2ce9b4575eec3e183d83396',
      file_extension: '.wav',
      is_supported: false,
      skip_reason: 'Audio binary file excluded by policy',
    },
  ];

  const sampleExtensions = ['.md', '.wav', '.json'];

  it('renders unsupported and skipped files with extensions and sizes', () => {
    render(
      <CoverageGapsTable
        manifestFiles={sampleManifestFiles}
        unsupportedExtensions={sampleExtensions}
      />
    );

    expect(screen.getByTestId('coverage-gaps-table')).toBeInTheDocument();
    expect(screen.getByText('README.md')).toBeInTheDocument();
    expect(screen.getByText('unsupported_media.wav')).toBeInTheDocument();
    expect(screen.queryByText('crypto_service.py')).not.toBeInTheDocument(); // supported files excluded from gaps table
    expect(screen.getAllByText('.md')[0]).toBeInTheDocument();
    expect(screen.getAllByText('.wav')[0]).toBeInTheDocument();
    expect(screen.getByText('SKIPPED')).toBeInTheDocument();
  });

  it('filters gap files using search input', () => {
    render(
      <CoverageGapsTable
        manifestFiles={sampleManifestFiles}
        unsupportedExtensions={sampleExtensions}
      />
    );

    const searchInput = screen.getByLabelText(/filter gap files/i);
    fireEvent.change(searchInput, { target: { value: 'README' } });

    expect(screen.getByText('README.md')).toBeInTheDocument();
    expect(screen.queryByText('unsupported_media.wav')).not.toBeInTheDocument();
  });

  it('renders empty message when all files are supported', () => {
    const allSupported = [
      {
        relative_path: 'crypto_service.py',
        size_bytes: 1558,
        file_extension: '.py',
        is_supported: true,
        skip_reason: null,
      },
    ];

    render(<CoverageGapsTable manifestFiles={allSupported} unsupportedExtensions={[]} />);
    expect(screen.getByText(/all files in the archive were supported and assessed/i)).toBeInTheDocument();
  });

  describe('formatBytes helper', () => {
    it('formats bytes correctly across units', () => {
      expect(formatBytes(0)).toBe('0 B');
      expect(formatBytes(512)).toBe('512 B');
      expect(formatBytes(2048)).toBe('2.0 KB');
      expect(formatBytes(5 * 1024 * 1024)).toBe('5.00 MB');
      expect(formatBytes(null)).toBe('0 B');
    });
  });
});
