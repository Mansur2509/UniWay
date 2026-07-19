import type { BadgeTone } from "@/shared/ui/badge";

import type {
  ApplicationFitTier,
  ApplicationPriority,
  DateConfidence,
  Urgency
} from "../index";

export const FIT_TIER_TONE: Record<ApplicationFitTier, BadgeTone> = {
  reach: "danger",
  competitive: "warning",
  target: "accent",
  safety: "success",
  unknown: "muted"
};

export const DEADLINE_STATUS_TONE: Record<
  "verified" | "estimated" | "not_published" | "outdated" | "requires_review",
  BadgeTone
> = {
  verified: "success",
  estimated: "warning",
  not_published: "muted",
  outdated: "danger",
  requires_review: "warning"
};

export const PRIORITY_TONE: Record<ApplicationPriority, BadgeTone> = {
  low: "muted",
  medium: "accent",
  high: "warning",
  dream: "danger"
};

export const URGENCY_TONE: Record<Urgency, BadgeTone> = {
  overdue: "danger",
  critical: "danger",
  urgent: "warning",
  soon: "warning",
  upcoming: "accent",
  far: "muted",
  unknown: "muted"
};

export const CONFIDENCE_TONE: Record<DateConfidence, BadgeTone> = {
  verified: "success",
  partial: "accent",
  user_provided: "accent",
  estimated: "muted",
  missing: "warning"
};
