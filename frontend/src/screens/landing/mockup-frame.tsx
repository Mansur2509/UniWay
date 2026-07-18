import type { ReactNode } from "react";

import { cn } from "@/shared/lib/cn";

type MockupFrameProps = {
  label: string;
  children: ReactNode;
  className?: string;
};

/**
 * Shared "browser chrome" bezel used to frame recreated real-UI fragments in
 * the hero and product showcase sections, so every mockup reads as one
 * consistent device rather than a loose card.
 */
export function MockupFrame({ label, children, className }: MockupFrameProps) {
  return (
    <div className={cn("overflow-hidden rounded-sm border bg-card shadow-card", className)}>
      <div className="flex items-center gap-1.5 border-b bg-elevated px-3 py-2">
        <span className="size-2 rounded-full bg-danger/50" />
        <span className="size-2 rounded-full bg-warning/50" />
        <span className="size-2 rounded-full bg-success/50" />
        <span className="ml-2 truncate text-[0.65rem] font-semibold uppercase tracking-[0.1em] text-muted-foreground">
          {label}
        </span>
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}
