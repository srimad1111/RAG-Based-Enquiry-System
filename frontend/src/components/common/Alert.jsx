import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

export function Alert({ type = 'error', title, message, onRetry }) {
  const styles = {
    error: {
      bg: 'bg-roseAccent/10 border-roseAccent/30 text-roseAccent-light',
      icon: <AlertCircle className="w-5 h-5 text-roseAccent flex-shrink-0" />,
    },
    warning: {
      bg: 'bg-amberAccent/10 border-amberAccent/30 text-amberAccent-light',
      icon: <AlertTriangle className="w-5 h-5 text-amberAccent flex-shrink-0" />,
    },
    success: {
      bg: 'bg-emeraldAccent/10 border-emeraldAccent/30 text-emeraldAccent-light',
      icon: <CheckCircle2 className="w-5 h-5 text-emeraldAccent flex-shrink-0" />,
    },
    info: {
      bg: 'bg-violetAccent/10 border-violetAccent/30 text-violetAccent-light',
      icon: <Info className="w-5 h-5 text-violetAccent flex-shrink-0" />,
    },
  }[type] || styles.error;

  return (
    <div className={`border rounded-xl p-4 ${styles.bg} flex items-start space-x-3 text-xs`}>
      {styles.icon}
      <div className="flex-1 min-w-0">
        {title && <h4 className="font-bold text-white text-xs mb-0.5">{title}</h4>}
        <p className="leading-relaxed">{message}</p>
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
