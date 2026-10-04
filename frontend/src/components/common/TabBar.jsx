import React, { useState, useRef, useId } from 'react';
import './TabBar.css';

/**
 * @typedef {Object} TabItem
 * @property {string} id
 * @property {React.ReactNode} label
 * @property {React.ReactNode} [icon]
 * @property {React.ReactNode} [badge]
 * @property {boolean} [disabled]
 */

/**
 * @typedef {Object} TabBarProps
 * @property {TabItem[]} tabs
 * @property {string} [value]
 * @property {string} [defaultValue]
 * @property {(tabId: string) => void} [onChange]
 * @property {string} [ariaLabel]
 * @property {string} [id]
 * @property {string} [className]
 */

export function TabPanel({
  id,
  active,
  children,
  className = '',
  ...rest
}) {
  return (
    <div
      id={`panel-${id}`}
      role="tabpanel"
      aria-labelledby={`tab-${id}`}
      hidden={!active}
      tabIndex={0}
      className={['tab-panel', className].filter(Boolean).join(' ')}
      {...rest}
    >
      {active && children}
    </div>
  );
}

export default function TabBar({
  tabs = [],
  value,
  defaultValue,
  onChange,
  ariaLabel = 'Navigation Tabs',
  id: customId,
  className = '',
  ...rest
}) {
  const generatedId = useId();
  const elementId = customId || generatedId;

  const isControlled = value !== undefined;
  const [internalValue, setInternalValue] = useState(
    defaultValue !== undefined ? defaultValue : (tabs[0]?.id || '')
  );

  const activeId = isControlled ? value : internalValue;
  const tabRefs = useRef([]);

  const handleSelect = (tabId) => {
    if (!isControlled) {
      setInternalValue(tabId);
    }
    if (onChange) {
      onChange(tabId);
    }
  };

  const handleKeyDown = (e, index) => {
    const enabledIndices = tabs
      .map((t, idx) => (!t.disabled ? idx : null))
      .filter((idx) => idx !== null);

    const currentPos = enabledIndices.indexOf(index);
    if (currentPos === -1) return;

    let nextIndex = null;

    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const nextPos = (currentPos + 1) % enabledIndices.length;
      nextIndex = enabledIndices[nextPos];
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prevPos = (currentPos - 1 + enabledIndices.length) % enabledIndices.length;
      nextIndex = enabledIndices[prevPos];
    } else if (e.key === 'Home') {
      e.preventDefault();
      nextIndex = enabledIndices[0];
    } else if (e.key === 'End') {
      e.preventDefault();
      nextIndex = enabledIndices[enabledIndices.length - 1];
    }

    if (nextIndex !== null) {
      const nextTab = tabs[nextIndex];
      if (nextTab) {
        tabRefs.current[nextIndex]?.focus();
        handleSelect(nextTab.id);
      }
    }
  };

  const classes = ['tab-bar', className].filter(Boolean).join(' ');

  return (
    <div
      id={elementId}
      className={classes}
      role="tablist"
      aria-label={ariaLabel}
      {...rest}
    >
      {tabs.map((tab, idx) => {
        const isSelected = tab.id === activeId;
        const tabClasses = [
          'tab-item',
          isSelected ? 'tab-item--active' : '',
          tab.disabled ? 'tab-item--disabled' : '',
        ]
          .filter(Boolean)
          .join(' ');

        return (
          <button
            key={tab.id}
            ref={(el) => {
              tabRefs.current[idx] = el;
            }}
            id={`tab-${tab.id}`}
            type="button"
            role="tab"
            aria-selected={isSelected}
            aria-controls={`panel-${tab.id}`}
            tabIndex={isSelected ? 0 : -1}
            disabled={tab.disabled}
            className={tabClasses}
            onClick={() => handleSelect(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, idx)}
          >
            {tab.icon && <span className="tab-item__icon">{tab.icon}</span>}
            <span className="tab-item__label">{tab.label}</span>
            {tab.badge && <span className="tab-item__badge">{tab.badge}</span>}
            {isSelected && <span className="tab-item__indicator" aria-hidden="true" />}
          </button>
        );
      })}
    </div>
  );
}
