import React, { useState } from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TabBar, { TabPanel } from './TabBar';

function ControlledTabBar({ tabs, onChange }) {
  const [activeTab, setActiveTab] = useState(tabs[0].id);
  return (
    <div>
      <TabBar
        tabs={tabs}
        value={activeTab}
        onChange={(id) => {
          setActiveTab(id);
          onChange?.(id);
        }}
      />
      {tabs.map((tab) => (
        <TabPanel key={tab.id} id={tab.id} active={activeTab === tab.id}>
          {tab.label} Panel Content
        </TabPanel>
      ))}
    </div>
  );
}

describe('TabBar', () => {
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'assets', label: 'Assets' },
    { id: 'compliance', label: 'Compliance' },
  ];

  it('tab selection changes active tab', async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<ControlledTabBar tabs={tabs} onChange={handleChange} />);

    const assetsTab = screen.getByRole('tab', { name: /assets/i });
    expect(assetsTab).toHaveAttribute('aria-selected', 'false');

    await user.click(assetsTab);
    expect(assetsTab).toHaveAttribute('aria-selected', 'true');
    expect(handleChange).toHaveBeenCalledWith('assets');
    expect(screen.getByText('Assets Panel Content')).toBeVisible();
  });

  it('keyboard ArrowRight moves selection/focus', async () => {
    const user = userEvent.setup();
    render(<ControlledTabBar tabs={tabs} />);

    const overviewTab = screen.getByRole('tab', { name: /overview/i });
    const assetsTab = screen.getByRole('tab', { name: /assets/i });

    overviewTab.focus();
    expect(document.activeElement).toBe(overviewTab);

    await user.keyboard('{ArrowRight}');
    expect(document.activeElement).toBe(assetsTab);
    expect(assetsTab).toHaveAttribute('aria-selected', 'true');
  });
});
