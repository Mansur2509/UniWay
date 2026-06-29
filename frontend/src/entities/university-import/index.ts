export type UniversityImportStatus = "pending" | "running" | "completed" | "failed";

export type UniversityImportMode = "dry_run" | "execute";

export type UniversityImportRowResult = {
  row_number: number;
  name: string;
  slug: string;
  status: "created" | "updated" | "skipped";
  duplicate_matched: boolean;
  parsed_field_count: number;
  questionable_fields: string[];
  source_url_count: number;
  last_verified_date: string | null;
  warnings: string[];
};

export type UniversityImportSummary = {
  summary?: {
    created: number;
    updated: number;
    skipped: number;
    warnings: number;
    placeholder_sat: number;
    parsed_deadlines: number;
    parsed_essays: number;
    source_urls: number;
    fields_verified: number;
  };
  rows?: UniversityImportRowResult[];
};

export type UniversityImportJob = {
  id: number;
  uploaded_by: number;
  uploaded_by_email: string;
  status: UniversityImportStatus;
  mode: UniversityImportMode;
  original_filename: string;
  row_count: number;
  created_count: number;
  updated_count: number;
  skipped_count: number;
  warning_count: number;
  source_url_count: number;
  field_verification_count: number;
  parsed_deadline_count: number;
  parsed_essay_count: number;
  questionable_sat_count: number;
  summary_json: UniversityImportSummary;
  error_message: string;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
};
