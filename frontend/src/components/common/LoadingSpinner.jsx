import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ label = 'Connecting to backend...', size = 20 }) {
  return (
    <div className="flex items-center justify-center space-x-2 py-6 text-slate-500">
      <Loader2 size={size} className="animate-spin text-indigo-600" />
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}

export default LoadingSpinner;

