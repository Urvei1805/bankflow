import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';

export const useAnalytics = () => {
  const [data, setData] = useState({
    summary: null,
    fraudDistribution: null,
    spendByCategory: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [summary, fraud, spend] = await Promise.all([
        api.getAnalyticsSummary(),
        api.getFraudDistribution(),
        api.getSpendByCategory(),
      ]);

      setData({
        summary: summary || {},
        fraudDistribution: fraud?.distribution || [],
        spendByCategory: spend?.categories || [],
      });
      setLastRefreshed(new Date().toISOString());
    } catch (err) {
      setError(err.message || 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  return { ...data, loading, error, lastRefreshed, refetch: fetchAnalytics };
};
