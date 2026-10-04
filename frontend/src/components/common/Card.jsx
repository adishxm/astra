import React, { useId } from 'react';
import './Card.css';

/**
 * @typedef {Object} CardProps
 * @property {'default' | 'elevated' | 'glass' | 'interactive'} [variant='default']
 * @property {React.ReactNode} [title]
 * @property {React.ReactNode} [actions]
 * @property {string} [id]
 * @property {string} [className]
 * @property {React.ReactNode} [children]
 * @property {React.MouseEventHandler} [onClick]
 * @property {React.ElementType} [as='section']
 */

export default function Card({
  variant = 'default',
  title = null,
  actions = null,
  id: customId,
  className = '',
  children,
  onClick,
  as: Component = 'section',
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;
  const isInteractive = variant === 'interactive' || Boolean(onClick);

  const handleKeyDown = (e) => {
    if (isInteractive && onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick(e);
    }
  };

  const classes = [
    'card',
    `card--${variant}`,
    isInteractive ? 'card--interactive' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <Component
      id={elementId}
      className={classes}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      tabIndex={isInteractive && onClick ? 0 : undefined}
      role={isInteractive && onClick ? 'button' : undefined}
      {...rest}
    >
      {(title || actions) && (
        <header className="card__header">
          {title && (typeof title === 'string' ? <h3 className="card__title">{title}</h3> : title)}
          {actions && <div className="card__actions">{actions}</div>}
        </header>
      )}
      <div className="card__body">{children}</div>
    </Component>
  );
}
