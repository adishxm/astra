import React, { useId } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  HelpCircle,
  AlertOctagon,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import './Badge.css';

/**
 * @typedef {'safe' | 'vulnerable' | 'unknown' | 'critical' | 'high' | 'medium' | 'low' | 'info' | 'pass' | 'fail'} BadgeVariant
 */

/**
 * @typedef {Object} BadgeProps
 * @property {BadgeVariant} [variant='unknown']
 * @property {boolean} [pulse=false]
 * @property {boolean} [live=false]
 * @property {React.ReactNode} [icon]
 * @property {string} [id]
 * @property {string} [className]
 * @property {React.ReactNode} [children]
 */

const DEFAULT_LABELS = {
  safe: 'Safe',
  vulnerable: 'Vulnerable',
  unknown: 'Unknown',
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  info: 'Info',
  pass: 'Pass',
  fail: 'Fail',
};

function getDefaultIcon(variant) {
  const iconProps = { size: 13, className: 'badge__icon', 'aria-hidden': 'true' };
  switch (variant) {
    case 'safe':
      return <ShieldCheck {...iconProps} />;
    case 'vulnerable':
      return <ShieldAlert {...iconProps} />;
    case 'unknown':
      return <HelpCircle {...iconProps} />;
    case 'critical':
      return <AlertOctagon {...iconProps} />;
    case 'high':
      return <AlertTriangle {...iconProps} />;
    case 'medium':
      return <AlertCircle {...iconProps} />;
    case 'low':
      return <CheckCircle2 {...iconProps} />;
    case 'info':
      return <Info {...iconProps} />;
    case 'pass':
      return <CheckCircle2 {...iconProps} />;
    case 'fail':
      return <XCircle {...iconProps} />;
    default:
      return <HelpCircle {...iconProps} />;
  }
}

export default function Badge({
  variant = 'unknown',
  pulse = false,
  live = false,
  icon = null,
  id: customId,
  className = '',
  children,
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;
  const normalizedVariant = String(variant).toLowerCase();

  const label = children !== undefined && children !== null ? children : (DEFAULT_LABELS[normalizedVariant] || normalizedVariant);
  const badgeIcon = icon !== undefined && icon !== null ? icon : getDefaultIcon(normalizedVariant);

  const classes = [
    'badge',
    `badge--${normalizedVariant}`,
    pulse && normalizedVariant === 'critical' ? 'badge--pulse' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <span
      id={elementId}
      className={classes}
      role={live ? 'status' : undefined}
      aria-live={live ? 'polite' : undefined}
      {...rest}
    >
      {badgeIcon}
      <span className="badge__text">{label}</span>
    </span>
  );
}
