"use client";

import { CheckCircle2, Download } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import type {
  OrganizerEvent,
  OrganizerParticipant,
  PaginatedResponse
} from "@/entities/event";
import {
  checkInParticipantRequest,
  exportOrganizerEventParticipantsRequest,
  getOrganizerEventParticipantsRequest,
  getOrganizerEventRequest,
  verifyEventTicketRequest
} from "@/features/organizer-events";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { formatDateTime } from "@/shared/lib/date-time";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { DEFAULT_PAGE_SIZE, PaginationControls } from "@/shared/ui/pagination";

export function OrganizerParticipantsScreen({ slug }: { slug: string }) {
  const { locale, t } = useI18n();
  const [event, setEvent] = useState<OrganizerEvent | null>(null);
  const [participants, setParticipants] = useState<OrganizerParticipant[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportError, setExportError] = useState(false);
  const [checkingInId, setCheckingInId] = useState<number | null>(null);
  const [checkInErrorId, setCheckInErrorId] = useState<number | null>(null);
  const [ticketCode, setTicketCode] = useState("");
  const [verifiedTicketParticipant, setVerifiedTicketParticipant] =
    useState<OrganizerParticipant | null>(null);
  const [ticketVerifyError, setTicketVerifyError] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    setHasError(false);
    try {
      const [eventResponse, participantResponse] = await Promise.all([
        getOrganizerEventRequest(slug),
        getOrganizerEventParticipantsRequest(slug, {
          page: currentPage,
          page_size: DEFAULT_PAGE_SIZE
        })
      ]);
      setEvent(eventResponse);
      setParticipants(
        (participantResponse as PaginatedResponse<OrganizerParticipant>).results
      );
      setTotalCount((participantResponse as PaginatedResponse<OrganizerParticipant>).count);
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, [slug, currentPage]);

  useEffect(() => {
    void load();
  }, [load]);

  if (isLoading) {
    return (
      <Card>
        <p className="text-sm text-muted-foreground">
          {t("organizer.participants.loading")}
        </p>
      </Card>
    );
  }

  if (hasError || !event) {
    return (
      <Card className="border-danger/35 bg-danger/10">
        <p className="text-sm text-danger" role="alert">
          {t("organizer.participants.loadError")}
        </p>
        <Button className="mt-4" onClick={() => void load()} type="button">
          {t("events.actions.retry")}
        </Button>
      </Card>
    );
  }

  const totalPages = Math.max(1, Math.ceil(totalCount / DEFAULT_PAGE_SIZE));
  const pageStart = totalCount ? (currentPage - 1) * DEFAULT_PAGE_SIZE + 1 : 0;
  const pageEnd = Math.min(pageStart + Math.max(participants.length, 1) - 1, totalCount);

  async function exportParticipants() {
    setIsExporting(true);
    setExportError(false);
    try {
      const blob = await exportOrganizerEventParticipantsRequest(slug);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${slug}-participants.csv`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setExportError(true);
    } finally {
      setIsExporting(false);
    }
  }

  async function checkIn(participant: OrganizerParticipant) {
    setCheckingInId(participant.id);
    setCheckInErrorId(null);
    try {
      await checkInParticipantRequest(slug, participant.id);
      await load();
    } catch {
      setCheckInErrorId(participant.id);
    } finally {
      setCheckingInId(null);
    }
  }

  async function verifyTicket() {
    setTicketVerifyError(false);
    setVerifiedTicketParticipant(null);
    try {
      setVerifiedTicketParticipant(await verifyEventTicketRequest(slug, ticketCode));
    } catch {
      setTicketVerifyError(true);
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-sm border bg-card p-6 shadow-card sm:p-9">
        <p className="text-eyebrow text-primary-hover">
          {t("organizer.participants.eyebrow")}
        </p>
        <div className="mt-3 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
          <div>
            <h1 className="text-display">{event.title}</h1>
            <p className="mt-4 text-muted-foreground">
              {t("organizer.participants.count", {
                count: totalCount
              })}
            </p>
          </div>
          <Button
            disabled={isExporting}
            onClick={() => void exportParticipants()}
            type="button"
            variant="secondary"
          >
            <Download aria-hidden className="mr-2 size-4" />
            {isExporting
              ? t("organizer.actions.exporting")
              : t("organizer.actions.exportCsv")}
          </Button>
        </div>
      </section>

      <Card>
        <p className="text-sm leading-6 text-muted-foreground">
          {t("organizer.participants.privacyNotice")}
        </p>
        {exportError ? (
          <p className="mt-3 text-sm text-danger" role="alert">
            {t("organizer.participants.exportError")}
          </p>
        ) : null}
      </Card>

      <Card>
        <h2 className="text-xl font-semibold">
          {t("organizer.participants.ticketVerifyTitle")}
        </h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">
          {t("organizer.participants.ticketVerifyDescription")}
        </p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            className="min-h-10 flex-1 rounded-sm border bg-background px-3 py-2 text-sm"
            onChange={(event) => setTicketCode(event.target.value)}
            placeholder={t("organizer.participants.ticketCodePlaceholder")}
            value={ticketCode}
          />
          <Button
            disabled={!ticketCode.trim()}
            onClick={() => void verifyTicket()}
            type="button"
            variant="secondary"
          >
            {t("organizer.participants.verifyTicket")}
          </Button>
        </div>
        {ticketVerifyError ? (
          <p className="mt-3 text-sm text-danger" role="alert">
            {t("organizer.participants.ticketVerifyError")}
          </p>
        ) : null}
        {verifiedTicketParticipant ? (
          <p className="mt-3 text-sm text-success" role="status">
            {t("organizer.participants.ticketVerified", {
              name:
                verifiedTicketParticipant.full_name ||
                verifiedTicketParticipant.email ||
                t("events.value.notSet")
            })}
          </p>
        ) : null}
      </Card>

      {participants.length === 0 ? (
        <Card>
          <h2 className="text-xl font-semibold">
            {t("organizer.participants.emptyTitle")}
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            {t("organizer.participants.emptyDescription")}
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          <p className="text-sm font-semibold text-muted-foreground">
            {t("pagination.showingRange", {
              start: pageStart,
              end: pageEnd,
              total: totalCount
            })}
          </p>
          <div className="overflow-hidden rounded-sm border bg-card shadow-card">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[72rem] text-left text-sm">
              <thead className="border-b bg-elevated/65 text-xs uppercase tracking-[0.1em] text-muted-foreground">
                <tr>
                  <th className="px-5 py-4">{t("organizer.participants.name")}</th>
                  <th className="px-5 py-4">{t("auth.email")}</th>
                  <th className="px-5 py-4">{t("profile.telegram")}</th>
                  <th className="px-5 py-4">{t("organizer.participants.status")}</th>
                  <th className="px-5 py-4">{t("organizer.participants.ticket")}</th>
                  <th className="px-5 py-4">{t("organizer.participants.answers")}</th>
                  <th className="px-5 py-4">{t("organizer.participants.registeredAt")}</th>
                  <th className="px-5 py-4">{t("organizer.participants.actions")}</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {participants.map((participant) => (
                  <tr key={participant.id}>
                    <td className="px-5 py-4 font-semibold">
                      {participant.full_name || t("events.value.notSet")}
                    </td>
                    <td className="px-5 py-4 text-muted-foreground">
                      {participant.email}
                    </td>
                    <td className="px-5 py-4 text-muted-foreground">
                      {participant.telegram_username || t("events.value.notSet")}
                    </td>
                    <td className="px-5 py-4">
                      {t(
                        `events.registration.status.${participant.status}` as TranslationKey
                      )}
                    </td>
                    <td className="px-5 py-4 text-muted-foreground">
                      {participant.ticket_status
                        ? t(
                            `events.ticket.status.${participant.ticket_status}` as TranslationKey
                          )
                        : t("events.value.notSet")}
                      {participant.checked_in_at ? (
                        <span className="mt-1 block text-xs">
                          {formatDateTime(participant.checked_in_at, locale)}
                        </span>
                      ) : null}
                    </td>
                    <td className="px-5 py-4 text-muted-foreground">
                      {participant.answers.length > 0 ? (
                        <ul className="space-y-2">
                          {participant.answers.map((answer) => (
                            <li key={answer.field_id}>
                              <span className="font-semibold text-foreground">
                                {answer.field_label}:
                              </span>{" "}
                              {formatAnswerValue(answer.value)}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        t("events.value.notSet")
                      )}
                    </td>
                    <td className="px-5 py-4 text-muted-foreground">
                      {formatDateTime(participant.created_at, locale)}
                    </td>
                    <td className="px-5 py-4">
                      {participant.status === "attended" ? (
                        <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-success">
                          <CheckCircle2 aria-hidden className="size-4" />
                          {t("organizer.participants.checkedIn")}
                        </span>
                      ) : participant.status === "cancelled" ? (
                        <span className="text-sm text-muted-foreground">
                          {t("events.registration.status.cancelled")}
                        </span>
                      ) : (
                        <Button
                          disabled={checkingInId === participant.id}
                          onClick={() => void checkIn(participant)}
                          size="sm"
                          type="button"
                          variant="secondary"
                        >
                          {checkingInId === participant.id
                            ? t("organizer.participants.checkingIn")
                            : t("organizer.participants.checkIn")}
                        </Button>
                      )}
                      {checkInErrorId === participant.id ? (
                        <p className="mt-2 text-xs text-danger" role="alert">
                          {t("organizer.participants.checkInError")}
                        </p>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
              </table>
            </div>
          </div>
          {totalPages > 1 ? (
            <PaginationControls
              currentPage={currentPage}
              onNext={() => setCurrentPage((page) => page + 1)}
              onPageSelect={setCurrentPage}
              onPrevious={() => setCurrentPage((page) => page - 1)}
              totalPages={totalPages}
            />
          ) : null}
        </div>
      )}

      <Button asChild variant="ghost">
        <Link href="/organizer/events">{t("organizer.actions.backToList")}</Link>
      </Button>
    </div>
  );
}

function formatAnswerValue(value: unknown) {
  if (Array.isArray(value)) {
    return value.join(", ");
  }
  if (typeof value === "string") {
    return value;
  }
  if (value === null || value === undefined) {
    return "";
  }
  return JSON.stringify(value);
}
