import { useState, useEffect, useCallback } from 'react';

const API = '/api';

export interface HorizonItem {
  ticker: string;
  currentPrice: number;
  baseFairValue: number;
  macroAdjustedFairValue: number;
  deltaPct: number;
  narrative: string;
}

export function useHorizon() {
  const [view, setView] = useState<HorizonItem[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchWatchlist = useCallback(async () => {
    try {
      const res = await fetch(`${API}/horizon/watchlist`);
      const data = await res.json();
      setWatchlist(data.watchlist || []);
    } catch (_) {
      setWatchlist([]);
    }
  }, []);

  const fetchView = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/horizon/view`);
      const data = await res.json();
      setView(data.view || []);
    } catch (_) {
      setView([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWatchlist();
  }, [fetchWatchlist]);

  useEffect(() => {
    fetchView();
  }, [fetchView]);

  const addTicker = useCallback(async (ticker: string) => {
    const t = ticker.trim().toUpperCase();
    if (!t) return;
    const res = await fetch(`${API}/horizon/watchlist`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: t }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to add ticker');
    setWatchlist(data.watchlist ?? [...watchlist, t]);
    await fetchView();
  }, [watchlist, fetchView]);

  return { view, watchlist, loading, refetch: fetchView, addTicker };
}
