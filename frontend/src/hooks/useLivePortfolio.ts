import { useState, useEffect, useCallback } from 'react';

const API_BASE = '/api';

export interface Allocation {
  [asset: string]: number;
}

export interface Metrics {
  reward: number;
  rewardDelta: number;
  risk: number;
  riskDelta: number;
  sharpe: number;
  sharpeDelta: number;
}

export interface ReallocationRow {
  assetClass: string;
  saa: number;
  taa: number;
  reasoning: string;
}

export function useLivePortfolio() {
  const [current, setCurrent] = useState<Allocation>({});
  const [recommended, setRecommended] = useState<Allocation>({});
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [table, setTable] = useState<ReallocationRow[]>([]);
  const [colors, setColors] = useState<Record<string, string>>({});
  const [wsConnected, setWsConnected] = useState(false);

  const fetchInitial = useCallback(async () => {
    try {
      const [currentRes, recRes, tableRes, metricsRes] = await Promise.all([
        fetch(`${API_BASE}/portfolio/current`),
        fetch(`${API_BASE}/portfolio/recommended`),
        fetch(`${API_BASE}/portfolio/reallocation-table`),
        fetch(`${API_BASE}/portfolio/metrics`),
      ]);
      const currentData = await currentRes.json();
      const recData = await recRes.json();
      setCurrent(currentData.allocation || {});
      setRecommended(recData.allocation || {});
      setColors(recData.colors || currentData.colors || {});
      setTable((await tableRes.json()).rows || []);
      setMetrics(await metricsRes.json());
    } catch (e) {
      console.error('Initial fetch failed', e);
    }
  }, []);

  useEffect(() => {
    fetchInitial();
  }, [fetchInitial]);

  useEffect(() => {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${proto}//${host}/ws`;
    let ws: WebSocket | null = null;
    let fallback: ReturnType<typeof setInterval> | null = null;

    const connect = () => {
      try {
        ws = new WebSocket(wsUrl);
        ws.onopen = () => setWsConnected(true);
        ws.onclose = () => {
          setWsConnected(false);
          fallback = setInterval(pollLive, 4000);
        };
        ws.onmessage = (ev) => {
          try {
            const data = JSON.parse(ev.data as string);
            if (data.type === 'live_update') {
              if (data.metrics) setMetrics(data.metrics);
              if (data.recommended) setRecommended(data.recommended);
            }
          } catch (_) {}
        };
      } catch (_) {
        fallback = setInterval(pollLive, 4000);
      }
    };

    async function pollLive() {
      try {
        const [recRes, metricsRes] = await Promise.all([
          fetch(`${API_BASE}/portfolio/recommended/live`),
          fetch(`${API_BASE}/portfolio/metrics`),
        ]);
        const recData = await recRes.json();
        setRecommended(recData.allocation || recommended);
        setMetrics(await metricsRes.json());
      } catch (_) {}
    }

    connect();
    return () => {
      if (ws) ws.close();
      if (fallback) clearInterval(fallback);
    };
  }, []);

  return {
    current,
    recommended,
    metrics,
    table,
    colors,
    wsConnected,
    refetch: fetchInitial,
  };
}
