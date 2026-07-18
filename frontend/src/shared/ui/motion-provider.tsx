"use client";

import { domAnimation, LazyMotion } from "motion/react";
import type { ReactNode } from "react";

/**
 * Loads only the "domAnimation" Motion feature set (animations, exit
 * animations via AnimatePresence, hover/tap gestures) instead of every
 * `motion.*` component's full default bundle, which also includes drag and
 * layout-projection code nothing in this app uses. Every primitive that
 * renders an `m.*` component (not `motion.*`) must live under this
 * provider -- it's mounted once at the root layout.
 */
export function MotionProvider({ children }: { children: ReactNode }) {
  return <LazyMotion features={domAnimation}>{children}</LazyMotion>;
}
