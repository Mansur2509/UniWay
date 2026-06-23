import type { UserRole } from "@/entities/user";

export type ScholarshipNeed = "yes" | "no" | "unsure";

export type TestScoreValue = string | number | string[];
export type TestScores = Record<string, TestScoreValue>;

export type PlannedExam = {
  name: string;
  date: string;
  target_score: string;
};

export type ExamPlans = {
  taken: string[];
  planned: PlannedExam[];
};

export type ActivityProfile = {
  extracurriculars: string[];
  honors: string[];
  sports: string[];
  olympiads: string[];
  research_projects: string[];
  mun_debate: string[];
  volunteering: string[];
  leadership: string[];
  work_internships: string[];
};

export type OnboardingSection =
  | "identity"
  | "academic"
  | "exams"
  | "activities"
  | "support";

export type StudentProfileDetails = {
  id: number;
  email: string;
  role: UserRole;
  full_name: string;
  birth_date: string | null;
  country: string;
  city: string;
  school_or_university: string;
  grade: string;
  expected_graduation_year: number | null;
  education_status: string;
  gpa: string | number | null;
  gpa_scale: string | number | null;
  intended_degree: string;
  target_countries: string[];
  intended_majors: string[];
  target_universities: string[];
  university_unsure: boolean;
  major_unsure: boolean;
  scholarship_need: ScholarshipNeed;
  interests: string[];
  languages: string[];
  test_scores: TestScores;
  exam_plans: ExamPlans;
  preparation_needs: string[];
  activities: ActivityProfile;
  essay_status: "yes" | "no" | "not_yet";
  essay_stage: string;
  support_priorities: string[];
  interested_classes: string[];
  ap_interests: string[];
  career_interests: string[];
  mun_debate_interest: boolean;
  research_interest: boolean;
  finance_literacy_interest: boolean;
  onboarding_sections: OnboardingSection[];
  onboarding_version: number;
  onboarding_completed_at: string | null;
  telegram_username: string;
  phone: string;
  updated_at: string;
};

export type UpdateStudentProfileInput = Partial<
  Omit<StudentProfileDetails, "id" | "email" | "role" | "updated_at">
>;

export type ProfileCompletion = {
  percentage: number;
  completed_fields: number;
  total_fields: number;
  missing_fields: string[];
  missing_sections: string[];
  required_fields: string[];
  is_complete: boolean;
  can_complete: boolean;
};

export type ApplicationReadiness = {
  stars: 1 | 2 | 3 | 4 | 5;
  level: "foundation" | "developing" | "competitive" | "strong" | "outstanding";
  score_components: Record<string, number>;
  strengths: string[];
  improvements: string[];
  comparison_status: "published_ranges" | "official_data_needed";
  compared_universities: string[];
  official_sources: Array<{
    title: string;
    url: string;
    university: string;
  }>;
};

export {
  majorCatalog,
  recommendationSignals,
  type MajorCategoryId,
  type MajorOption
} from "./major-catalog";
export {
  classCatalog,
  targetCountries,
  type RecommendedClass,
  type RecommendedClassId
} from "./admissions-catalog";
export {
  assessmentQuestions,
  categoryForMajor,
  recommendFromAssessment,
  recommendationsForMajors,
  type AssessmentAnswer,
  type RecommendationResult
} from "./recommendation-engine";
export { ReadinessCard } from "./ui/readiness-card";
