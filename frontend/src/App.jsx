import { useState, useEffect, useRef, useCallback } from 'react'
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, LineChart, Line, CartesianGrid, Legend,
} from 'recharts'

// ── Config ────────────────────────────────────────────────────
const API = {
  analytics: import.meta.env.VITE_ANALYTICS_API_URL || 'http://localhost:8003',
  banking: import.meta.env.VITE_BANKING_API_URL || 'http://localhost:8002',
  ws: import.meta.env.VITE_WS_URL || 'ws://localhost:8002',
}

const COLORS = {
  chart: ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6'],
  risk: { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#10b981' },
}

// ── Utility ───────────────────────────────────────────────────
function formatCurrency(val) {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(val)
}

function formatNumber(val) {
  return new Intl.NumberFormat('en-GB').format(val)
}

// ── Stat Card Component ──────────────────────────────────────
function StatCard({ icon, label, value, change }) {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <div className="stat-card-icon">{icon}</div>
        <span className="stat-label">{label}</span>
      </div>
      <div className="stat-value">{value}</div>
      {change && <div className="stat-change">{change}</div>}
    </div>
  )
}

// ── Main App ─────────────────────────────────────────────────
export default function App() {
  const [summary, setSummary] = useState(null)
  const [fraudData, setFraudData] = useState([])
  const [spendData, setSpendData] = useState([])
  const [transactions, setTransactions] = useState([])
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [latencyData, setLatencyData] = useState([])
  const wsRef = useRef(null)
  const latencyRef = useRef([])

  // ── Fetch Analytics Data ───────────────────────────────────
  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const [summaryRes, fraudRes, spendRes] = await Promise.allSettled([
        fetch(`${API.analytics}/v1/analytics/summary`).then(r => r.json()),
        fetch(`${API.analytics}/v1/analytics/fraud-distribution`).then(r => r.json()),
        fetch(`${API.analytics}/v1/analytics/spend-by-category`).then(r => r.json()),
      ])

      if (summaryRes.status === 'fulfilled') {
        setSummary(summaryRes.value?.data?.attributes || null)
      }

      if (fraudRes.status === 'fulfilled') {
        const dist = fraudRes.value?.data?.attributes?.distribution || []
        setFraudData(dist.map(d => ({
          name: d.risk_level,
          value: d.count,
          amount: d.total_amount,
          fill: COLORS.risk[d.risk_level] || '#6366f1',
        })))
      }

      if (spendRes.status === 'fulfilled') {
        const cats = spendRes.value?.data?.attributes?.categories || []
        setSpendData(cats.slice(0, 8).map(c => ({
          name: c.category,
          spend: c.total_spend,
          count: c.transaction_count,
        })))
      }
    } catch (err) {
      console.error('Analytics fetch error:', err)
      setError('Unable to connect to analytics service. Showing demo data.')
      // Fallback demo data
      setSummary({
        total_transactions: 48293,
        total_volume: 2847391.42,
        avg_transaction: 58.94,
        fraud_distribution: { HIGH: 1247, MEDIUM: 8341, LOW: 38705 },
      })
      setFraudData([
        { name: 'LOW', value: 38705, fill: COLORS.risk.LOW },
        { name: 'MEDIUM', value: 8341, fill: COLORS.risk.MEDIUM },
        { name: 'HIGH', value: 1247, fill: COLORS.risk.HIGH },
      ])
      setSpendData([
        { name: 'shopping', spend: 487291, count: 8432 },
        { name: 'groceries', spend: 392847, count: 12093 },
        { name: 'restaurants', spend: 284739, count: 6721 },
        { name: 'transport', spend: 198432, count: 9284 },
        { name: 'entertainment', spend: 156892, count: 4327 },
        { name: 'utilities', spend: 134298, count: 3892 },
        { name: 'healthcare', spend: 98432, count: 2143 },
        { name: 'travel', spend: 87291, count: 1893 },
      ])
    } finally {
      setLoading(false)
    }
  }, [])

  // ── WebSocket Connection ───────────────────────────────────
  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket(`${API.ws}/ws/transactions`)
      wsRef.current = ws

      ws.onopen = () => {
        setWsStatus('connected')
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        try {
          const txn = JSON.parse(event.data)
          setTransactions(prev => [txn, ...prev.slice(0, 49)])

          // Track latency (simulated)
          const now = new Date()
          const latencyPoint = {
            time: now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            latency: Math.floor(Math.random() * 40) + 5,
          }
          latencyRef.current = [...latencyRef.current.slice(-29), latencyPoint]
          setLatencyData([...latencyRef.current])
        } catch (e) {
          console.error('WS message parse error:', e)
        }
      }

      ws.onerror = () => setWsStatus('error')
      ws.onclose = () => {
        setWsStatus('disconnected')
        // Auto-reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000)
      }
    } catch {
      setWsStatus('error')
      // Generate mock transactions if WS fails
      generateMockFeed()
    }
  }, [])

  // ── Mock Transaction Feed (fallback) ───────────────────────
  const generateMockFeed = useCallback(() => {
    const categories = ['groceries', 'restaurants', 'transport', 'shopping', 'entertainment', 'utilities']
    const countries = ['GB', 'US', 'FR', 'DE', 'JP']

    const interval = setInterval(() => {
      const amount = +(Math.random() * 500 + 2).toFixed(2)
      const country = countries[Math.floor(Math.random() * countries.length)]
      const isForeign = country !== 'GB'
      const isHigh = amount > 300
      let score = 0
      if (isHigh) score += 0.3
      if (isForeign) score += 0.3
      let level = 'LOW'
      if (score >= 0.6) level = 'HIGH'
      else if (score >= 0.3) level = 'MEDIUM'

      const txn = {
        transaction_id: crypto.randomUUID(),
        merchant_name: `Merchant_${Math.floor(Math.random() * 100)}`,
        merchant_category: categories[Math.floor(Math.random() * categories.length)],
        amount,
        currency: 'GBP',
        country,
        transaction_type: Math.random() > 0.3 ? 'debit' : 'credit',
        fraud_risk_level: level,
        fraud_score: score,
        timestamp: new Date().toISOString(),
      }
      setTransactions(prev => [txn, ...prev.slice(0, 49)])

      const now = new Date()
      const latencyPoint = {
        time: now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        latency: Math.floor(Math.random() * 40) + 5,
      }
      latencyRef.current = [...latencyRef.current.slice(-29), latencyPoint]
      setLatencyData([...latencyRef.current])
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  // ── Effects ────────────────────────────────────────────────
  useEffect(() => {
    fetchAnalytics()
    connectWebSocket()

    return () => {
      if (wsRef.current) wsRef.current.close()
    }
  }, [fetchAnalytics, connectWebSocket])

  // If WS never connects, start mock feed
  useEffect(() => {
    if (wsStatus === 'error' || wsStatus === 'disconnected') {
      const timer = setTimeout(() => {
        if (transactions.length === 0) {
          const cleanup = generateMockFeed()
          return cleanup
        }
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [wsStatus, transactions.length, generateMockFeed])

  // ── Custom Tooltip ─────────────────────────────────────────
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null
    return (
      <div style={{
        background: '#1f2937', border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 8, padding: '10px 14px', fontSize: '0.8rem',
      }}>
        <p style={{ fontWeight: 600, marginBottom: 4 }}>{label}</p>
        {payload.map((p, i) => (
          <p key={i} style={{ color: p.color }}>
            {p.name}: {typeof p.value === 'number' && p.value > 100
              ? formatCurrency(p.value) : p.value}
          </p>
        ))}
      </div>
    )
  }

  // ── Render ─────────────────────────────────────────────────
  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="dashboard-logo">
          <div className="logo-icon">B</div>
          <div className="logo-text">
            <h1>BankFlow</h1>
            <p>Open Banking Analytics</p>
          </div>
        </div>
        <div className="header-status">
          <div className="status-dot"></div>
          {wsStatus === 'connected' ? 'Live Feed Active' : 'Demo Mode'}
        </div>
      </header>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {/* Stat Cards */}
      <div className="stats-grid">
        <StatCard
          icon="📊"
          label="Total Transactions"
          value={loading ? '—' : formatNumber(summary?.total_transactions || 0)}
          change="All time"
        />
        <StatCard
          icon="💷"
          label="Total Volume"
          value={loading ? '—' : formatCurrency(summary?.total_volume || 0)}
          change="Across all accounts"
        />
        <StatCard
          icon="📈"
          label="Avg Transaction"
          value={loading ? '—' : formatCurrency(summary?.avg_transaction || 0)}
          change="Per transaction"
        />
        <StatCard
          icon="🛡️"
          label="High Risk Alerts"
          value={loading ? '—' : formatNumber(summary?.fraud_distribution?.HIGH || 0)}
          change={`${formatNumber(summary?.fraud_distribution?.MEDIUM || 0)} medium risk`}
        />
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Fraud Distribution Pie */}
        <div className="chart-card">
          <div className="chart-title">
            Fraud Risk Distribution
            <div className="chart-subtitle">Transaction count by risk level</div>
          </div>
          {loading ? (
            <div className="loading-container"><div className="spinner" /></div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={fraudData}
                  cx="50%"
                  cy="50%"
                  innerRadius={65}
                  outerRadius={100}
                  paddingAngle={4}
                  dataKey="value"
                  stroke="none"
                >
                  {fraudData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  formatter={(val) => <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>{val}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Spend by Category Bar */}
        <div className="chart-card">
          <div className="chart-title">
            Spend by Category
            <div className="chart-subtitle">Total debit amounts by merchant category</div>
          </div>
          {loading ? (
            <div className="loading-container"><div className="spinner" /></div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={spendData} barSize={28}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                />
                <YAxis
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                  tickFormatter={(v) => `£${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="spend" radius={[6, 6, 0, 0]}>
                  {spendData.map((_, i) => (
                    <Cell key={i} fill={COLORS.chart[i % COLORS.chart.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* API Latency Trend */}
        <div className="chart-card">
          <div className="chart-title">
            API Latency Trend
            <div className="chart-subtitle">Response time in milliseconds (simulated)</div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={latencyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis
                dataKey="time"
                tick={{ fill: '#6b7280', fontSize: 10 }}
                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              />
              <YAxis
                tick={{ fill: '#6b7280', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
                domain={[0, 50]}
                tickFormatter={(v) => `${v}ms`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="latency"
                stroke="#6366f1"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#6366f1' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Placeholder for additional chart */}
        <div className="chart-card">
          <div className="chart-title">
            Transaction Volume Over Time
            <div className="chart-subtitle">Hourly transaction count</div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={latencyData.map((d, i) => ({
              time: d.time,
              volume: Math.floor(Math.random() * 200) + 50,
            }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis
                dataKey="time"
                tick={{ fill: '#6b7280', fontSize: 10 }}
                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              />
              <YAxis
                tick={{ fill: '#6b7280', fontSize: 11 }}
                axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="volume" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={12} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Real-Time Transaction Feed */}
      <div className="feed-section">
        <div className="feed-header">
          <span className="feed-title">🔴 Real-Time Transaction Feed</span>
          <div className="feed-badge">
            <div className="status-dot" style={{
              background: wsStatus === 'connected' ? '#10b981' : '#6366f1'
            }}></div>
            {transactions.length} transactions
          </div>
        </div>
        <ul className="feed-list">
          {transactions.length === 0 ? (
            <div className="loading-container">
              <div className="spinner" />
              <span>Waiting for transactions...</span>
            </div>
          ) : (
            transactions.map((txn) => (
              <li key={txn.transaction_id} className="feed-item">
                <div className="feed-icon">
                  {txn.transaction_type === 'credit' ? '💰' : '💳'}
                </div>
                <div className="feed-details">
                  <div className="feed-merchant">{txn.merchant_name}</div>
                  <div className="feed-category">{txn.merchant_category} · {txn.country}</div>
                </div>
                <span className={`feed-amount ${txn.transaction_type}`}>
                  {txn.transaction_type === 'credit' ? '+' : '-'}{formatCurrency(txn.amount)}
                </span>
                <span className={`risk-badge ${txn.fraud_risk_level?.toLowerCase()}`}>
                  {txn.fraud_risk_level}
                </span>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  )
}
