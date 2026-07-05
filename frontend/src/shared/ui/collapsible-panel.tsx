"use client";

import { ChevronDown } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/shared/lib/cn";

import { Card } from "./card";

type CollapsiblePanelProps = {
  isOpen: boolean;
  onToggle: () => void;
  header: ReactNode;
  toggleLabel: string;
  children: ReactNode;
  className?: string;
};

/** Generic collapsible card: unlike CollapsibleFilterPanel (which owns its
 * own open/closed state and localStorage key internally), this is a
 * controlled component -- the caller owns isOpen/onToggle so it can force
 * the panel open in response to an action (e.g. a fresh successful result)
 * without fighting the panel's own state. */
export function CollapsiblePanel({
  isOpen,
  onToggle,
  header,
  toggleLabel,
  children,
  className
}: CollapsiblePanelProps) {
  return (
    <Card className={cn("p-4", className)}>
      <button
        aria-expanded={isOpen}
        className="flex w-full flex-wrap items-center justify-between gap-3 text-left"
        onClick={onToggle}
        type="button"
      >
        <span className="flex flex-wrap items-center gap-2 text-sm font-semibold">
          {toggleLabel}
          <ChevronDown
            aria-hidden
            className={cn("size-3.5 transition-transform", isOpen ? "rotate-180" : "")}
          />
        </span>
        <span className="text-xs font-medium text-muted-foreground">{header}</span>
      </button>
      {isOpen ? <div className="mt-4 border-t pt-4">{children}</div> : null}
    </Card>
  );
}
