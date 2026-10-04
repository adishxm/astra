import React, { useId } from 'react';
import { AlertTriangle, RotateCw, X } from 'lucide-react';
import Button from './Button';
import './ErrorBanner.css';

/**
 * @typedef {Object} ErrorBannerProps
 * @property {string} [title]
 * @property {string} message
 * @property {() => void} [onRetry]
 * @property {() => void} [onDismiss]
 * @property {string} [id]
 * @property {string} [className]
 */

export default function ErrorBanner({
  title,
  message,
  onRetry,
  onDismiss,
  id: customId,
  className = '',
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;

  const classes = ['error-banner', className].filter(Boolean).join(' ');

  return (
    <div id={elementId} className={classes} role="alert" {...rest}>
      <div className="error-banner__icon" aria-hidden="true">
        <AlertTriangle size={18} />
      </div>
      <div className="error-banner__body">
        {title && <strong className="error-banner__title">{title}</strong>}
        <p className="error-banner__message">{message}</p>
      </div>
      {(onRetry || onDismiss) && (
        <div className="error-banner__actions">
          {onRetry && (
            <Button
              variant="danger"
              size="sm"
              onClick={onRetry}
              icon={<RotateCw size={14} />}
            >
              Retry
            </Button>
          )}
          {onDismiss && (
            <button
              type="button"
              className="error-banner__dismiss"
              onClick={onDismiss}
              aria-label="Dismiss error"
            >
              <X size={16} aria-hidden="true" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
