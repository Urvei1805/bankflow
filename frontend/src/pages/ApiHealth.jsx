import React from 'react';
import { useServiceHealth } from '../hooks/useServiceHealth';
import { ChartCard, LoadingSkeleton } from '../components/Shared';
import { RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

const StatusIndicator = ({ status }) => {
  if (status === 'up' || status === 'healthy') return <div className="flex items-center gap-2 text-success"><CheckCircle size={18} /> Healthy</div>;
  if (status === 'down' || status === 'unhealthy') return <div className="flex items-center gap-2 text-danger"><XCircle size={18} /> Offline</div>;
  return <div className="flex items-center gap-2 text-muted"><Clock size={18} className="animate-spin" /> Checking...</div>;
};

const ApiHealth = () => {
  const { health, loading, lastRefreshed, refetch } = useServiceHealth();

  const services = [
    { name: 'Auth Service', key: 'auth', url: import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001' },
    { name: 'Banking API Service', key: 'banking', url: import.meta.env.VITE_BANKING_API_URL || 'http://localhost:8002' },
    { name: 'Analytics Service', key: 'analytics', url: import.meta.env.VITE_ANALYTICS_API_URL || 'http://localhost:8003' },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">System Health</h1>
          <p className="text-muted">Microservice status and latency</p>
        </div>
        <button 
          onClick={refetch} 
          disabled={loading}
          className="btn btn-secondary flex items-center gap-2"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh Status
        </button>
      </div>

      <div className="grid grid-cols-3 gap-6 md:grid-cols-1">
        {services.map((svc) => {
          const svcHealth = health[svc.key];
          const isUp = svcHealth?.status === 'up';
          return (
            <div key={svc.key} className="glass-panel" style={{ padding: '1.5rem' }}>
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-semibold text-lg">{svc.name}</h3>
                <StatusIndicator status={svcHealth?.status} />
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between border-b border-white/5 pb-2">
                  <span className="text-muted">URL</span>
                  <span className="font-medium">{svc.url}</span>
                </div>
                <div className="flex justify-between border-b border-white/5 py-2">
                  <span className="text-muted">Latency</span>
                  <span className="font-medium">{svcHealth?.latencyMs ? `${svcHealth.latencyMs}ms` : '-'}</span>
                </div>
                <div className="flex justify-between pt-2">
                  <span className="text-muted">Database</span>
                  <span className={svcHealth?.db_status === 'connected' ? 'text-success' : 'text-danger'}>
                    {svcHealth?.db_status || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <ChartCard title="WebSocket Connection">
         <div className="flex items-center gap-4 p-4 bg-white/5 rounded-lg border border-white/10">
           <div className="p-3 bg-primary/20 rounded-full">
             <RefreshCw className="text-primary" size={24} />
           </div>
           <div>
             <h4 className="font-medium">Transaction Stream</h4>
             <p className="text-sm text-muted">{import.meta.env.VITE_WS_URL || 'ws://localhost:8002'}/ws/transactions</p>
           </div>
           <div className="ml-auto">
             <span className="bg-success/20 text-success px-3 py-1 rounded-full text-sm font-medium">Ready</span>
           </div>
         </div>
      </ChartCard>
    </div>
  );
};

export default ApiHealth;
