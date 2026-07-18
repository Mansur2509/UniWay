"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Animates a numeric display value from its previous value up (or down) to
 * the target over a short duration -- used for stat numbers (fit scores,
 * percentages, counts) so a changed number draws the eye instead of just
 * snapping. Skips the animation entirely (returns the target immediately)
 * when the value hasn't changed, on first mount, or when the user prefers
 * reduced motion, so it never gates content on motion succeeding.
 */
export function useCountUp(target: number, durationMs = 600): number {
  const [display, setDisplay] = useState(target);
  const previousRef = useRef(target);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const from = previousRef.current;
    previousRef.current = target;
    if (from === target) return;
    if (typeof window === "undefined" || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setDisplay(target);
      return;
    }

    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / durationMs);
      const eased = 1 - (1 - progress) * (1 - progress);
      setDisplay(from + (target - from) * eased);
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(tick);
      } else {
        setDisplay(target);
      }
    };
    frameRef.current = requestAnimationFrame(tick);
    return () => {
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  return display;
}
