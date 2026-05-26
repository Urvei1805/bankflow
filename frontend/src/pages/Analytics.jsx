import React from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import { ChartCard, LoadingSkeleton } from '../components/Shared';
import { THEME_COLORS } from '../utils/constants';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const Analytics = () => {
  const { spendByCategory, loading } = useAnalytics();
  const spendData = (spendByCategory || [])
    .map(c => ({ name: c.category, value: c.total_spend }))
    .sort((a,b) => b.value - a.value);

  // Generate some mock timeline data since the API doesn't have a trend endpoint yet
  const timelineData = Array.from({ length: 30 }).map((_, i) => ({
    day: `Day ${i + 1}`,
    volume: Math.floor(Math.random() * 50000) + 10000,
    fraud: Math.floor(Math.random() * 2000)
  }));

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Deep Analytics</h1>
          <p className="text-muted">Historical trends and categorization</p>
        </div>
      </div>

      <ChartCard title="30-Day Transaction Volume Trend">
        <div style={{ height: 350 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timelineData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={THEME_COLORS.primary} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={THEME_COLORS.primary} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="day" stroke={THEME_COLORS.textMuted} tick={{fontSize: 12}} />
              <YAxis stroke={THEME_COLORS.textMuted} tick={{fontSize: 12}} />
              <RechartsTooltip contentStyle={{ background: THEME_COLORS.surface, border: '1px solid var(--color-border)', borderRadius: '8px' }} />
              <Area type="monotone" dataKey="volume" stroke={THEME_COLORS.primary} fillOpacity={1} fill="url(#colorVolume)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      <div className="grid grid-cols-2 gap-6" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))' }}>
        <ChartCard title="Top Spending Categories">
          {loading ? <LoadingSkeleton /> : (
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={spendData.slice(0, 5)} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" stroke={THEME_COLORS.textMuted} />
                  <YAxis stroke={THEME_COLORS.textMuted} />
                  <RechartsTooltip contentStyle={{ background: THEME_COLORS.surface, border: 'none', borderRadius: '8px' }} cursor={{fill: 'rgba(255,255,255,0.05)'}} />
                  <Bar dataKey="value" fill={THEME_COLORS.accent} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </ChartCard>
        
        <ChartCard title="Risk Volume Overlay">
           <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timelineData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={THEME_COLORS.danger} stopOpacity={0.4}/>
                      <stop offset="95%" stopColor={THEME_COLORS.danger} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="day" stroke={THEME_COLORS.textMuted} />
                  <YAxis stroke={THEME_COLORS.textMuted} />
                  <RechartsTooltip contentStyle={{ background: THEME_COLORS.surface, border: 'none', borderRadius: '8px' }} />
                  <Area type="monotone" dataKey="fraud" stroke={THEME_COLORS.danger} fillOpacity={1} fill="url(#colorFraud)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
        </ChartCard>
      </div>
    </div>
  );
};

export default Analytics;
