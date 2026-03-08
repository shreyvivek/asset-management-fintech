import { useState, useCallback } from 'react';

const API = '/api';

export interface SimulateResult {
  event: { id?: string; title?: string };
  riskChain: { order: number; implication: string; assetClass: string }[];
  agents: { id: string; name: string; analysis: string }[];
  debater: string | null;
  consensus: { direction?: string; conviction?: number };
}

export function useSimulate() {
  const [result, setResult] = useState<SimulateResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (eventId?: string, event?: { title: string; body?: string; type?: string }, profile?: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          eventId: eventId || undefined,
          event: eventId ? undefined : event,
          portfolioProfile: profile || 'global_macro',
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Simulation failed');
      setResult(data);
      return data;
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Simulation failed';
      setError(msg);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, run };
}
