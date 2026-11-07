import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

export function Alert({ type = 'error', title, message, onRetry }) {
  const styles = {
    error: {
      bg: 'bg-accent-coral/10 border-accent-coral/30 text-accent-coral',
      icon: <AlertCircle className="w-4 h-4 text-accent-coral flex-shrink-0" />,
    },
    warning: {
      bg: 'bg-accent-amber/10 border-accent-amber/30 text-accent-amber',
      icon: <AlertTriangle className="w-4 h-4 text-accent-amber flex-shrink-0" />,
    },
    success: {
      bg: 'bg-accent-emerald/10 border-accent-emerald/30 text-accent-emerald',
      icon: <CheckCircle2 className="w-4 h-4 text-accent-emerald flex-shrink-0" />,
    },
    info: {
      bg: 'bg-accent-blue/10 border-accent-blue/30 text-accent-blue',
      icon: <Info className="w-4 h-4 text-accent-blue flex-shrink-0" />,
    },
  }[type] || styles.error;

  return (
    <div className={`border rounded-xl p-3.5 ${styles.bg} flex items-start space-x-3 text-xs`}>
      {styles.icon}
      <div className="flex-1 min-w-0">
        {title && <h4 className="font-semibold text-white text-xs mb-0.5">{title}</h4>}
        <p className="leading-relaxed text-slate-200">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-xs font-semibold text-white underline hover:opacity-80 transition-opacity"
          >
            Retry Connection
          </button>
        )}
      </div>
    </div>
  );
}

export default Alert;
