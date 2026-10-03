import React, { useId } from 'react';
import './LoadingSpinner.css';

/**
 * @typedef {Object} LoadingSpinnerProps
 * @property {'sm' | 'md' | 'lg'} [size='md']
 * @property {string} [label]
 * @property {number} [elapsedSeconds]
 * @property {string} [ariaLabel='Loading']
 * @property {string} [id]
 * @property {string} [className]
 */

export default function LoadingSpinner({
  size = 'md',
  label,
  elapsedSeconds,
  ariaLabel = 'Loading',
  id: customId,
  className = '',
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;

  const hasElapsed = typeof elapsedSeconds === 'number';
  const displayText = hasElapsed
    ? `${label || 'Analyzing...'} ${elapsedSeconds}s`
    : label;

  const classes = [
    'spinner-container',
    `spinner-container--${size}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div
      id={elementId}
      className={classes}
      role="status"
      aria-label={displayText || ariaLabel}
      {...rest}
    >
      <div className={`spinner spinner--${size}`} aria-hidden="true" />
      {displayText && (
        <span className="spinner__label">{displayText}</span>
      )}
    </div>
  );
}
