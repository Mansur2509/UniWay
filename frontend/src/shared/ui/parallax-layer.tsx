"use client";

import { motion, useSpring } from "motion/react";
import { type ReactNode, useEffect, useState } from "react";

import { usePrefersReducedMotion } from "./use-reduced-motion";

type ParallaxLayerProps = {
  children: ReactNode;
  className?: string;
  depth?: number;
  axis?: "x" | "y" | "both";
};

const MAX_OFFSET_PX = 18;

/**
 * Bounded, pointer-reactive decorative depth layer for hero/showcase
 * compositions -- never wraps text, forms, or nav. No-ops (renders children
 * in place) under reduced motion or on touch/coarse-pointer devices.
 */
export function ParallaxLayer({
  children,
  className,
  depth = 0.2,
  axis = "both"
}: ParallaxLayerProps) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const [canHover, setCanHover] = useState(false);
  const x = useSpring(0, { stiffness: 120, damping: 20 });
  const y = useSpring(0, { stiffness: 120, damping: 20 });

  useEffect(() => {
    setCanHover(window.matchMedia("(hover: hover) and (pointer: fine)").matches);
  }, []);

  useEffect(() => {
    if (prefersReducedMotion || !canHover) return;

    function handlePointerMove(event: PointerEvent) {
      const offsetX = (event.clientX / window.innerWidth - 0.5) * 2;
      const offsetY = (event.clientY / window.innerHeight - 0.5) * 2;
      if (axis === "x" || axis === "both") x.set(offsetX * MAX_OFFSET_PX * depth);
      if (axis === "y" || axis === "both") y.set(offsetY * MAX_OFFSET_PX * depth);
    }

    window.addEventListener("pointermove", handlePointerMove);
    return () => window.removeEventListener("pointermove", handlePointerMove);
  }, [axis, canHover, depth, prefersReducedMotion, x, y]);

  if (prefersReducedMotion || !canHover) {
    return <div className={className}>{children}</div>;
  }

  return (
    <motion.div className={className} style={{ x, y }}>
      {children}
    </motion.div>
  );
}
