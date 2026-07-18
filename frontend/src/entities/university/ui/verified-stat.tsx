"use client";

import { ExternalLink } from "lucide-react";

import type { UniversityFieldVerification, VerificationStatus } from "@/entities/university";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { Badge, type BadgeTone } from "@/shared/ui/badge";

import { StatValue } from "./stat-value";

const VERIFICATION_TONE: Record<VerificationStatus, BadgeTone> = {
  verified: "success",
  partial: "warning",
  estimated: "muted"
};

export function VerificationBadge({ status }: { status: VerificationStatus }) {
  const { t } = useI18n();
  return (
    <Badge className="px-1.5 py-0.5 text-[0.62rem]" tone={VERIFICATION_TONE[status]}>
      {t(`universities.verification.status.${status}` as TranslationKey)}
    </Badge>
  );
}

export function VerifiedStat({
  value,
  suffix,
  verification
}: {
  value: string | number | boolean | null;
  suffix?: string;
  verification?: UniversityFieldVerification;
}) {
  const { locale, t } = useI18n();
  const isMissing = value === null || value === undefined || value === "";

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <StatValue suffix={suffix} value={value} />
        {!isMissing && verification ? <VerificationBadge status={verification.status} /> : null}
      </div>
      {!isMissing && verification ? (
        <div className="mt-1 flex flex-wrap items-center gap-2 text-[0.65rem] text-muted-foreground">
          <span>
            {t("universities.verification.lastVerified", {
              date: formatDate(verification.last_verified_date, locale)
            })}
          </span>
          <a
            className="inline-flex items-center gap-1 underline hover:text-primary-hover"
            href={verification.source_url}
            rel="noreferrer"
            target="_blank"
          >
            {t("universities.verification.source")}
            <ExternalLink aria-hidden className="size-3" />
          </a>
        </div>
      ) : null}
    </div>
  );
}
