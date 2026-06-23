import type { HTMLAttributes } from "react";

import { cn } from "@/shared/lib/cn";

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm border border-primary/25 bg-primary/10 px-2.5 py-1 text-[0.68rem] font-bold uppercase tracking-[0.08em] text-primary-hover",
        className
      )}
      {...props}
    />
  );
}
