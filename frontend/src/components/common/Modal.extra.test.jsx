import React, { useState } from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Modal from './Modal';

function FocusTrapHarness() {
  const [open, setOpen] = useState(false);

  return (
    <div>
      <button type="button" id="trigger-btn" onClick={() => setOpen(true)}>
        Open Modal
      </button>
      <Modal open={open} onClose={() => setOpen(false)} title="Focus Trap Modal">
        <input type="text" placeholder="First Field" data-testid="field-1" />
        <button type="button" data-testid="btn-inside">Inside Action</button>
      </Modal>
    </div>
  );
}

describe('Modal (Focus Trap & Restoration Extra)', () => {
  it('traps focus and restores focus upon close', async () => {
    const user = userEvent.setup();
    render(<FocusTrapHarness />);

    const triggerBtn = screen.getByRole('button', { name: /open modal/i });
    triggerBtn.focus();
    expect(document.activeElement).toBe(triggerBtn);

    await user.click(triggerBtn);

    const dialog = screen.getByRole('dialog');
    expect(dialog).toBeInTheDocument();

    const field1 = screen.getByTestId('field-1');
    const insideBtn = screen.getByTestId('btn-inside');
    const closeBtn = screen.getByRole('button', { name: /close dialog/i });

    expect(field1).toBeInTheDocument();
    expect(insideBtn).toBeInTheDocument();
    expect(closeBtn).toBeInTheDocument();

    // Focus starts inside the dialog
    expect(dialog.contains(document.activeElement)).toBe(true);

    // Press Escape to close modal
    await user.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

    // Focus restored to trigger
    expect(document.activeElement).toBe(triggerBtn);
  });
});
