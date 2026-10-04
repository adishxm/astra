import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import ScanUpload, { validateScanFile, formatBytes } from './ScanUpload';
import { MockXMLHttpRequest } from '../../test/mockXhr';
import scanUploadResponseFixture from '../../test/fixtures/scan_upload_response.json';
import toast from 'react-hot-toast';

vi.mock('react-hot-toast', () => ({
  default: Object.assign(vi.fn(), {
    success: vi.fn(),
    error: vi.fn(),
  }),
}));

describe('ScanUpload', () => {
  const originalXhr = global.XMLHttpRequest;

  beforeEach(() => {
    vi.restoreAllMocks();
    MockXMLHttpRequest.reset();
    global.XMLHttpRequest = MockXMLHttpRequest;
  });

  afterEach(() => {
    global.XMLHttpRequest = originalXhr;
  });

  it('validates file constraints with pure validator', () => {
    expect(validateScanFile(null)).toBe('Please select a repository archive to scan.');

    const zeroByteFile = new File([''], 'empty.zip');
    expect(validateScanFile(zeroByteFile)).toBe('Uploaded archive is zero bytes. Please upload a valid archive.');

    const largeBlob = new Blob([new Uint8Array(101 * 1024 * 1024)]);
    const largeFile = new File([largeBlob], 'too_large.zip');
    expect(validateScanFile(largeFile)).toContain('exceeds maximum limit of 100 MB');

    const invalidExtFile = new File(['content'], 'malware.exe');
    expect(validateScanFile(invalidExtFile)).toBe('Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2');

    const validFile = new File(['valid content'], 'repo.tar.gz');
    expect(validateScanFile(validFile)).toBe(null);
  });

  it('formatBytes formats file sizes correctly', () => {
    expect(formatBytes(0)).toBe('0 Bytes');
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1024 * 1024 * 5)).toBe('5 MB');
  });

  it('renders upload dropzone and file input', () => {
    render(
      <MemoryRouter>
        <ScanUpload />
      </MemoryRouter>
    );

    expect(screen.getByRole('button', { name: /upload repository archive dropzone/i })).toBeInTheDocument();
    expect(screen.getByText(/click to browse/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start scan/i })).toBeDisabled();
  });

  it('handles file selection and displays filename', async () => {
    const user = userEvent.setup();
    const { container } = render(
      <MemoryRouter>
        <ScanUpload />
      </MemoryRouter>
    );

    const file = new File(['fake archive data'], 'my_project.zip', { type: 'application/zip' });
    const input = container.querySelector('#scan-file-input');

    await user.upload(input, file);

    expect(screen.getByText('my_project.zip')).toBeInTheDocument();
    const startBtn = screen.getByRole('button', { name: /start scan/i });
    expect(startBtn).not.toBeDisabled();
  });

  it('handles successful submission and calls onSuccess', async () => {
    const user = userEvent.setup();
    const handleSuccess = vi.fn();

    const { container } = render(
      <MemoryRouter>
        <ScanUpload onSuccess={handleSuccess} navigateOnSuccess={false} />
      </MemoryRouter>
    );

    const file = new File(['fake zip content'], 'app_code.zip', { type: 'application/zip' });
    const input = container.querySelector('#scan-file-input');
    await user.upload(input, file);

    const startBtn = screen.getByRole('button', { name: /start scan/i });
    await user.click(startBtn);

    const xhr = MockXMLHttpRequest.lastInstance;
    expect(xhr).toBeDefined();

    // Trigger upload progress to 100%
    xhr.triggerProgress(100, 100);

    // Complete upload
    xhr.triggerLoad(200, scanUploadResponseFixture);

    await waitFor(() => {
      expect(screen.getByText(/scan complete: scan-cf529d73/i)).toBeInTheDocument();
    });

    expect(handleSuccess).toHaveBeenCalledWith(scanUploadResponseFixture);
    expect(toast.success).toHaveBeenCalled();
  });

  it('handles API upload failure and displays error banner', async () => {
    const user = userEvent.setup();

    const { container } = render(
      <MemoryRouter>
        <ScanUpload />
      </MemoryRouter>
    );

    const file = new File(['fake zip content'], 'failing_app.zip', { type: 'application/zip' });
    const input = container.querySelector('#scan-file-input');
    await user.upload(input, file);

    const startBtn = screen.getByRole('button', { name: /start scan/i });
    await user.click(startBtn);

    const xhr = MockXMLHttpRequest.lastInstance;
    xhr.triggerLoad(400, { detail: 'Unsupported archive format. Expected one of: .zip, .tar, .tar.gz, .tar.bz2' });

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByText(/the archive could not be accepted/i)).toBeInTheDocument();
    expect(toast.error).toHaveBeenCalled();
  });

  it('handles scan cancellation via Cancel button', async () => {
    const user = userEvent.setup();

    const { container } = render(
      <MemoryRouter>
        <ScanUpload />
      </MemoryRouter>
    );

    const file = new File(['fake zip content'], 'cancel_me.zip', { type: 'application/zip' });
    const input = container.querySelector('#scan-file-input');
    await user.upload(input, file);

    const startBtn = screen.getByRole('button', { name: /start scan/i });
    await user.click(startBtn);

    const cancelBtn = screen.getByRole('button', { name: /cancel scan/i });
    await user.click(cancelBtn);

    const xhr = MockXMLHttpRequest.lastInstance;
    expect(xhr.aborted).toBe(true);
  });
});
