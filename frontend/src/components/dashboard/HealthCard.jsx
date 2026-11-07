import React from 'react';
import { Activity, CheckCircle, AlertTriangle, Clock, Server } from 'lucide-react';
import { formatDateTime } from '../../utils/formatters';

export function HealthCard({ health, loading, onRefresh }) {
  const isHealthy = health?.status === 'healthy';

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-lg ${isHealthy ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 text-base">Backend Health Status</h3>
            <p className="text-xs text-slate-500">Live FastAPI Health-Check Monitor</p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1.5 ${
          isHealthy ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
        }`}>
          {isHealthy ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
          <span className="capitalize">{health?.status || 'Unknown'}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-100 text-xs">
        <div>
          <span className="text-slate-400 block mb-0.5">App Version</span>
          <span className="font-semibold text-slate-700 font-mono">{health?.version || 'N/A'}</span>
        </div>
        <div>
          <span className="text-slate-400 block mb-0.5">Environment</span>
          <span className="font-semibold text-slate-700 capitalize">{health?.environment || 'N/A'}</span>
        </div>
        <div>
          <span className="text-slate-400 block mb-0.5">Last Checked</span>
          <span className="font-semibold text-slate-700 font-mono">
            {formatDateTime(health?.timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
}

export default HealthCard;

