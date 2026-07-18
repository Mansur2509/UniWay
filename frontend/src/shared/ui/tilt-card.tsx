"use client";

import { m, useSpring } from "motion/react";
import { type PointerEvent, type ReactNode, useEffect, useState } from "react";

import { usePrefersReducedMotion } from "./use-reduced-motion";

type TiltCardProps = {
  children: ReactNode;
  className?: string;
  maxTiltDeg?: number;
};

/**
 * Subtle pointer-tracking 3D tilt for decorative hero/showcase cards only --
 * never forms, tables, or dense workflow cards (per product rule). Disabled
 * under reduced motion and on touch/coarse-pointer devices.
 */
export function TiltCard({ children, className, maxTiltDeg = 5 }: TiltCardProps) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const [canHover, setCanHover] = useState(false);
  const rotateX = useSpring(0, { stiffness: 220, damping: 22 });
  const rotateY = useSpring(0, { stiffness: 220, damping: 22 });

  useEffect(() => {
    setCanHover(window.matchMedia("(hover: hover) and (pointer: fine)").matches);
  }, []);

  if (prefersReducedMotion || !canHover) {
    return <div className={className}>{children}</div>;
  }

  function handlePointerMove(event: PointerEvent<HTMLDivElement>) {
    const bounds = event.currentTarget.getBoundingClientRect();
    const offsetX = (event.clientX - bounds.left) / bounds.width - 0.5;
    const offsetY = (event.clientY - bounds.top) / bounds.height - 0.5;
    rotateY.set(offsetX * maxTiltDeg * 2);
    rotateX.set(offsetY * -maxTiltDeg * 2);
  }

  function handlePointerLeave() {
    rotateX.set(0);
    rotateY.set(0);
  }

  return (
    <m.div
      className={className}
      onPointerLeave={handlePointerLeave}
      onPointerMove={handlePointerMove}
      style={{ rotateX, rotateY, transformPerspective: 800 }}
    >
      {children}
    </m.div>
  );
}
