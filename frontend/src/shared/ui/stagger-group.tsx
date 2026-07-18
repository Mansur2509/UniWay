import { Children, type ReactNode } from "react";

import { MotionReveal } from "./motion-reveal";

type StaggerGroupProps = {
  children: ReactNode;
  className?: string;
  staggerMs?: number;
};

/**
 * Wraps each direct child in its own MotionReveal with a computed per-index
 * delay -- the same "wrap each item with an increasing delayMs" idiom
 * already used throughout the app (e.g. PaginatedGrid's Reveal-per-card),
 * rather than relying on motion/react's variant-propagation-to-children,
 * which is harder to reason about for arbitrary caller-supplied children.
 */
export function StaggerGroup({ children, className, staggerMs = 60 }: StaggerGroupProps) {
  const items = Children.toArray(children);

  return (
    <div className={className}>
      {items.map((child, index) => (
        <MotionReveal delayMs={index * staggerMs} key={index}>
          {child}
        </MotionReveal>
      ))}
    </div>
  );
}
