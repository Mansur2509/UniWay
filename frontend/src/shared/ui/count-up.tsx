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

// A stat number stuck at 0 forever reads as a false/broken claim, which is
// worse than an invisible element -- if the viewport observer hasn't
// reported this element as visible within this window, count up anyway.
const FORCE_REVEAL_AFTER_MS = 1500;

/**
 * Animates a truthful, already-known number from 0 up to `target` the first
 * time it enters the viewport. Wraps the existing useCountUp hook (which
 * only animates when its target argument changes) rather than duplicating
 * its easing/reduced-motion logic.
 */
export function CountUp({ target, durationMs = 900, prefix = "", suffix = "", className }: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-80px 0px" });
  const [activeTarget, setActiveTarget] = useState(0);

  useEffect(() => {
    if (isInView) {
      setActiveTarget(target);
      return;
    }
    const timer = setTimeout(() => setActiveTarget(target), FORCE_REVEAL_AFTER_MS);
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
