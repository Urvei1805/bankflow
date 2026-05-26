import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { LayoutDashboard, Receipt, BarChart2, ShieldAlert, Activity, Settings as SettingsIcon } from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Dashboard" },
    { to: "/transactions", icon: Receipt, label: "Transactions" },
    { to: "/analytics", icon: BarChart2, label: "Analytics" },
    { to: "/risk", icon: ShieldAlert, label: "Risk Monitoring" },
    { to: "/health", icon: Activity, label: "API Health" },
    { to: "/settings", icon: SettingsIcon, label: "Settings" },
  ];

  return (
    <aside style={{ width: '250px', display: 'flex', flexDirection: 'column', background: 'var(--color-surface)', borderRight: '1px solid var(--color-border)' }}>
      <div style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'linear-gradient(135deg, var(--color-primary), var(--color-secondary))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>B</div>
        <h1 className="text-xl font-bold" style={{ letterSpacing: '-0.5px' }}>BankFlow</h1>
      </div>
      <nav style={{ flex: 1, padding: '0 1rem' }}>
        <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.to}>
                <NavLink 
                  to={item.to}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.75rem',
                    padding: '0.75rem 1rem',
                    borderRadius: '8px',
                    color: isActive ? 'var(--color-text)' : 'var(--color-text-muted)',
                    background: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                    fontWeight: isActive ? 600 : 500,
                    transition: 'all 0.2s',
                  })}
                >
                  <Icon size={18} style={{ color: 'inherit' }} />
                  {item.label}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>
      <div style={{ padding: '1.5rem', borderTop: '1px solid var(--color-border)' }}>
        <div className="text-xs text-muted">BankFlow Admin SOC</div>
        <div className="text-xs text-muted" style={{ marginTop: '0.25rem' }}>v1.0.0</div>
      </div>
    </aside>
  );
};

const Topbar = () => {
  return (
    <header style={{ height: '64px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 2rem', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)' }}>
      <div className="text-sm text-muted">
        Environment: <span className="text-success font-medium px-2 py-1" style={{ background: 'var(--color-success-bg)', borderRadius: '4px' }}>Production</span>
      </div>
      <div className="flex items-center gap-4">
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--color-success)', boxShadow: '0 0 8px var(--color-success)' }} className="animate-pulse" title="System Live"></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-primary-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.875rem', fontWeight: 600 }}>A</div>
          <span className="text-sm font-medium">Admin User</span>
        </div>
      </div>
    </header>
  );
};

export const Layout = () => {
  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Topbar />
        <main style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
