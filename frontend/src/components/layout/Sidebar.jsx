import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ScanLine, ShieldAlert, Flame } from 'lucide-react';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: <LayoutDashboard size={18} aria-hidden="true" />, end: true },
  { to: '/scan', label: 'New Scan', icon: <ScanLine size={18} aria-hidden="true" />, end: false },
  { to: '/findings', label: 'Findings', icon: <ShieldAlert size={18} aria-hidden="true" />, end: false },
  { to: '/risk', label: 'Risk Assessment', icon: <Flame size={18} aria-hidden="true" />, end: false },
];

export default function Sidebar() {
  return (
    <aside className="app-sidebar">
      <nav aria-label="Main navigation" className="app-sidebar__nav">
        <ul className="app-sidebar__list">
          {NAV_ITEMS.map((item) => (
            <li key={item.to} className="app-sidebar__item">
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    'app-sidebar__link',
                    isActive ? 'app-sidebar__link--active' : '',
                  ]
                    .filter(Boolean)
                    .join(' ')
                }
              >
                <span className="app-sidebar__link-icon">{item.icon}</span>
                <span className="app-sidebar__link-text">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
