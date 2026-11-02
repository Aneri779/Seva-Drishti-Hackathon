// src/hooks/useApi.js
import { useEffect, useState, useCallback } from 'react';

export function useApi(fn, deps = [], pollIntervalMs = null) {
  const [state, setState] = useState({ data: null, loading: true, error: null });

  const fetcher = useCallback(() => {
    let live = true;
    
    fn()
      .then(d => {
        if (live) setState({ data: d, loading: false, error: null });
      })
      .catch(e => {
        if (live) setState(prev => ({ ...prev, loading: false, error: e.message }));
      });

    return () => {
      live = false;
    };
  }, deps);

  useEffect(() => {
    const cancel = fetcher();
    
    let timer = null;
    if (pollIntervalMs && pollIntervalMs > 0) {
      timer = setInterval(() => {
        fetcher();
      }, pollIntervalMs);
    }
    
    return () => {
      cancel();
      if (timer) clearInterval(timer);
    };
  }, [fetcher, pollIntervalMs]);

  return { ...state, refetch: fetcher };
}

