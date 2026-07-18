"use client";

import { useI18n } from "@/shared/i18n";
import { useCountUp } from "@/shared/lib/use-count-up";

export function StatValue({
  value,
  suffix
}: {
  value: string | number | boolean | null;
  suffix?: string;
}) {
  const { t } = useI18n();
  const numeric = typeof value === "number" && Number.isFinite(value) ? value : 0;
  // Always called (rules-of-hooks) -- animated only for finite-number values;
  // the string/null/boolean branches below simply never read `animated`.
  const animated = useCountUp(numeric);

  if (value === null || value === undefined || value === "") {
    return (
      <span className="italic text-muted-foreground">{t("universities.notVerifiedYet")}</span>
    );
  }
  if (typeof value === "boolean") {
    return <span>{value ? t("common.yes") : t("common.no")}</span>;
  }
  if (typeof value === "number") {
    const rounded = Number.isInteger(value) ? Math.round(animated) : Math.round(animated * 10) / 10;
    return (
      <span>
        {rounded}
        {suffix ?? ""}
      </span>
    );
  }
  return (
    <span>
      {value}
      {suffix ?? ""}
    </span>
  );
}
