"use client";

import { motion, useInView } from "motion/react";
import { type ReactNode, useRef } from "react";

import { MOTION_DURATION, MOTION_EASE_OUT } from "@/shared/lib/motion-tokens";

import { usePrefersReducedMotion } from "./use-reduced-motion";

type MotionRevealProps = {
  children: ReactNode;
  className?: string;
  delayMs?: number;
  direction?: "up" | "none";
  once?: boolean;
};

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

  if (prefersReducedMotion) {
    return <div className={className}>{children}</div>;
  }

  const travel = direction === "up" ? 16 : 0;

  return (
    <motion.div
      animate={isInView ? "visible" : "hidden"}
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
    </motion.div>
  );
}
