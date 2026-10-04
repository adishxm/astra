import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Tooltip, { computeTooltipPosition } from './Tooltip';

describe('Tooltip', () => {
  it('shows on hover', async () => {
    const user = userEvent.setup();
    render(
      <Tooltip content="Helpful tooltip text">
        <button type="button">Hover Trigger</button>
      </Tooltip>
    );

    const trigger = screen.getByRole('button', { name: /hover trigger/i });
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();

    await user.hover(trigger);
    const tooltip = screen.getByRole('tooltip');
    expect(tooltip).toBeInTheDocument();
    expect(tooltip).toHaveTextContent('Helpful tooltip text');

    await user.unhover(trigger);
    expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  });

  it('computeTooltipPosition flips when it would overflow', () => {
    const triggerRect = { top: 10, left: 100, right: 180, bottom: 40, width: 80, height: 30 };
    const tooltipRect = { width: 120, height: 40 };
    const viewport = { width: 800, height: 600 };

    // When requested 'top' overflows top boundary (top is at 10, height is 40, 10 - 40 - 8 < 0)
    const posTop = computeTooltipPosition(triggerRect, tooltipRect, 'top', viewport, 8);
    expect(posTop.actualPlacement).toBe('bottom');
    expect(posTop.top).toBe(triggerRect.bottom + 8);

    // When requested 'left' overflows left boundary
    const triggerLeft = { top: 200, left: 20, right: 100, bottom: 230, width: 80, height: 30 };
    const posLeft = computeTooltipPosition(triggerLeft, tooltipRect, 'left', viewport, 8);
    expect(posLeft.actualPlacement).toBe('right');
    expect(posLeft.left).toBe(triggerLeft.right + 8);
  });
});
