import React from 'react';
import { ChartCard } from '../components/Shared';
import { Settings as SettingsIcon, Database, Server, Monitor } from 'lucide-react';

const Settings = () => {
  const envVars = [
    { key: 'VITE_AUTH_API_URL', val: import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001' },
    { key: 'VITE_BANKING_API_URL', val: import.meta.env.VITE_BANKING_API_URL || 'http://localhost:8002' },
    { key: 'VITE_ANALYTICS_API_URL', val: import.meta.env.VITE_ANALYTICS_API_URL || 'http://localhost:8003' },
    { key: 'VITE_WS_URL', val: import.meta.env.VITE_WS_URL || 'ws://localhost:8002' },
    { key: 'MODE', val: import.meta.env.MODE },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Preferences & Configuration</h1>
          <p className="text-muted">Manage local frontend settings</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 md:grid-cols-1">
        <ChartCard title="Environment Variables">
          <p className="text-sm text-muted mb-4">
            These variables are currently injected into the React build by Vite. 
            To change them, update your <code>.env</code> file or ECS task definition and rebuild the container.
          </p>
          <div className="flex flex-col gap-3">
            {envVars.map((env, i) => (
              <div key={i} className="flex justify-between items-center p-3 bg-white/5 rounded border border-white/5">
                <code className="text-sm text-accent">{env.key}</code>
                <span className="text-sm font-mono">{env.val}</span>
              </div>
            ))}
          </div>
        </ChartCard>

        <div className="flex flex-col gap-6">
          <ChartCard title="Display Options">
            <div className="flex items-center justify-between p-3 border-b border-white/5">
              <div>
                <h4 className="font-medium">Compact Table View</h4>
                <p className="text-xs text-muted">Reduce padding in data tables</p>
              </div>
              <input type="checkbox" className="toggle" defaultChecked />
            </div>
            <div className="flex items-center justify-between p-3 border-b border-white/5">
              <div>
                <h4 className="font-medium">Animations</h4>
                <p className="text-xs text-muted">Enable UI transitions and pulses</p>
              </div>
              <input type="checkbox" className="toggle" defaultChecked />
            </div>
            <div className="flex items-center justify-between p-3">
              <div>
                <h4 className="font-medium">Dark Mode</h4>
                <p className="text-xs text-muted">Force dark theme everywhere</p>
              </div>
              <input type="checkbox" className="toggle" defaultChecked disabled />
            </div>
          </ChartCard>

          <ChartCard title="Developer Options">
             <div className="p-4 bg-warning/10 border border-warning/20 rounded-lg text-warning">
               <h4 className="font-medium flex items-center gap-2 mb-2"><Monitor size={18} /> Demo Fallback Mode</h4>
               <p className="text-sm mb-3">
                 If backend APIs are completely unavailable, the UI can fall back to hardcoded mock data to allow UI development to continue.
               </p>
               <button className="btn btn-secondary text-white w-full border-warning/50 hover:bg-warning/20">Enable Mock Override</button>
             </div>
          </ChartCard>
        </div>
      </div>
    </div>
  );
};

export default Settings;
