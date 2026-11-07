import { useState, useEffect, useCallback } from 'react';
import documentService from '../services/documentService';

export function useDocuments() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOverview = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await documentService.getOverview();
      setOverview(data);
    } catch (err) {
      console.error('Error fetching document overview:', err);
      setError(err.message || 'Failed to load documents catalog');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchOverview();
  }, [fetchOverview]);

  return { overview, loading, error, refreshDocuments: fetchOverview };
}

export default useDocuments;

