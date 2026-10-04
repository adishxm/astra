import React, { useEffect, useRef, useId } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import './Modal.css';

/**
 * @typedef {Object} ModalProps
 * @property {boolean} open
 * @property {() => void} onClose
 * @property {React.ReactNode} title
 * @property {string} [description]
 * @property {boolean} [closeOnBackdrop=true]
 * @property {'sm' | 'md' | 'lg' | 'xl'} [size='md']
 * @property {string} [id]
 * @property {string} [className]
 * @property {React.ReactNode} [children]
 */

export default function Modal({
  open = false,
  onClose,
  title,
  description,
  closeOnBackdrop = true,
  size = 'md',
  id: customId,
  className = '',
  children,
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;
  const titleId = `modal-title-${elementId}`;
  const descId = description ? `modal-desc-${elementId}` : undefined;

  const modalRef = useRef(null);
  const previousFocusRef = useRef(null);

  useEffect(() => {
    if (!open) return;

    // Save previous active element to restore focus on close
    previousFocusRef.current = document.activeElement;

    // Lock body scroll
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    // Focus first focusable element in modal
    const focusableSelectors = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const focusableElements = modalRef.current?.querySelectorAll(focusableSelectors);
    if (focusableElements && focusableElements.length > 0) {
      focusableElements[0].focus();
    } else {
      modalRef.current?.focus();
    }

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose?.();
        return;
      }

      if (e.key === 'Tab') {
        const focusable = modalRef.current?.querySelectorAll(focusableSelectors);
        if (!focusable || focusable.length === 0) {
          e.preventDefault();
          return;
        }

        const firstElement = focusable[0];
        const lastElement = focusable[focusable.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      document.removeEventListener('keydown', handleKeyDown);
      if (previousFocusRef.current && typeof previousFocusRef.current.focus === 'function') {
        previousFocusRef.current.focus();
      }
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && closeOnBackdrop) {
      onClose?.();
    }
  };

  const modalContent = (
    <div className="modal-backdrop" onClick={handleBackdropClick} role="presentation">
      <div
        ref={modalRef}
        id={elementId}
        className={['modal', `modal--${size}`, className].filter(Boolean).join(' ')}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descId}
        tabIndex={-1}
        {...rest}
      >
        <header className="modal__header">
          <div>
            <h2 id={titleId} className="modal__title">
              {title}
            </h2>
            {description && (
              <p id={descId} className="modal__description">
                {description}
              </p>
            )}
          </div>
          <button
            type="button"
            className="modal__close"
            onClick={onClose}
            aria-label="Close dialog"
          >
            <X size={18} aria-hidden="true" />
          </button>
        </header>
        <div className="modal__body">{children}</div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
