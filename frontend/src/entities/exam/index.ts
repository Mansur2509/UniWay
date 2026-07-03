export type OfficialExamDate = {
  id: number;
  exam_type: "SAT" | "AP";
  event_kind: "exam" | "ordering_deadline" | "performance_task" | "portfolio_deadline";
  name: string;
  test_date: string;
  test_time: string;
  registration_deadline: string | null;
  late_registration_deadline: string | null;
  late_test_date: string | null;
  late_test_time: string;
  score_release_window: string;
  academic_year: string;
  region: string;
  source_url: string;
  last_verified_date: string;
  verification_status: "verified" | "partial" | "outdated";
  notes: string;
};
