"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

type RevealProps = {
  children: ReactNode;
  className?: string;
  delayMs?: number;
};

/**
 * Scroll-triggered entrance: content starts slightly lower and transparent,
 * then settles into place the first time it enters the viewport. Uses a
 * plain IntersectionObserver rather than a library -- one observer per
 * instance, disconnected after the first reveal since content never needs to
 * hide again. Renders fully visible immediately if IntersectionObserver isn't
 * available (very old browsers) or the user prefers reduced motion, so
 * content is never gated behind JS/motion succeeding.
 */
export function Reveal({ children, className, delayMs = 0 }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setVisible(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      className={className}
      ref={ref}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(12px)",
        transition: `opacity var(--motion-slow) var(--motion-ease-out), transform var(--motion-slow) var(--motion-ease-out)`,
        transitionDelay: visible ? `${delayMs}ms` : "0ms"
      }}
    >
      {children}
    </div>
  );
}
