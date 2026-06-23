import type { LucideIcon } from "lucide-react";

import type { TranslationKey } from "@/shared/i18n";

export type NavigationItem = {
  href: string;
  labelKey: TranslationKey;
  icon: LucideIcon;
};
