import axios from 'axios';

const ANALYTICS_API_URL = import.meta.env.VITE_ANALYTICS_API_URL || 'http://localhost:8003';
const BANKING_API_URL = import.meta.env.VITE_BANKING_API_URL || 'http://localhost:8002';
const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8001';

export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8002';

// Create base clients
const analyticsClient = axios.create({
  baseURL: ANALYTICS_API_URL,
  timeout: 10000,
});

const bankingClient = axios.create({
  baseURL: BANKING_API_URL,
  timeout: 10000,
});

const authClient = axios.create({
  baseURL: AUTH_API_URL,
  timeout: 10000,
});

// Generic error handler
const handleError = (error, fallback = null) => {
  console.error('API Error:', error.message);
  if (error.response) {
    console.error('Response data:', error.response.data);
  }
  return fallback;
};

export const api = {
  // Analytics Endpoints
  getAnalyticsSummary: async () => {
    try {
      const response = await analyticsClient.get('/v1/analytics/summary');
      return response.data?.data?.attributes || response.data;
    } catch (error) {
      return handleError(error, {
        total_transactions: 0,
        total_volume: 0,
        avg_transaction_value: 0,
        high_risk_transactions: 0,
      });
    }
  },

  getFraudDistribution: async () => {
    try {
      const response = await analyticsClient.get('/v1/analytics/fraud-distribution');
      return response.data?.data?.attributes || response.data;
    } catch (error) {
      return handleError(error, { risk_distribution: {} });
    }
  },

  getSpendByCategory: async () => {
    try {
      const response = await analyticsClient.get('/v1/analytics/spend-by-category');
      return response.data?.data?.attributes || response.data;
    } catch (error) {
      return handleError(error, { categories: {} });
    }
  },

  // Service Health Endpoints
  getServiceHealth: async (service) => {
    try {
      let client;
      switch (service) {
        case 'auth': client = authClient; break;
        case 'banking': client = bankingClient; break;
        case 'analytics': client = analyticsClient; break;
        default: return { status: 'unknown' };
      }
      
      const start = performance.now();
      const response = await client.get('/health');
      const end = performance.now();
      
      return {
        ...response.data,
        latencyMs: Math.round(end - start),
      };
    } catch (error) {
      return { status: 'down', error: error.message, latencyMs: 0 };
    }
  },
};
