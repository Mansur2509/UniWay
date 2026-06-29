"use client";

import { useEffect, useState } from "react";

/**
 * Returns true once a loading state has been active longer than `delayMs`.
 * Used to surface a "the server may be waking up" hint during a Render cold
 * start, where the first request can legitimately take up to a minute, without
 * showing that hint for the common fast case.
 */
export function useSlowLoad(isLoading: boolean, delayMs = 5000): boolean {
  const [isSlow, setIsSlow] = useState(false);

  useEffect(() => {
    if (!isLoading) {
      setIsSlow(false);
      return;
    }
    const timer = setTimeout(() => setIsSlow(true), delayMs);
    return () => clearTimeout(timer);
  }, [isLoading, delayMs]);

  return isSlow;
}
