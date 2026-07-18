"use client";

import { useEffect, useState } from "react";

/**
 * Shared prefers-reduced-motion check for the new marketing/motion
 * primitives. The existing Reveal component and useCountUp hook keep their
 * own inline matchMedia checks -- this is the single source of truth for
 * everything built on top of them going forward.
 */
export function usePrefersReducedMotion(): boolean {
  const [prefersReduced, setPrefersReduced] = useState(false);

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReduced(query.matches);

    function handleChange(event: MediaQueryListEvent) {
      setPrefersReduced(event.matches);
    }

    query.addEventListener("change", handleChange);
    return () => query.removeEventListener("change", handleChange);
  }, []);

  return prefersReduced;
}
