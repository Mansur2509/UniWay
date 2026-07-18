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
    if (isInView) setActiveTarget(target);
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
