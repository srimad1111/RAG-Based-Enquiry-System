import React from 'react';
import { getStatusColor } from '../../utils/formatters';

export function Badge({ text, status, className = '' }) {
  const colorClasses = status ? getStatusColor(status) : 'bg-slate-100 text-slate-700 border-slate-200';
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClasses} ${className}`}>
      {text || status}
    </span>
  );
}

export default Badge;

