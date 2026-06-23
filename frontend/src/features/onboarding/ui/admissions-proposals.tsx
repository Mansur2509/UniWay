"use client";

import { BookOpenCheck, CalendarDays, GraduationCap, Route } from "lucide-react";

import {
  recommendationsForMajors,
  type RecommendationResult
} from "@/entities/profile";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

type AdmissionsProposalsProps = {
  majors: string[];
  selectedClasses: string[];
  targetCountries: string[];
  scholarshipNeed: "yes" | "no" | "unsure";
  hasExamPlan: boolean;
  hasActivities: boolean;
  essayStage: string;
  onAddClass: (value: string) => void;
};

function ProposalList({
  title,
  items
}: {
  title: string;
  items: string[];
}) {
  if (!items.length) return null;
  return (
    <div>
      <h3 className="text-sm font-semibold">{title}</h3>
      <ul className="mt-2 space-y-1.5 text-xs leading-5 text-muted-foreground">
        {items.map((item) => (
          <li className="border-l-2 border-border pl-2" key={item}>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function AdmissionsProposals({
  majors,
  selectedClasses,
  targetCountries,
  scholarshipNeed,
  hasExamPlan,
  hasActivities,
  essayStage,
  onAddClass
}: AdmissionsProposalsProps) {
  const { t } = useI18n();
  const recommendations: RecommendationResult = recommendationsForMajors(majors);
  const improvements = [
    ...(!majors.length ? [t("admissions.improvement.majors")] : []),
    ...(!targetCountries.length ? [t("admissions.improvement.countries")] : []),
    ...(!hasExamPlan ? [t("admissions.improvement.exams")] : []),
    ...(!hasActivities ? [t("admissions.improvement.activities")] : []),
    ...(!essayStage.trim() ? [t("admissions.improvement.essays")] : [])
  ];
  const searchDirection =
    scholarshipNeed === "yes"
      ? t("admissions.proposals.searchScholarship")
      : targetCountries.length
        ? t("admissions.proposals.searchCountries")
        : t("admissions.proposals.searchUndecided");
  const roadmapDirection = !hasExamPlan
    ? t("admissions.proposals.roadmapExam")
    : improvements.length
      ? t("admissions.proposals.roadmapProfile")
      : t("admissions.proposals.roadmapActivity");

  return (
    <Card className="lg:sticky lg:top-24">
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary-hover">
        {t("admissions.proposals.title")}
      </p>
      <p className="mt-2 text-xs leading-5 text-muted-foreground">
        {t("admissions.proposals.description")}
      </p>

      {!majors.length ? (
        <p className="mt-5 border border-dashed bg-elevated/35 p-3 text-xs leading-5 text-muted-foreground">
          {t("admissions.proposals.empty")}
        </p>
      ) : (
        <div className="mt-5 space-y-5">
          <ProposalList
            items={recommendations.reasonKeys.map((key) => t(key))}
            title={t("admissions.proposals.majors")}
          />
          <div>
            <h3 className="flex items-center gap-2 text-sm font-semibold">
              <BookOpenCheck aria-hidden className="size-4 text-accent" />
              {t("admissions.proposals.classes")}
            </h3>
            <div className="mt-2 space-y-2">
              {recommendations.classes.slice(0, 6).map((item) => {
                const added = selectedClasses.includes(item.value);
                return (
                  <div
                    className="flex items-center justify-between gap-2 border bg-surface p-2"
                    key={item.id}
                  >
                    <span className="text-xs font-medium">{t(item.labelKey)}</span>
                    <Button
                      className="h-8 px-2 text-xs"
                      disabled={added}
                      onClick={() => onAddClass(item.value)}
                      type="button"
                      variant="ghost"
                    >
                      {added
                        ? t("admissions.classes.added")
                        : t("admissions.classes.add")}
                    </Button>
                  </div>
                );
              })}
            </div>
          </div>
          <ProposalList
            items={recommendations.examKeys.map((key) => t(key))}
            title={t("admissions.proposals.exams")}
          />
          <ProposalList
            items={recommendations.eventKeys.map((key) => t(key))}
            title={t("admissions.proposals.events")}
          />
        </div>
      )}

      <div className="mt-5 space-y-4 border-t pt-5">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <GraduationCap aria-hidden className="size-4 text-accent" />
            {t("admissions.proposals.search")}
          </h3>
          <p className="mt-2 text-xs leading-5 text-muted-foreground">
            {searchDirection}
          </p>
        </div>
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Route aria-hidden className="size-4 text-accent" />
            {t("admissions.proposals.roadmap")}
          </h3>
          <p className="mt-2 text-xs leading-5 text-muted-foreground">
            {roadmapDirection}
          </p>
        </div>
        <ProposalList
          items={improvements}
          title={t("admissions.proposals.improvements")}
        />
        {recommendations.eventKeys.length ? (
          <p className="flex items-start gap-2 text-xs leading-5 text-muted-foreground">
            <CalendarDays aria-hidden className="mt-0.5 size-4 shrink-0 text-accent" />
            {recommendations.eventKeys
              .slice(0, 2)
              .map((key: TranslationKey) => t(key))
              .join(" · ")}
          </p>
        ) : null}
      </div>
    </Card>
  );
}
