import React from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import { useTransactionStream } from '../hooks/useTransactionStream';
import { StatCard, ChartCard, RiskBadge, LoadingSkeleton } from '../components/Shared';
import { formatCurrency, formatNumber } from '../utils/formatters';
import { Activity, DollarSign, AlertTriangle, Hash } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';
import { THEME_COLORS } from '../utils/constants';

const Dashboard = () => {
  const { summary, fraudDistribution, spendByCategory, loading: analyticsLoading } = useAnalytics();
  const { transactions, status } = useTransactionStream();

  const fraudData = (fraudDistribution || []).map(f => ({ name: f.risk_level, value: f.count }));
  const spendData = (spendByCategory || []).map(c => ({ name: c.category, value: c.total_spend }));

  const COLORS = [THEME_COLORS.success, THEME_COLORS.warning, THEME_COLORS.danger];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Platform Overview</h1>
          <p className="text-muted">Real-time banking analytics and fraud monitoring</p>
        </div>
        <div className="flex items-center gap-2 glass-panel" style={{ padding: '0.5rem 1rem' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: status === 'connected' ? THEME_COLORS.success : THEME_COLORS.danger }} className={status === 'connected' ? 'animate-pulse' : ''} />
          <span className="text-sm font-medium">WebSocket: {status}</span>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-6 md:grid-cols-2" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
        <StatCard 
          title="Total Volume" 
          value={analyticsLoading ? '...' : formatCurrency(summary?.total_volume)}
          icon={DollarSign}
          trend="up"
          trendValue="12%"
        />
        <StatCard 
          title="Total Transactions" 
          value={analyticsLoading ? '...' : formatNumber(summary?.total_transactions)}
          icon={Hash}
        />
        <StatCard 
          title="Avg Transaction" 
          value={analyticsLoading ? '...' : formatCurrency(summary?.avg_transaction)}
          icon={Activity}
        />
        <StatCard 
          title="High Risk Alerts" 
          value={analyticsLoading ? '...' : formatNumber(summary?.fraud_distribution?.HIGH || 0)}
          icon={AlertTriangle}
          trend="down"
          trendValue="4%"
        />
      </div>

      <div className="grid gap-6" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
        <ChartCard title="Fraud Risk Distribution">
          {analyticsLoading ? <LoadingSkeleton /> : (
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={fraudData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                    {fraudData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: THEME_COLORS.surface, border: 'none', borderRadius: '8px', color: 'white' }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </ChartCard>

        <ChartCard title="Spend by Category">
          {analyticsLoading ? <LoadingSkeleton /> : (
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={spendData} layout="vertical" margin={{ left: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                  <XAxis type="number" stroke={THEME_COLORS.textMuted} />
                  <YAxis dataKey="name" type="category" stroke={THEME_COLORS.textMuted} />
                  <Tooltip contentStyle={{ background: THEME_COLORS.surface, border: 'none', borderRadius: '8px', color: 'white' }} />
                  <Bar dataKey="value" fill={THEME_COLORS.primary} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </ChartCard>
      </div>

      <ChartCard title="Live Transaction Feed">
        <div className="table-container" style={{ maxHeight: '400px', overflowY: 'auto' }}>
          <table className="table">
            <thead style={{ position: 'sticky', top: 0, zIndex: 10 }}>
              <tr>
                <th>ID</th>
                <th>Time</th>
                <th>Merchant</th>
                <th>Amount</th>
                <th>Risk</th>
              </tr>
            </thead>
            <tbody>
              {transactions.slice(0, 10).map((tx) => (
                <tr key={tx.id}>
                  <td className="font-medium text-muted">...{String(tx.id).slice(-8)}</td>
                  <td>{new Date(tx.timestamp).toLocaleTimeString()}</td>
                  <td>{tx.merchant}</td>
                  <td className={tx.type === 'CREDIT' ? 'text-success' : ''}>
                    {tx.type === 'CREDIT' ? '+' : ''}{formatCurrency(tx.amount)}
                  </td>
                  <td><RiskBadge level={tx.risk_level} /></td>
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center text-muted" style={{ padding: '2rem' }}>
                    Waiting for live transactions...
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

export default Dashboard;
