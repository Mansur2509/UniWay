"use client";

import { m, useInView } from "motion/react";
import { type ReactNode, useEffect, useRef, useState } from "react";

import { MOTION_DURATION, MOTION_EASE_OUT } from "@/shared/lib/motion-tokens";

import { usePrefersReducedMotion } from "./use-reduced-motion";

type MotionRevealProps = {
  children: ReactNode;
  className?: string;
  delayMs?: number;
  direction?: "up" | "none";
  once?: boolean;
};

// Safety net matching the existing shared/ui/reveal.tsx's own guarantee:
// content must never stay invisible just because a viewport observer never
// reported the element as visible (missing IntersectionObserver support,
// an unusual host environment, etc.) -- if that hasn't happened within this
// window, force the reveal anyway.
const FORCE_VISIBLE_AFTER_MS = 1500;

/**
 * Marketing-page scroll reveal built on motion/react's useInView. Kept
 * separate from the existing shared/ui/reveal.tsx (which 9 authenticated
 * screens already depend on for its exact current behavior) since this one
 * needs larger travel distance and composes with StaggerGroup.
 */
export function MotionReveal({
  children,
  className,
  delayMs = 0,
  direction = "up",
  once = true
}: MotionRevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once, margin: "-60px 0px" });
  const prefersReducedMotion = usePrefersReducedMotion();
  const [forceVisible, setForceVisible] = useState(false);

  useEffect(() => {
    if (isInView) return;
    const timer = setTimeout(() => setForceVisible(true), FORCE_VISIBLE_AFTER_MS);
    return () => clearTimeout(timer);
  }, [isInView]);

  if (prefersReducedMotion) {
    return <div className={className}>{children}</div>;
  }

  const travel = direction === "up" ? 16 : 0;
  const visible = isInView || forceVisible;

  return (
    <m.div
      animate={visible ? "visible" : "hidden"}
      className={className}
      initial="hidden"
      ref={ref}
      variants={{
        hidden: { opacity: 0, y: travel },
        visible: {
          opacity: 1,
          y: 0,
          transition: {
            duration: MOTION_DURATION.slow,
            delay: delayMs / 1000,
            ease: MOTION_EASE_OUT
          }
        }
      }}
    >
      {children}
    </m.div>
  );
}
