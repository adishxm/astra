import React, { useState, useRef, useId, cloneElement } from 'react';
import { createPortal } from 'react-dom';
import './Tooltip.css';

/* eslint-disable react-refresh/only-export-components */
/**
 * Pure function to compute tooltip position with viewport flipping
 * @param {{top: number, left: number, right: number, bottom: number, width: number, height: number}} triggerRect
 * @param {{width: number, height: number}} tooltipRect
 * @param {'top' | 'bottom' | 'left' | 'right'} placement
 * @param {{width: number, height: number}} [viewport]
 * @param {number} [offset=8]
 * @returns {{top: number, left: number, actualPlacement: string}}
 */
export const computeTooltipPosition = (
  triggerRect,
  tooltipRect,
  placement = 'top',
  viewport = {
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
  },
  offset = 8
) => {
  let actualPlacement = placement;
  let top = 0;
  let left = 0;

  if (placement === 'top') {
    top = triggerRect.top - tooltipRect.height - offset;
    left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
    if (top < 0 && triggerRect.bottom + tooltipRect.height + offset <= viewport.height) {
      actualPlacement = 'bottom';
      top = triggerRect.bottom + offset;
    }
  } else if (placement === 'bottom') {
    top = triggerRect.bottom + offset;
    left = triggerRect.left + (triggerRect.width - tooltipRect.width) / 2;
    if (top + tooltipRect.height > viewport.height && triggerRect.top - tooltipRect.height - offset >= 0) {
      actualPlacement = 'top';
      top = triggerRect.top - tooltipRect.height - offset;
    }
  } else if (placement === 'left') {
    left = triggerRect.left - tooltipRect.width - offset;
    top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
    if (left < 0 && triggerRect.right + tooltipRect.width + offset <= viewport.width) {
      actualPlacement = 'right';
      left = triggerRect.right + offset;
    }
  } else if (placement === 'right') {
    left = triggerRect.right + offset;
    top = triggerRect.top + (triggerRect.height - tooltipRect.height) / 2;
    if (left + tooltipRect.width > viewport.width && triggerRect.left - tooltipRect.width - offset >= 0) {
      actualPlacement = 'left';
      left = triggerRect.left - tooltipRect.width - offset;
    }
  }

  // Clamping to ensure tooltip remains visible on screen
  if (left < 4) left = 4;
  if (left + tooltipRect.width > viewport.width - 4) {
    left = Math.max(4, viewport.width - tooltipRect.width - 4);
  }

  return { top, left, actualPlacement };
}

/**
 * @typedef {Object} TooltipProps
 * @property {React.ReactNode} content
 * @property {'top' | 'bottom' | 'left' | 'right'} [placement='top']
 * @property {string} [id]
 * @property {string} [className]
 * @property {React.ReactElement} children
 */

export default function Tooltip({
  content,
  placement = 'top',
  id: customId,
  className = '',
  children,
  ...rest
}) {
  const generatedId = useId();
  const tooltipId = customId || `tooltip-${generatedId}`;

  const [visible, setVisible] = useState(false);
  const [coords, setCoords] = useState({ top: 0, left: 0, actualPlacement: placement });
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);

  const updatePosition = () => {
    if (!triggerRef.current) return;
    const triggerRect = triggerRef.current.getBoundingClientRect();
    const tooltipRect = tooltipRef.current
      ? tooltipRef.current.getBoundingClientRect()
      : { width: 120, height: 32 };

    const pos = computeTooltipPosition(triggerRect, tooltipRect, placement);
    setCoords(pos);
  };

  const show = () => {
    setVisible(true);
    // Recalculate position on next tick
    setTimeout(updatePosition, 0);
  };

  const hide = () => {
    setVisible(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      hide();
    }
  };

  const trigger = React.isValidElement(children) ? (
    cloneElement(children, {
      ref: triggerRef,
      'aria-describedby': visible ? tooltipId : undefined,
      onMouseEnter: (e) => {
        children.props?.onMouseEnter?.(e);
        show();
      },
      onMouseLeave: (e) => {
        children.props?.onMouseLeave?.(e);
        hide();
      },
      onFocus: (e) => {
        children.props?.onFocus?.(e);
        show();
      },
      onBlur: (e) => {
        children.props?.onBlur?.(e);
        hide();
      },
      onKeyDown: (e) => {
        children.props?.onKeyDown?.(e);
        handleKeyDown(e);
      },
    })
  ) : (
    <span
      ref={triggerRef}
      role="button"
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
      tabIndex={0}
      aria-describedby={visible ? tooltipId : undefined}
    >
      {children}
    </span>
  );

  return (
    <>
      {trigger}
      {visible &&
        createPortal(
          <div
            ref={tooltipRef}
            id={tooltipId}
            role="tooltip"
            className={['tooltip', `tooltip--${coords.actualPlacement}`, className].filter(Boolean).join(' ')}
            style={{
              top: `${coords.top}px`,
              left: `${coords.left}px`,
            }}
            {...rest}
          >
            {content}
          </div>,
          document.body
        )}
    </>
  );
}
