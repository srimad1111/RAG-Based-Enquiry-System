import React from 'react';
import { HealthCard } from '../components/dashboard/HealthCard';
import { ComponentStatusGrid } from '../components/dashboard/ComponentStatusGrid';
import { SystemInfoCard } from '../components/dashboard/SystemInfoCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Alert } from '../components/common/Alert';
import { useSystem } from '../context/SystemContext';

export function DashboardPage() {
  const { health, systemInfo, loading, error, refreshHealth } = useSystem();

  if (loading && !health) {
    return <LoadingSpinner label="Testing FastAPI connection and loading diagnostics..." />;
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert
          type="error"
          title="Backend Connection Offline"
          message={`FastAPI server is not reachable: ${error}. Ensure backend is running via: uvicorn app.main:app --reload`}
          onRetry={refreshHealth}
        />
      )}

      {/* Top summary row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <HealthCard health={health} loading={loading} onRefresh={refreshHealth} />
        </div>
        <div>
          <SystemInfoCard systemInfo={systemInfo} />
        </div>
      </div>

      {/* Subsystem diagnostics */}
      {health?.components && (
        <ComponentStatusGrid components={health.components} />
      )}
    </div>
  );
}

export default DashboardPage;

