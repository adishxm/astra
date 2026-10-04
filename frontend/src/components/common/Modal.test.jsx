import React, { useState } from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from './Modal';

function ModalWrapper({ initialOpen = true, closeOnBackdrop = true, onClose }) {
  const [open, setOpen] = useState(initialOpen);

  const handleClose = () => {
    setOpen(false);
    onClose?.();
  };

  return (
    <div>
      <button type="button" onClick={() => setOpen(true)}>
        Open Modal
      </button>
      <Modal
        open={open}
        onClose={handleClose}
        title="Test Modal Title"
        description="Test modal description"
        closeOnBackdrop={closeOnBackdrop}
      >
        <p>Modal Body Content</p>
        <button type="button">Inside Action</button>
      </Modal>
    </div>
  );
}

describe('Modal', () => {
  it('opens/closes', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();
    render(<ModalWrapper initialOpen={false} onClose={handleClose} />);

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

    const openBtn = screen.getByRole('button', { name: /open modal/i });
    await user.click(openBtn);

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText('Test Modal Title')).toBeInTheDocument();
    expect(screen.getByText('Modal Body Content')).toBeInTheDocument();

    const closeBtn = screen.getByRole('button', { name: /close dialog/i });
    await user.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('backdrop click closes', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();
    render(<ModalWrapper initialOpen={true} closeOnBackdrop={true} onClose={handleClose} />);

    const backdrop = document.querySelector('.modal-backdrop');
    expect(backdrop).toBeInTheDocument();

    await user.click(backdrop);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('Escape closes', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();
    render(<ModalWrapper initialOpen={true} onClose={handleClose} />);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});
