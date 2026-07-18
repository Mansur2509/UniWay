"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useI18n } from "@/shared/i18n";
import { cn } from "@/shared/lib/cn";
import type { NavigationItem } from "@/shared/types/navigation";
import { AppIcon } from "@/shared/ui/icon";

export function NavLink({
  item,
  compact = false,
  compactHorizontal = false,
  inverse = false
}: {
  item: NavigationItem;
  compact?: boolean;
  compactHorizontal?: boolean;
  inverse?: boolean;
}) {
  const pathname = usePathname();
  const { t } = useI18n();
  const active =
    pathname === item.href ||
    (item.href !== "/dashboard" && pathname.startsWith(`${item.href}/`));
  const Icon = item.icon;

  return (
    <Link
      aria-current={active ? "page" : undefined}
      className={cn(
        "relative flex items-center gap-3 rounded-sm text-sm font-medium transition-colors",
        compact
          ? "min-w-16 flex-col px-2 py-2 text-[0.68rem]"
          : compactHorizontal
            ? "shrink-0 px-3 py-2 text-xs"
            : "px-3 py-2",
        active
          ? "bg-primary-button text-primary-foreground"
          : inverse
            ? "text-white/70 hover:bg-white/10 hover:text-white"
            : "text-muted-foreground hover:bg-muted hover:text-foreground"
      )}
      href={item.href}
    >
      {/* Animated active-route indicator: a leading accent bar that scales in
          from the center rather than the whole row just swapping background
          color instantly -- gives the active state a sense of motion without
          measuring/animating between two different rows' positions. */}
      {!compact && !compactHorizontal ? (
        <span
          aria-hidden
          className={cn(
            "absolute inset-y-1 left-0 w-[3px] rounded-full bg-accent transition-transform duration-normal ease-academic",
            active ? "scale-y-100" : "scale-y-0"
          )}
        />
      ) : null}
      <AppIcon icon={Icon} />
      <span>{t(item.labelKey)}</span>
    </Link>
  );
}
