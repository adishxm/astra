import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Tooltip, { computeTooltipPosition } from './Tooltip';

describe('Tooltip (focus, escape & placement extra)', () => {
  it('shows on focus and hides on blur and Escape', async () => {
    const user = userEvent.setup();
    render(
      <Tooltip content="Keyboard tooltip">
        <button type="button">Focusable Target</button>
      </Tooltip>
    );

    const btn = screen.getByRole('button', { name: /focusable target/i });
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();

    // Focus triggers tooltip
    await user.tab();
    expect(document.activeElement).toBe(btn);
    const tooltip = screen.getByRole('tooltip');
    expect(tooltip).toBeInTheDocument();
    expect(tooltip).toHaveTextContent('Keyboard tooltip');

    // Escape hides tooltip
    await user.keyboard('{Escape}');
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('renders with non-element children', async () => {
    const user = userEvent.setup();
    render(<Tooltip content="String child tooltip">Plain text trigger</Tooltip>);

    const trigger = screen.getByRole('button', { name: /plain text trigger/i });
    await user.hover(trigger);
    expect(screen.getByRole('tooltip')).toHaveTextContent('String child tooltip');
    await user.unhover(trigger);
  });

  it('computeTooltipPosition handles bottom and right overflow flipping', () => {
    const tooltipRect = { width: 100, height: 40 };
    const viewport = { width: 500, height: 500 };

    // Overflow bottom -> flips to top
    const triggerBottom = { top: 460, bottom: 490, left: 100, right: 180, width: 80, height: 30 };
    const posBottom = computeTooltipPosition(triggerBottom, tooltipRect, 'bottom', viewport, 8);
    expect(posBottom.actualPlacement).toBe('top');

    // Overflow right -> flips to left
    const triggerRight = { top: 100, bottom: 130, left: 420, right: 490, width: 70, height: 30 };
    const posRight = computeTooltipPosition(triggerRight, tooltipRect, 'right', viewport, 8);
    expect(posRight.actualPlacement).toBe('left');
  });
});
