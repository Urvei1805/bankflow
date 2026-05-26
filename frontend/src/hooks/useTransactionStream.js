import { useState, useEffect, useCallback, useRef } from 'react';
import { WS_URL } from '../api/client';

const MAX_TRANSACTIONS = 100;

export const useTransactionStream = () => {
  const [transactions, setTransactions] = useState([]);
  const [status, setStatus] = useState('disconnected'); // 'disconnected', 'connecting', 'connected', 'error'
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  
  // Base reconnect delay in ms
  const baseReconnectDelay = 2000;
  const maxReconnectDelay = 30000;
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      return;
    }

    setStatus('connecting');
    setError(null);
    
    try {
      const ws = new WebSocket(`${WS_URL}/ws/transactions`);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data);
          const data = {
            id: raw.transaction_id || raw.id,
            amount: raw.amount,
            merchant: raw.merchant_name || raw.merchant,
            category: raw.merchant_category || raw.category,
            risk_level: raw.fraud_risk_level || raw.risk_level,
            risk_score: raw.fraud_score || raw.risk_score,
            timestamp: raw.timestamp,
            type: (raw.transaction_type || raw.type || '').toUpperCase(),
          };
          setTransactions(prev => {
            // Unshift new data and limit to MAX_TRANSACTIONS
            const updated = [data, ...prev];
            return updated.length > MAX_TRANSACTIONS ? updated.slice(0, MAX_TRANSACTIONS) : updated;
          });
        } catch (err) {
          console.error('Failed to parse WebSocket message', err);
        }
      };

      ws.onclose = () => {
        setStatus('disconnected');
        scheduleReconnect();
      };

      ws.onerror = (err) => {
        setStatus('error');
        setError('WebSocket error occurred');
        ws.close();
      };
    } catch (err) {
      setStatus('error');
      setError(err.message);
      scheduleReconnect();
    }
  }, []);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    // Exponential backoff
    const delay = Math.min(
      baseReconnectDelay * Math.pow(1.5, reconnectAttempts.current),
      maxReconnectDelay
    );
    
    reconnectAttempts.current += 1;
    reconnectTimeoutRef.current = setTimeout(connect, delay);
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  // Provide a fallback function to load mock data if WS is persistently down
  const loadMockData = useCallback(() => {
    const mockTx = {
      id: `mock-${Date.now()}`,
      amount: (Math.random() * 500).toFixed(2),
      merchant: ['Amazon', 'Uber', 'Starbucks', 'Netflix', 'Apple'][Math.floor(Math.random() * 5)],
      category: ['Shopping', 'Transport', 'Food', 'Entertainment', 'Technology'][Math.floor(Math.random() * 5)],
      risk_level: Math.random() > 0.8 ? 'HIGH' : Math.random() > 0.5 ? 'MEDIUM' : 'LOW',
      risk_score: (Math.random() * 100).toFixed(1),
      timestamp: new Date().toISOString(),
      type: Math.random() > 0.8 ? 'CREDIT' : 'DEBIT',
    };
    
    setTransactions(prev => [mockTx, ...prev].slice(0, MAX_TRANSACTIONS));
  }, []);

  return { transactions, status, error, loadMockData };
};
