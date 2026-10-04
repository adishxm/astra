import React, { useId } from 'react';
import './ProgressRing.css';

/* eslint-disable react-refresh/only-export-components */
/**
 * Pure function to map progress percentage to tone
 * @param {number} value
 * @returns {'danger' | 'warning' | 'good'}
 */
export const getProgressTone = (value) => {
  const num = Number(value);
  if (isNaN(num) || num < 50) {
    return 'danger';
  }
  if (num < 80) {
    return 'warning';
  }
  return 'good';
};

/**
 * @typedef {Object} ProgressRingProps
 * @property {number} value (0 - 100)
 * @property {number} [size=100]
 * @property {number} [strokeWidth=8]
 * @property {string} [label]
 * @property {'danger' | 'warning' | 'good' | 'neutral' | 'info'} [tone]
 * @property {string} [id]
 * @property {string} [className]
 */

export default function ProgressRing({
  value = 0,
  size = 100,
  strokeWidth = 8,
  label,
  tone,
  id: customId,
  className = '',
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;

  const rawNum = typeof value === 'number' ? value : parseFloat(value);
  const clampedValue = isNaN(rawNum) ? 0 : Math.min(100, Math.max(0, Math.round(rawNum)));
  const computedTone = tone || getProgressTone(clampedValue);

  const center = size / 2;
  const radius = center - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clampedValue / 100) * circumference;

  const classes = [
    'progress-ring',
    `progress-ring--${computedTone}`,
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div
      id={elementId}
      className={classes}
      role="progressbar"
      aria-valuenow={clampedValue}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label || `Progress: ${clampedValue}%`}
      style={{ width: `${size}px`, height: `${size}px` }}
      {...rest}
    >
      <svg
        className="progress-ring__svg"
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
      >
        <circle
          className="progress-ring__bg"
          cx={center}
          cy={center}
          r={radius}
          strokeWidth={strokeWidth}
        />
        <circle
          className="progress-ring__bar"
          cx={center}
          cy={center}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
      <div className="progress-ring__content">
        <span className="progress-ring__value">{clampedValue}%</span>
        {label && <span className="progress-ring__label">{label}</span>}
      </div>
    </div>
  );
}
