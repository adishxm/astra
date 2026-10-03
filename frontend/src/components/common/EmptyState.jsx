import React, { useId } from 'react';
import { useNavigate } from 'react-router-dom';
import { PackageOpen } from 'lucide-react';
import Button from './Button';
import './EmptyState.css';

/**
 * @typedef {Object} EmptyStateProps
 * @property {React.ReactNode} [icon]
 * @property {string} title
 * @property {string} message
 * @property {string} [ctaLabel]
 * @property {string} [ctaTo]
 * @property {() => void} [onCta]
 * @property {string} [id]
 * @property {string} [className]
 */

export default function EmptyState({
  icon,
  title,
  message,
  ctaLabel,
  ctaTo,
  onCta,
  id: customId,
  className = '',
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;
  const navigate = useNavigate();

  const handleCtaClick = (e) => {
    if (onCta) {
      onCta(e);
    }
    if (ctaTo) {
      navigate(ctaTo);
    }
  };

  const classes = ['empty-state', className].filter(Boolean).join(' ');

  return (
    <div id={elementId} className={classes} {...rest}>
      <div className="empty-state__icon" aria-hidden="true">
        {icon || <PackageOpen size={48} />}
      </div>
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__message">{message}</p>
      {ctaLabel && (
        <div className="empty-state__cta">
          <Button variant="primary" onClick={handleCtaClick}>
            {ctaLabel}
          </Button>
        </div>
      )}
    </div>
  );
}
