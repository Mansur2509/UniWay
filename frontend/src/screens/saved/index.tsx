"use client";

import { Bookmark, CalendarClock, GraduationCap, MapPin, Sparkles } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import type { SavedUniversity } from "@/entities/university";
import { getShortlistRequest, removeFromShortlistRequest } from "@/features/universities";
import { useI18n } from "@/shared/i18n";
import { formatDate } from "@/shared/lib/date-time";
import { useSlowLoad } from "@/shared/lib/use-slow-load";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { EmptyState } from "@/shared/ui/empty-state";
import { IconChip } from "@/shared/ui/icon-chip";
import { Reveal } from "@/shared/ui/reveal";
import { SkeletonRows } from "@/shared/ui/skeleton";

export function SavedScreen() {
  const { locale, t } = useI18n();
  const [saved, setSaved] = useState<SavedUniversity[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [retryToken, setRetryToken] = useState(0);
  const [removingSlug, setRemovingSlug] = useState<string | null>(null);
  const [actionError, setActionError] = useState(false);
  const isSlow = useSlowLoad(isLoading);

  useEffect(() => {
    let active = true;
    setIsLoading(true);
    setHasError(false);
    getShortlistRequest()
      .then((response) => {
        if (active) setSaved(response.results);
      })
      .catch(() => {
        if (active) setHasError(true);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [retryToken]);

  const handleRemove = useCallback(async (item: SavedUniversity) => {
    setActionError(false);
    setRemovingSlug(item.university.slug);
    try {
      await removeFromShortlistRequest(item.university.slug);
      setSaved((prev) => (prev ? prev.filter((entry) => entry.id !== item.id) : prev));
    } catch {
      setActionError(true);
    } finally {
      setRemovingSlug(null);
    }
  }, []);

  return (
    <div className="space-y-5">
      <section className="relative overflow-hidden rounded-sm border bg-card p-6 shadow-card sm:p-9">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-gradient-to-br from-scholarship/8 via-transparent to-primary/8"
        />
        <div className="relative flex min-w-0 items-start gap-3">
          <IconChip icon={Bookmark} size="lg" tone="scholarship" />
          <div>
            <p className="text-eyebrow text-primary-hover">{t("saved.eyebrow")}</p>
            <h1 className="text-display mt-2 max-w-3xl">{t("saved.title")}</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
              {t("saved.description")}
            </p>
          </div>
        </div>
      </section>

      {actionError ? (
        <Card animate="fade-up" className="border-danger/35 bg-danger/10">
          <p className="text-sm text-danger" role="alert">
            {t("saved.states.actionError")}
          </p>
        </Card>
      ) : null}

      {isLoading ? (
        <div className="space-y-3">
          <SkeletonRows count={3} />
        </div>
      ) : hasError ? (
        <Card className="flex flex-col items-center gap-3 py-8 text-center">
          <p className="text-sm text-danger" role="alert">
            {t("saved.states.error")}
          </p>
          <Button onClick={() => setRetryToken((value) => value + 1)} size="sm" type="button">
            {t("common.retry")}
          </Button>
          {isSlow ? (
            <p className="text-xs leading-5 text-muted-foreground" role="status">
              {t("common.wakingUp")}
            </p>
          ) : null}
        </Card>
      ) : !saved || saved.length === 0 ? (
        <EmptyState
          action={
            <Button asChild size="sm" variant="secondary">
              <Link href="/universities">{t("saved.empty.action")}</Link>
            </Button>
          }
          description={t("saved.empty.description")}
          icon={Bookmark}
          title={t("saved.empty.title")}
        />
      ) : (
        <>
          <p className="text-sm font-semibold text-muted-foreground">
            {t("saved.count", { count: saved.length })}
          </p>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {saved.map((item, index) => (
              <Reveal delayMs={Math.min(index, 8) * 40} key={item.id}>
                <Card className="flex min-w-0 flex-col gap-2 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    {item.university.scholarship_available ? (
                      <Badge className="gap-1 normal-case tracking-normal" tone="scholarship">
                        {t("universities.fields.scholarshipAvailable")}
                      </Badge>
                    ) : null}
                    {item.university.application_deadline ? (
                      <Badge className="gap-1 normal-case tracking-normal" tone="accent">
                        <CalendarClock aria-hidden className="size-3.5" />
                        {formatDate(item.university.application_deadline, locale)}
                      </Badge>
                    ) : null}
                  </div>
                  <h2 className="flex items-center gap-2 text-base font-semibold break-words">
                    <IconChip icon={GraduationCap} size="sm" tone="primary" />
                    <Link className="hover:text-primary-hover" href={`/universities/${item.university.slug}`}>
                      {item.university.name}
                    </Link>
                  </h2>
                  <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <MapPin aria-hidden className="size-3.5 shrink-0" />
                    <span className="truncate">
                      {[item.university.city, item.university.country].filter(Boolean).join(", ")}
                    </span>
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {t("saved.savedOn", { date: formatDate(item.created_at, locale) })}
                  </p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Button asChild size="sm" variant="secondary">
                      <Link href={`/universities/${item.university.slug}`}>
                        {t("universities.actions.viewDetails")}
                      </Link>
                    </Button>
                    <Button
                      disabled={removingSlug === item.university.slug}
                      onClick={() => void handleRemove(item)}
                      size="sm"
                      type="button"
                      variant="ghost"
                    >
                      {removingSlug === item.university.slug
                        ? t("saved.unsaving")
                        : t("saved.unsave")}
                    </Button>
                  </div>
                </Card>
              </Reveal>
            ))}
          </div>
        </>
      )}

      <Card className="flex items-start gap-4 bg-muted/45">
        <IconChip icon={Sparkles} tone="muted" />
        <div>
          <h2 className="text-sm font-semibold">{t("saved.otherTypes.title")}</h2>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            {t("saved.otherTypes.description")}
          </p>
        </div>
      </Card>
    </div>
  );
}
