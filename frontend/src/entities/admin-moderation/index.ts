export type ModerationStatus =
  | "pending_review"
  | "verified"
  | "needs_update"
  | "rejected"
  | "archived";

export const MODERATION_STATUSES: ModerationStatus[] = [
  "pending_review",
  "verified",
  "needs_update",
  "rejected",
  "archived"
];

export type ModerationIssueType =
  | "missing_source"
  | "outdated_data"
  | "conflicting_data"
  | "shifted_row"
  | "boilerplate"
  | "user_report"
  | "admin_note";

export const MODERATION_ISSUE_TYPES: ModerationIssueType[] = [
  "missing_source",
  "outdated_data",
  "conflicting_data",
  "shifted_row",
  "boilerplate",
  "user_report",
  "admin_note"
];

export type UniversityModerationRecord = {
  id: number;
  university: number;
  university_name: string;
  status: ModerationStatus;
  field_name: string;
  issue_type: ModerationIssueType;
  description: string;
  created_by: number | null;
  created_by_email: string | null;
  resolved_by: number | null;
  resolved_by_email: string | null;
  resolved_at: string | null;
  created_at: string;
};

export type UniversityModerationActionInput = {
  status: ModerationStatus;
  field_name?: string;
  issue_type: ModerationIssueType;
  description?: string;
};

export type ReportTargetType = "university" | "event" | "organizer" | "essay_review" | "other";

export const REPORT_TARGET_TYPES: ReportTargetType[] = [
  "university",
  "event",
  "organizer",
  "essay_review",
  "other"
];

export type ReportStatus = "open" | "reviewing" | "resolved" | "dismissed";

export const REPORT_STATUSES: ReportStatus[] = ["open", "reviewing", "resolved", "dismissed"];

export type UserReport = {
  id: number;
  reporter: number | null;
  reporter_email: string | null;
  target_type: ReportTargetType;
  target_id: number;
  reason: string;
  description: string;
  status: ReportStatus;
  resolved_at: string | null;
  created_at: string;
};

export type UserReportInput = {
  target_type: ReportTargetType;
  target_id: number;
  reason: string;
  description?: string;
};

export type OrganizerModerationStatus = "pending" | "approved" | "rejected" | "suspended";

export const ORGANIZER_MODERATION_STATUSES: OrganizerModerationStatus[] = [
  "pending",
  "approved",
  "rejected",
  "suspended"
];

export type OrganizerModerationRow = {
  id: number;
  email: string;
  username: string;
  event_count: number;
  moderation_status: OrganizerModerationStatus;
  moderation_reason: string;
  reviewed_at: string | null;
};

export type OrganizerModerationActionInput = {
  status: OrganizerModerationStatus;
  reason?: string;
};
