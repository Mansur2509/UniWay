import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/shared/lib/cn";

import { Card } from "./card";

type EmptyStateProps = {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
};

/**
 * Shared empty-state surface for "no data yet" / "no results" moments
 * (empty saved list, no applications, no search matches, ...). Callers pass
 * their own translated copy and an optional action -- this owns only the
 * visual shape, so one consistent treatment replaces the previously ad hoc,
 * per-screen empty blocks.
 */
export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <Card className={cn("flex flex-col items-center gap-3 py-10 text-center", className)}>
      {Icon ? (
        <span className="grid size-11 shrink-0 place-items-center rounded-full border border-border bg-muted text-muted-foreground">
          <Icon aria-hidden className="size-5" strokeWidth={1.75} />
        </span>
      ) : null}
      <div className="space-y-1">
        <h2 className="text-sm font-semibold">{title}</h2>
        {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
      </div>
      {action}
    </Card>
  );
}
