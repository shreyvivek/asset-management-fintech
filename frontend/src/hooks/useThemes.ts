import { useState, useEffect, useCallback } from 'react';

const API = '/api';

export interface Theme {
  id: string;
  name: string;
  region?: string;
  heat: number;
  trajectory: 'heating' | 'cooling' | 'stable';
  eventCount?: number;
}

export function useThemes(profile = 'global_macro') {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchThemes = useCallback(async () => {
    try {
      const res = await fetch(`${API}/macro/themes?profile=${profile}`);
      const data = await res.json();
      setThemes(data.themes || []);
    } catch (_) {
      setThemes([]);
    } finally {
      setLoading(false);
    }
  }, [profile]);

  useEffect(() => {
    fetchThemes();
  }, [fetchThemes]);

  return { themes, loading, refetch: fetchThemes };
}
