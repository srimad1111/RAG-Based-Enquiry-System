import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ label = 'Connecting to backend...', size = 18 }) {
  return (
    <div className="flex items-center justify-center space-x-2 py-6 text-slate-400">
      <Loader2 size={size} className="animate-spin text-violetAccent-light" />
      <span className="text-xs font-mono font-medium text-slate-300">{label}</span>
    </div>
  );
}

export default LoadingSpinner;
