import React from 'react';

export const StatCard = ({ title, value, icon: Icon, trend, trendValue, subtitle }) => {
  return (
    <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm text-muted font-medium">{title}</h3>
        {Icon && <div style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}><Icon size={18} className="text-primary" /></div>}
      </div>
      <div className="flex items-baseline gap-2">
        <h2 className="text-2xl font-bold">{value}</h2>
        {trend && (
          <span className={`text-xs font-medium ${trend === 'up' ? 'text-success' : 'text-danger'}`}>
            {trend === 'up' ? '↑' : '↓'} {trendValue}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-muted">{subtitle}</p>}
    </div>
  );
};

export const ChartCard = ({ title, children, action }) => {
  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 className="font-semibold">{title}</h3>
        {action}
      </div>
      <div style={{ padding: '1.5rem', flex: 1 }}>
        {children}
      </div>
    </div>
  );
};

export const RiskBadge = ({ level }) => {
  const styles = {
    LOW: { bg: 'var(--color-success-bg)', color: 'var(--color-success)' },
    MEDIUM: { bg: 'var(--color-warning-bg)', color: 'var(--color-warning)' },
    HIGH: { bg: 'var(--color-danger-bg)', color: 'var(--color-danger)' }
  };
  
  const style = styles[level] || { bg: 'rgba(255,255,255,0.1)', color: 'white' };
  
  return (
    <span style={{ 
      background: style.bg, 
      color: style.color, 
      padding: '0.25rem 0.5rem', 
      borderRadius: '999px', 
      fontSize: '0.75rem', 
      fontWeight: 600,
      letterSpacing: '0.05em'
    }}>
      {level}
    </span>
  );
};

export const LoadingSkeleton = ({ height = '200px' }) => (
  <div style={{ height, background: 'rgba(255,255,255,0.05)', borderRadius: '8px', animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }} />
);

export const EmptyState = ({ message, icon: Icon }) => (
  <div className="flex flex-col items-center justify-center gap-4" style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
    {Icon && <Icon size={48} opacity={0.5} />}
    <p>{message}</p>
  </div>
);
