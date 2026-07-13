export type OfficialExamDate = {
  id: number;
  exam_type: "SAT" | "AP";
  event_kind: "exam" | "ordering_deadline" | "performance_task" | "portfolio_deadline";
  name: string;
  test_date: string | null;
  test_time: string;
  registration_deadline: string | null;
  late_registration_deadline: string | null;
  late_test_date: string | null;
  late_test_time: string;
  score_release_window: string;
  academic_year: string;
  exam_year: number | null;
  region: string;
  source_url: string;
  source_title: string;
  last_verified_date: string;
  last_verified_at: string | null;
  local_timezone: string;
  verification_status:
    | "verified"
    | "partial"
    | "not_published"
    | "outdated"
    | "requires_review";
  date_status: "verified" | "not_published" | "outdated" | "requires_review";
  countdown_days: number | null;
  notes: string;
};
