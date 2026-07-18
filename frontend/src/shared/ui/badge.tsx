import type { HTMLAttributes } from "react";

import { cn } from "@/shared/lib/cn";

export type BadgeTone =
  | "primary"
  | "success"
  | "warning"
  | "danger"
  | "info"
  | "accent"
  | "event"
  | "recommendation"
  | "scholarship"
  | "muted";

type BadgeProps = HTMLAttributes<HTMLSpanElement> & {
  tone?: BadgeTone;
};

// Single source of truth for the tone-chip look used across status/category/
// verification labels -- before this, each screen hand-rolled its own
// border/bg/text triad per tone (dashboard workflow steps, organizer
// moderation status, event category, university verification). Keeping the
// tone set fixed (not computed) so colors stay stable across the app.
const BADGE_TONE_CLASSES: Record<BadgeTone, string> = {
  primary: "border-primary/25 bg-primary/10 text-primary-hover",
  success: "border-success/35 bg-success/10 text-success",
  warning: "border-warning/35 bg-warning/10 text-warning",
  danger: "border-danger/35 bg-danger/10 text-danger",
  info: "border-info/35 bg-info/10 text-info",
  accent: "border-accent/35 bg-accent/10 text-accent",
  event: "border-event/35 bg-event/10 text-event",
  recommendation: "border-recommendation/30 bg-recommendation/10 text-recommendation",
  scholarship: "border-scholarship/40 bg-scholarship/15 text-scholarship",
  muted: "border-muted-foreground/25 bg-surface text-muted-foreground"
};

export function Badge({ className, tone = "primary", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm border px-2.5 py-1 text-[0.68rem] font-bold uppercase tracking-[0.08em]",
        BADGE_TONE_CLASSES[tone],
        className
      )}
      {...props}
    />
  );
}
