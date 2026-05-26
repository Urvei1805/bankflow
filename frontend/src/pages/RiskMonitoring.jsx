import React from 'react';
import { useTransactionStream } from '../hooks/useTransactionStream';
import { RiskBadge, ChartCard, StatCard } from '../components/Shared';
import { formatCurrency, formatDate } from '../utils/formatters';
import { ShieldAlert, AlertTriangle, Eye, Shield } from 'lucide-react';

const RiskMonitoring = () => {
  const { transactions } = useTransactionStream();
  const highRiskTxs = transactions.filter(tx => tx.risk_level === 'HIGH' || tx.risk_score >= 80);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-danger">SOC Risk Monitoring</h1>
          <p className="text-muted">High-priority alerts and fraud prevention rules</p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6 md:grid-cols-2">
        <StatCard title="Active Threats" value={highRiskTxs.length} icon={ShieldAlert} trend="up" trendValue="2" />
        <StatCard title="Blocked IP Attempts" value="142" icon={Shield} />
        <StatCard title="Suspicious Entities" value="18" icon={Eye} />
        <StatCard title="System Risk Level" value="ELEVATED" icon={AlertTriangle} subtitle="Requires attention" />
      </div>

      <div className="grid grid-cols-3 gap-6" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--color-danger)' }}>
          <h3 className="font-semibold flex items-center gap-2"><AlertTriangle size={18} className="text-danger" /> High Amount Rule</h3>
          <p className="text-sm text-muted mt-2">Flags any transaction exceeding standard account limits by 300% or greater.</p>
          <div className="mt-4 text-xs font-medium text-danger bg-danger-bg px-2 py-1 rounded inline-block">Triggered 4 times today</div>
        </div>
        
        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--color-warning)' }}>
          <h3 className="font-semibold flex items-center gap-2"><ShieldAlert size={18} className="text-warning" /> Velocity Rule</h3>
          <p className="text-sm text-muted mt-2">Flags accounts making more than 10 transactions within a 5-minute window.</p>
          <div className="mt-4 text-xs font-medium text-warning bg-warning-bg px-2 py-1 rounded inline-block">Triggered 12 times today</div>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', borderLeft: '4px solid var(--color-danger)' }}>
          <h3 className="font-semibold flex items-center gap-2"><Eye size={18} className="text-danger" /> Geo-Mismatch Rule</h3>
          <p className="text-sm text-muted mt-2">Flags transactions originating from a foreign country distinct from user's primary residence.</p>
          <div className="mt-4 text-xs font-medium text-danger bg-danger-bg px-2 py-1 rounded inline-block">Triggered 1 time today</div>
        </div>
      </div>

      <ChartCard title="High Priority Review Queue">
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Severity</th>
                <th>Time</th>
                <th>Entity</th>
                <th>Triggered Rule</th>
                <th>Amount</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {highRiskTxs.map((tx) => (
                <tr key={tx.id}>
                  <td><RiskBadge level={tx.risk_level} /></td>
                  <td>{formatDate(tx.timestamp)}</td>
                  <td className="font-medium">{tx.merchant}</td>
                  <td className="text-danger">High Risk Score ({tx.risk_score})</td>
                  <td className="font-semibold">{formatCurrency(tx.amount)}</td>
                  <td>
                    <button className="btn btn-primary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>Review</button>
                  </td>
                </tr>
              ))}
              {highRiskTxs.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center text-muted" style={{ padding: '3rem' }}>
                    <Shield size={48} className="mx-auto mb-4 opacity-50" />
                    No high-risk transactions requiring review.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </ChartCard>
    </div>
  );
};

export default RiskMonitoring;
