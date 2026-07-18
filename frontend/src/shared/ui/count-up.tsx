"use client";

import { useInView } from "motion/react";
import { useEffect, useRef, useState } from "react";

import { useCountUp } from "@/shared/lib/use-count-up";

type CountUpProps = {
  target: number;
  durationMs?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
};

/**
 * Displays a truthful, already-known number, with a purely decorative 0 ->
 * target count-up the first time it scrolls into view. The initial/SSR
 * value is always `target` itself -- never 0 -- so no-JS clients, crawlers,
 * and the pre-hydration paint always show the correct number; the animation
 * is layered on top afterwards, not a precondition for correctness. Wraps
 * the existing useCountUp hook (which only animates when its target
 * argument changes) rather than duplicating its easing/reduced-motion logic.
 */
export function CountUp({ target, durationMs = 900, prefix = "", suffix = "", className }: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px 0px" });
  const [activeTarget, setActiveTarget] = useState(target);
  const hasRevealedRef = useRef(false);

  useEffect(() => {
    if (!isInView || hasRevealedRef.current) return;
    hasRevealedRef.current = true;
    // Dip to 0 only once, right before the reveal-triggered count-up --
    // this happens after hydration, as a deliberate animation moment, never
    // as the page's first-paint content.
    setActiveTarget(0);
    const timer = setTimeout(() => setActiveTarget(target), 16);
    return () => clearTimeout(timer);
  }, [isInView, target]);

  const display = useCountUp(activeTarget, durationMs);

  return (
    <span className={className} ref={ref}>
      {prefix}
      {Math.round(display)}
      {suffix}
    </span>
  );
}
