import { useState, useEffect, useCallback } from 'react';

const API = '/api';

export interface FeedEvent {
  id: string;
  type?: string;
  source?: string;
  title?: string;
  body?: string;
  timestamp?: string;
  themeId?: string;
  verified?: boolean;
}

export function useFeed() {
  const [feed, setFeed] = useState<FeedEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchFeed = useCallback(async () => {
    try {
      const res = await fetch(`${API}/feed?limit=30`);
      const data = await res.json();
      setFeed(data.feed || []);
    } catch (_) {
      setFeed([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  return { feed, loading, refetch: fetchFeed };
}
