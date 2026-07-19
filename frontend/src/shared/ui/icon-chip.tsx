import type { LucideIcon } from "lucide-react";

import { cn } from "@/shared/lib/cn";

import type { BadgeTone } from "./badge";
import { AppIcon, type IconSize } from "./icon";

const CHIP_TONE_CLASSES: Record<BadgeTone, string> = {
  primary: "border-primary/25 bg-primary/10 text-primary-hover",
  success: "border-success/30 bg-success/10 text-success",
  warning: "border-warning/30 bg-warning/10 text-warning",
  danger: "border-danger/35 bg-danger/10 text-danger",
  info: "border-info/30 bg-info/10 text-info",
  accent: "border-accent/35 bg-accent/10 text-accent",
  event: "border-event/30 bg-event/10 text-event",
  recommendation: "border-recommendation/30 bg-recommendation/10 text-recommendation",
  scholarship: "border-scholarship/35 bg-scholarship/10 text-scholarship",
  muted: "border-muted-foreground/25 bg-surface text-muted-foreground"
};

const CHIP_SIZE_CLASSES: Record<"sm" | "md" | "lg", string> = {
  sm: "size-7",
  md: "size-9",
  lg: "size-11"
};

const CHIP_ICON_SIZE: Record<"sm" | "md" | "lg", IconSize> = {
  sm: "xs",
  md: "sm",
  lg: "md"
};

type IconChipProps = {
  icon: LucideIcon;
  tone?: BadgeTone;
  size?: "sm" | "md" | "lg";
  className?: string;
};

// Single source of truth for the "colored rounded box around an icon" motif
// used throughout the app (dashboard core tools, organizer status tiles,
// profile section headers, destination card stats, ...). Before this, each
// screen hand-rolled its own copy of `grid size-N place-items-center
// rounded-sm border {tone classes}`.
export function IconChip({ icon, tone = "primary", size = "md", className }: IconChipProps) {
  return (
    <span
      className={cn(
        "grid shrink-0 place-items-center rounded-sm border",
        CHIP_SIZE_CLASSES[size],
        CHIP_TONE_CLASSES[tone],
        className
      )}
    >
      <AppIcon icon={icon} size={CHIP_ICON_SIZE[size]} />
    </span>
  );
}
