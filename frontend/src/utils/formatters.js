/**
 * Utility formatters for timestamps and status indicators.
 */

export function formatDateTime(isoString) {
  if (!isoString) return 'N/A';
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' ' + date.toLocaleDateString();
  } catch {
    return isoString;
  }
}

export function getStatusColor(status) {
  switch (status?.toLowerCase()) {
    case 'healthy':
    case 'operational':
    case 'ready':
      return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    case 'degraded':
    case 'standby':
      return 'bg-amber-100 text-amber-800 border-amber-300';
    case 'error':
    case 'down':
      return 'bg-rose-100 text-rose-800 border-rose-300';
    default:
      return 'bg-slate-100 text-slate-800 border-slate-300';
  }
}

export function getStatusDotColor(status) {
  switch (status?.toLowerCase()) {
    case 'healthy':
    case 'operational':
    case 'ready':
      return 'bg-emerald-500';
    case 'degraded':
    case 'standby':
      return 'bg-amber-500';
    case 'error':
    case 'down':
      return 'bg-rose-500';
    default:
      return 'bg-slate-400';
  }
}

