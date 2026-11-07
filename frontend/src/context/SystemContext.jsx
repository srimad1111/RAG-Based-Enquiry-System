import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import healthService from '../services/healthService';

const SystemContext = createContext(null);

export const SystemProvider = ({ children }) => {
  const [health, setHealth] = useState(null);
  const [systemInfo, setSystemInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedVersion, setSelectedVersion] = useState('v3.0');
  const [lastChecked, setLastChecked] = useState(null);

  const fetchSystemData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthData, infoData] = await Promise.all([
        healthService.getHealth(),
        healthService.getSystemInfo(),
      ]);
      setHealth(healthData);
      setSystemInfo(infoData);
      if (infoData?.default_product_version) {
        setSelectedVersion((prev) => prev || infoData.default_product_version);
      }
      setLastChecked(new Date());
    } catch (err) {
      console.error('Failed to communicate with FastAPI backend:', err);
      setError(err.message || 'Could not connect to FastAPI server at http://127.0.0.1:8000');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSystemData();
  }, [fetchSystemData]);

  const value = {
    health,
    systemInfo,
    loading,
    error,
    selectedVersion,
    setSelectedVersion,
    lastChecked,
    refreshHealth: fetchSystemData,
  };

  return <SystemContext.Provider value={value}>{children}</SystemContext.Provider>;
};

export const useSystem = () => {
  const context = useContext(SystemContext);
  if (!context) {
    throw new Error('useSystem must be used within a SystemProvider');
  }
  return context;
};

