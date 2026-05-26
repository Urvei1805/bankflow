import React, { useState } from 'react';
import { useTransactionStream } from '../hooks/useTransactionStream';
import { RiskBadge } from '../components/Shared';
import { formatCurrency, formatDate } from '../utils/formatters';
import { Search, Filter, PlayCircle } from 'lucide-react';

const Transactions = () => {
  const { transactions, status, loadMockData } = useTransactionStream();
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');

  const filteredTransactions = transactions.filter(tx => {
    const matchesSearch = String(tx.merchant || '').toLowerCase().includes(searchTerm.toLowerCase()) || 
                          String(tx.id || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk = riskFilter === 'ALL' || tx.risk_level === riskFilter;
    return matchesSearch && matchesRisk;
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Transaction Explorer</h1>
          <p className="text-muted">Live view of network transactions</p>
        </div>
        {status !== 'connected' && (
          <button className="btn btn-secondary flex items-center gap-2" onClick={loadMockData}>
            <PlayCircle size={16} /> Load Demo Data
          </button>
        )}
      </div>

      <div className="glass-panel" style={{ padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} className="text-muted" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
          <input 
            type="text" 
            className="input" 
            placeholder="Search by merchant or ID..." 
            style={{ paddingLeft: '2.5rem' }}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={18} className="text-muted" />
          <select 
            className="input" 
            style={{ width: 'auto' }}
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="ALL">All Risk Levels</option>
            <option value="HIGH">High Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="LOW">Low Risk</option>
          </select>
        </div>
      </div>

      <div className="glass-panel table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Transaction ID</th>
              <th>Date & Time</th>
              <th>Merchant / Counterparty</th>
              <th>Category</th>
              <th>Amount</th>
              <th>Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {filteredTransactions.map((tx) => (
              <tr key={tx.id}>
                <td className="font-medium text-muted">{tx.id}</td>
                <td>{formatDate(tx.timestamp)}</td>
                <td className="font-medium">{tx.merchant}</td>
                <td>
                  <span style={{ padding: '0.2rem 0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', fontSize: '0.75rem' }}>
                    {tx.category || 'General'}
                  </span>
                </td>
                <td className={tx.type === 'CREDIT' ? 'text-success font-semibold' : 'font-semibold'}>
                  {tx.type === 'CREDIT' ? '+' : '-'}{formatCurrency(tx.amount)}
                </td>
                <td>
                  <div className="flex items-center gap-2">
                    <RiskBadge level={tx.risk_level} />
                    <span className="text-xs text-muted">({tx.risk_score})</span>
                  </div>
                </td>
              </tr>
            ))}
            {filteredTransactions.length === 0 && (
              <tr>
                <td colSpan="6" className="text-center text-muted" style={{ padding: '4rem' }}>
                  No transactions found matching your criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Transactions;
