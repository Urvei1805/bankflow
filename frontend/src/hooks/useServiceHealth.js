import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

export const useServiceHealth = () => {
  const [health, setHealth] = useState({
    auth: { status: 'loading' },
    banking: { status: 'loading' },
    analytics: { status: 'loading' },
  });
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const fetchHealth = useCallback(async () => {
    setLoading(true);
    try {
      const [auth, banking, analytics] = await Promise.all([
        api.getServiceHealth('auth'),
        api.getServiceHealth('banking'),
        api.getServiceHealth('analytics'),
      ]);

      setHealth({ auth, banking, analytics });
      setLastRefreshed(new Date().toISOString());
    } catch (err) {
      console.error('Error fetching service health:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    // Refresh every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  return { health, loading, lastRefreshed, refetch: fetchHealth };
};
