import React, { useId } from 'react';
import './Button.css';

/**
 * @typedef {Object} ButtonProps
 * @property {'primary' | 'secondary' | 'ghost' | 'danger'} [variant='primary']
 * @property {'sm' | 'md' | 'lg'} [size='md']
 * @property {boolean} [loading=false]
 * @property {boolean} [disabled=false]
 * @property {React.ReactNode} [icon]
 * @property {React.ElementType} [as='button']
 * @property {string} [type='button']
 * @property {string} [id]
 * @property {string} [className]
 * @property {React.ReactNode} [children]
 */

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon = null,
  as: Component = 'button',
  type = 'button',
  id: customId,
  className = '',
  children,
  onClick,
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;
  const isButton = Component === 'button';

  const handleClick = (e) => {
    if (disabled || loading) {
      e.preventDefault();
      return;
    }
    if (onClick) {
      onClick(e);
    }
  };

  const classes = [
    'btn',
    `btn--${variant}`,
    `btn--${size}`,
    loading ? 'btn--loading' : '',
    disabled ? 'btn--disabled' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const props = {
    id: elementId,
    className: classes,
    onClick: handleClick,
    'aria-busy': loading ? 'true' : undefined,
    'aria-disabled': disabled || loading ? 'true' : undefined,
    disabled: isButton ? disabled || loading : undefined,
    ...(isButton ? { type } : {}),
    ...rest,
  };

  return (
    <Component {...props}>
      {loading ? (
        <span className="btn__spinner" aria-hidden="true" />
      ) : icon ? (
        <span className="btn__icon" aria-hidden="true">
          {icon}
        </span>
      ) : null}
      <span className="btn__content">{children}</span>
    </Component>
  );
}
