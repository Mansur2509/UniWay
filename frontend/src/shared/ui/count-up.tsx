type CountUpProps = {
  target: number;
  prefix?: string;
  suffix?: string;
  className?: string;
};

/**
 * Displays a truthful stat number: SSR, no-JS, reduced-motion, and
 * fully-hydrated visitors all see the exact same static `target` text, with
 * no digit-counting animation and no reset-to-0-then-recount. Callers that
 * want a reveal effect wrap this in MotionReveal (see hero-section.tsx and
 * trust-section.tsx), which animates opacity/position only -- never the
 * number itself.
 */
export function CountUp({ target, prefix = "", suffix = "", className }: CountUpProps) {
  return (
    <span className={className}>
      {prefix}
      {target}
      {suffix}
    </span>
  );
}
