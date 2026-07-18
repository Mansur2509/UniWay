"use client";

import { Briefcase, X } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";

import type { OrganizerApplicationStatusSummary } from "@/entities/organizer-application";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { fieldClassName } from "@/shared/ui/field";
import { AppIcon } from "@/shared/ui/icon";
import { IconButton } from "@/shared/ui/icon-button";

import {
  createOrganizerApplicationRequest,
  getMyOrganizerApplicationRequest
} from "../api/organizer-application-api";

export function OrganizerApplicationCard() {
  const { t } = useI18n();
  const [isOpen, setIsOpen] = useState(false);
  const [existing, setExisting] = useState<OrganizerApplicationStatusSummary | null>(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [telegramUsername, setTelegramUsername] = useState("");
  const [description, setDescription] = useState("");
  const [projectLink, setProjectLink] = useState("");
  const [motivation, setMotivation] = useState("");
  const [experience, setExperience] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getMyOrganizerApplicationRequest()
      .then((result) => {
        if (!cancelled) setExisting(result);
      })
      .finally(() => {
        if (!cancelled) setIsLoadingStatus(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!isOpen) return;
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setIsOpen(false);
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  function openDialog() {
    setSubmitError(false);
    setIsOpen(true);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setSubmitError(false);
    try {
      const application = await createOrganizerApplicationRequest({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        telegram_username: telegramUsername.trim(),
        description: description.trim(),
        project_link: projectLink.trim() || undefined,
        motivation: motivation.trim(),
        experience: experience.trim() || undefined
      });
      setExisting({
        id: application.id,
        status: application.status,
        created_at: application.created_at,
        reviewed_at: null
      });
      setIsOpen(false);
    } catch {
      setSubmitError(true);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoadingStatus) {
    return <p className="text-sm text-muted-foreground">{t("common.loading")}</p>;
  }

  return (
    <div>
      {existing ? (
        <p className="text-sm">
          {t("settings.organizerApplication.statusLabel")}{" "}
          <span className="font-semibold">
            {t(`settings.organizerApplication.status.${existing.status}` as TranslationKey)}
          </span>
        </p>
      ) : (
        <p className="text-sm text-muted-foreground">
          {t("settings.organizerApplication.description")}
        </p>
      )}

      {!existing || existing.status === "rejected" ? (
        <Button className="mt-3" onClick={openDialog} size="sm" type="button" variant="secondary">
          <AppIcon className="mr-2" icon={Briefcase} />
          {existing ? t("settings.organizerApplication.reapply") : t("settings.organizerApplication.apply")}
        </Button>
      ) : null}

      {isOpen ? (
        <div
          aria-modal="true"
          className="fixed inset-0 z-50 grid place-items-center bg-navy/55 p-4"
          role="dialog"
        >
          <div className="max-h-[calc(100vh-2rem)] w-full max-w-lg overflow-y-auto rounded-sm border bg-card p-5 shadow-xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-eyebrow text-primary-hover">
                  {t("settings.organizerApplication.modalEyebrow")}
                </p>
                <h2 className="mt-1 text-xl font-semibold">
                  {t("settings.organizerApplication.modalTitle")}
                </h2>
                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                  {t("settings.organizerApplication.modalDescription")}
                </p>
                <p className="mt-2 text-xs font-semibold text-muted-foreground">
                  {t("settings.organizerApplication.requiredLegend")}
                </p>
              </div>
              <IconButton
                className="size-10 min-h-10"
                label={t("common.actions.close")}
                onClick={() => setIsOpen(false)}
              >
                <AppIcon icon={X} />
              </IconButton>
            </div>

            <form className="mt-4 space-y-3" onSubmit={handleSubmit}>
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="block">
                  <span className="text-xs font-semibold">
                    {t("settings.organizerApplication.firstName")}
                    <span aria-hidden className="ml-0.5 text-primary-hover">
                      *
                    </span>
                  </span>
                  <input
                    className={fieldClassName}
                    maxLength={120}
                    onChange={(event) => setFirstName(event.target.value)}
                    required
                    value={firstName}
                  />
                </label>
                <label className="block">
                  <span className="text-xs font-semibold">
                    {t("settings.organizerApplication.lastName")}
                    <span aria-hidden className="ml-0.5 text-primary-hover">
                      *
                    </span>
                  </span>
                  <input
                    className={fieldClassName}
                    maxLength={120}
                    onChange={(event) => setLastName(event.target.value)}
                    required
                    value={lastName}
                  />
                </label>
              </div>
              <label className="block">
                <span className="text-xs font-semibold">
                  {t("settings.organizerApplication.email")}
                  <span aria-hidden className="ml-0.5 text-primary-hover">
                    *
                  </span>
                </span>
                <input
                  className={fieldClassName}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                  type="email"
                  value={email}
                />
              </label>
              <label className="block">
                <span className="text-xs font-semibold">
                  {t("settings.organizerApplication.telegramUsername")}
                  <span aria-hidden className="ml-0.5 text-primary-hover">
                    *
                  </span>
                </span>
                <input
                  className={fieldClassName}
                  maxLength={33}
                  onChange={(event) => setTelegramUsername(event.target.value)}
                  placeholder={t("settings.organizerApplication.telegramUsernamePlaceholder")}
                  required
                  value={telegramUsername}
                />
              </label>
              <label className="block">
                <span className="text-xs font-semibold">
                  {t("settings.organizerApplication.description")}
                  <span aria-hidden className="ml-0.5 text-primary-hover">
                    *
                  </span>
                </span>
                <textarea
                  className={`${fieldClassName} min-h-20 resize-y py-2 leading-5`}
                  maxLength={2000}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder={t("settings.organizerApplication.descriptionPlaceholder")}
                  required
                  value={description}
                />
              </label>
              <label className="block">
                <span className="text-xs font-semibold">
                  {t("settings.organizerApplication.projectLink")}
                </span>
                <input
                  className={fieldClassName}
                  onChange={(event) => setProjectLink(event.target.value)}
                  placeholder="https://"
                  type="url"
                  value={projectLink}
                />
              </label>
              <label className="block">
                <span className="text-xs font-semibold">
                  {t("settings.organizerApplication.motivation")}
                  <span aria-hidden className="ml-0.5 text-primary-hover">
                    *
                  </span>
                </span>
                <textarea
                  className={`${fieldClassName} min-h-16 resize-y py-2 leading-5`}
                  maxLength={1000}
                  onChange={(event) => setMotivation(event.target.value)}
                  placeholder={t("settings.organizerApplication.motivationPlaceholder")}
                  required
                  value={motivation}
                />
              </label>
              <label className="block">
                <span className="text-xs font-semibold">
                  {t("settings.organizerApplication.experience")}
                </span>
                <textarea
                  className={`${fieldClassName} min-h-16 resize-y py-2 leading-5`}
                  maxLength={1000}
                  onChange={(event) => setExperience(event.target.value)}
                  placeholder={t("settings.organizerApplication.experiencePlaceholder")}
                  value={experience}
                />
              </label>

              {submitError ? (
                <p className="rounded-sm border border-danger/35 bg-danger/10 p-2 text-xs text-danger" role="alert">
                  {t("settings.organizerApplication.submitError")}
                </p>
              ) : null}

              <div className="flex justify-end gap-2 border-t pt-3">
                <Button
                  disabled={isSubmitting}
                  onClick={() => setIsOpen(false)}
                  size="sm"
                  type="button"
                  variant="ghost"
                >
                  {t("common.actions.cancel")}
                </Button>
                <Button disabled={isSubmitting} size="sm" type="submit">
                  {isSubmitting
                    ? t("settings.organizerApplication.submitting")
                    : t("settings.organizerApplication.submit")}
                </Button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}
