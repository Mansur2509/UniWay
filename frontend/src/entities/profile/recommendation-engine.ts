import type { TranslationKey } from "@/shared/i18n";

import {
  classCatalog,
  clusterClassMap,
  clusterEventKeys,
  type RecommendedClass
} from "./admissions-catalog";
import {
  majorCatalog,
  type MajorCategoryId,
  type MajorOption
} from "./major-catalog";

export type AssessmentAnswer = 1 | 2 | 3 | 4 | 5;

export type AssessmentQuestion = {
  id: string;
  section: number;
  labelKey: TranslationKey;
  clusters: MajorCategoryId[];
};

const sectionClusters: MajorCategoryId[][] = [
  ["computing", "engineering", "mathematics", "naturalSciences", "humanities"],
  ["engineering", "computing", "business", "artsDesign", "interdisciplinary"],
  ["health", "education", "socialSciences", "lawPolicy", "business"],
  ["health", "engineering", "lawPolicy", "business", "naturalSciences"],
  ["business", "engineering", "computing", "health", "mathematics"],
  ["business", "engineering", "education", "health", "artsDesign"],
  ["artsDesign", "media", "computing", "mathematics", "humanities"],
  ["lawPolicy", "education", "health", "environment", "socialSciences"]
];

export const assessmentQuestions: AssessmentQuestion[] = sectionClusters.flatMap(
  (clusters, sectionIndex) =>
    clusters.map((cluster, questionIndex) => ({
      id: `s${sectionIndex + 1}q${questionIndex + 1}`,
      section: sectionIndex + 1,
      labelKey: `admissions.assessment.s${sectionIndex + 1}.q${questionIndex + 1}` as TranslationKey,
      clusters: [
        cluster,
        ...(questionIndex % 2 === 0
          ? [sectionClusters[sectionIndex][(questionIndex + 1) % 5]]
          : [])
      ]
    }))
);

export type RecommendationResult = {
  clusters: MajorCategoryId[];
  majors: MajorOption[];
  classes: RecommendedClass[];
  eventKeys: TranslationKey[];
  examKeys: TranslationKey[];
  reasonKeys: TranslationKey[];
};

export function categoryForMajor(value: string): MajorCategoryId | null {
  return (
    majorCatalog.find((category) =>
      category.majors.some((major) => major.value === value)
    )?.id ?? null
  );
}

export function recommendFromAssessment(
  answers: Record<string, AssessmentAnswer>
): RecommendationResult {
  const scores = new Map<MajorCategoryId, number>();
  assessmentQuestions.forEach((question) => {
    const answer = answers[question.id] ?? 3;
    question.clusters.forEach((cluster) => {
      scores.set(cluster, (scores.get(cluster) ?? 0) + answer);
    });
  });
  const clusters = [...scores.entries()]
    .sort((left, right) => right[1] - left[1])
    .slice(0, 3)
    .map(([cluster]) => cluster);
  return recommendationsForClusters(clusters);
}

export function recommendationsForMajors(majors: string[]): RecommendationResult {
  const clusters = [...new Set(majors.map(categoryForMajor).filter(Boolean))] as MajorCategoryId[];
  return recommendationsForClusters(clusters.slice(0, 4));
}

export function recommendationsForClusters(
  clusters: MajorCategoryId[]
): RecommendationResult {
  const majors = clusters.flatMap(
    (cluster) => majorCatalog.find((category) => category.id === cluster)?.majors.slice(0, 4) ?? []
  );
  const classIds = [...new Set(clusters.flatMap((cluster) => clusterClassMap[cluster]))];
  const classes = classIds
    .map((id) => classCatalog.find((item) => item.id === id))
    .filter((item): item is RecommendedClass => Boolean(item));
  const eventKeys = [...new Set(clusters.flatMap((cluster) => clusterEventKeys[cluster]))];
  const examKeys = [
    ...(classIds.includes("satMath") ? ["admissions.exam.satMath" as TranslationKey] : []),
    ...(classIds.some((id) => id.startsWith("ielts")) ? ["admissions.exam.ielts" as TranslationKey] : []),
    ...(classIds.some((id) => id.startsWith("ap")) ? ["admissions.exam.ap" as TranslationKey] : [])
  ];
  return {
    clusters,
    majors: [...new Map(majors.map((major) => [major.value, major])).values()].slice(0, 10),
    classes,
    eventKeys,
    examKeys,
    reasonKeys: clusters.map(
      (cluster) => `admissions.clusterReason.${cluster}` as TranslationKey
    )
  };
}
