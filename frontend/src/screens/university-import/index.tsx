"use client";

import Link from "next/link";
import {
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  FileSpreadsheet,
  RefreshCw,
  Upload
} from "lucide-react";
import { useState } from "react";

import type {
  UniversityImportJob,
  UniversityImportRowResult,
  UniversityImportStatus
} from "@/entities/university-import";
import {
  createUniversityImportDryRunRequest,
  createUniversityImportExecuteRequest,
  getUniversityImportJobRequest
} from "@/features/university-import";
import { useI18n, type TranslationKey } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { fieldClassName } from "@/shared/ui/field";

type ImportAction = "dry_run" | "execute" | null;

const TERMINAL_STATUSES: UniversityImportStatus[] = ["completed", "failed"];

function isTerminal(job: UniversityImportJob) {
  return TERMINAL_STATUSES.includes(job.status);
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function StatusBadge({ status }: { status: UniversityImportStatus }) {
  const { t } = useI18n();
  const isGood = status === "completed";
  const isBad = status === "failed";
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-sm border px-2 py-1 text-xs font-semibold ${
        isGood
          ? "border-success/40 bg-success/10 text-success"
          : isBad
            ? "border-danger/40 bg-danger/10 text-danger"
            : "border-border bg-elevated text-muted-foreground"
      }`}
    >
      {isGood ? <CheckCircle2 aria-hidden className="size-3.5" /> : null}
      {isBad ? <AlertTriangle aria-hidden className="size-3.5" /> : null}
      {t(`universityImport.status.${status}` as TranslationKey)}
    </span>
  );
}

function Metric({
  label,
  value
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-sm border bg-surface p-3">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-1 text-xl font-semibold">{value}</dd>
    </div>
  );
}

function rowsWithWarnings(rows: UniversityImportRowResult[]) {
  return rows.filter((row) => row.warnings.length > 0 || row.questionable_fields.length > 0);
}

function ImportReport({
  job,
  title,
  description
}: {
  job: UniversityImportJob | null;
  title: string;
  description: string;
}) {
  const { t } = useI18n();
  if (!job) {
    return (
      <Card>
        <h2 className="text-xl font-semibold">{title}</h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
        <p className="mt-5 text-sm text-muted-foreground">
          {t("universityImport.report.empty")}
        </p>
      </Card>
    );
  }

  const rows = job.summary_json.rows ?? [];
  const warningRows = rowsWithWarnings(rows);
  const hasSkipped = job.skipped_count > 0;
  const hasQuestionableSat = job.questionable_sat_count > 0;
  const hasMissingSources =
    job.source_url_count === 0 ||
    rows.some((row) =>
      row.warnings.some((warning) => warning.toLowerCase().includes("missing source"))
    );

  return (
    <Card>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">{title}</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
        </div>
        <StatusBadge status={job.status} />
      </div>

      <dl className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label={t("universityImport.fields.filename")} value={job.original_filename} />
        <Metric label={t("universityImport.fields.rowCount")} value={job.row_count} />
        <Metric label={t("universityImport.fields.created")} value={job.created_count} />
        <Metric label={t("universityImport.fields.updated")} value={job.updated_count} />
        <Metric label={t("universityImport.fields.skipped")} value={job.skipped_count} />
        <Metric label={t("universityImport.fields.warnings")} value={job.warning_count} />
        <Metric
          label={t("universityImport.fields.questionableSat")}
          value={job.questionable_sat_count}
        />
        <Metric
          label={t("universityImport.fields.fieldVerifications")}
          value={job.field_verification_count}
        />
        <Metric
          label={t("universityImport.fields.parsedDeadlines")}
          value={job.parsed_deadline_count}
        />
        <Metric
          label={t("universityImport.fields.parsedEssays")}
          value={job.parsed_essay_count}
        />
        <Metric label={t("universityImport.fields.sourceUrls")} value={job.source_url_count} />
      </dl>

      {job.status === "failed" ? (
        <p className="mt-5 rounded-sm border border-danger/35 bg-danger/10 p-3 text-sm text-danger">
          {job.error_message || t("universityImport.report.unknownError")}
        </p>
      ) : null}

      {hasSkipped || hasQuestionableSat || hasMissingSources ? (
        <div className="mt-5 space-y-2 rounded-sm border border-warning/40 bg-warning/10 p-4 text-sm">
          {hasSkipped ? (
            <p className="flex gap-2">
              <AlertTriangle aria-hidden className="mt-0.5 size-4 shrink-0" />
              <span>{t("universityImport.warning.skipped")}</span>
            </p>
          ) : null}
          {hasQuestionableSat ? (
            <p className="flex gap-2">
              <AlertTriangle aria-hidden className="mt-0.5 size-4 shrink-0" />
              <span>{t("universityImport.warning.questionableSat")}</span>
            </p>
          ) : null}
          {hasMissingSources ? (
            <p className="flex gap-2">
              <AlertTriangle aria-hidden className="mt-0.5 size-4 shrink-0" />
              <span>{t("universityImport.warning.missingSources")}</span>
            </p>
          ) : null}
        </div>
      ) : null}

      {warningRows.length ? (
        <details className="mt-5 rounded-sm border bg-elevated/45 p-4">
          <summary className="cursor-pointer text-sm font-semibold">
            {t("universityImport.report.rowWarnings", { count: warningRows.length })}
          </summary>
          <ul className="mt-3 space-y-3 text-sm">
            {warningRows.slice(0, 10).map((row) => (
              <li className="border-t pt-3 first:border-t-0 first:pt-0" key={row.row_number}>
                <p className="font-semibold">
                  {t("universityImport.report.rowLabel", {
                    row: row.row_number,
                    name: row.name
                  })}
                </p>
                <p className="mt-1 text-muted-foreground">
                  {[...row.warnings, ...row.questionable_fields].join("; ")}
                </p>
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </Card>
  );
}

function VerificationLinks() {
  const { t } = useI18n();
  const links = [
    { href: "/universities", key: "universityImport.verify.universities" },
    {
      href: "/universities/massachusetts-institute-of-technology",
      key: "universityImport.verify.mit"
    },
    { href: "/universities?search=Oxford", key: "universityImport.verify.oxford" },
    { href: "/universities?search=NUS", key: "universityImport.verify.nus" },
    { href: "/universities?search=Bocconi", key: "universityImport.verify.bocconi" },
    { href: "/universities?search=Sorbonne", key: "universityImport.verify.sorbonne" },
    {
      href: "/universities/massachusetts-institute-of-technology?tab=sources",
      key: "universityImport.verify.sources"
    }
  ];

  return (
    <Card>
      <h2 className="text-xl font-semibold">{t("universityImport.verify.title")}</h2>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        {t("universityImport.verify.description")}
      </p>
      <div className="mt-5 flex flex-wrap gap-2">
        {links.map((link) => (
          <Button asChild key={link.key} size="sm" variant="secondary">
            <Link href={link.href}>
              {t(link.key as TranslationKey)}
              <ExternalLink aria-hidden className="ml-2 size-3.5" />
            </Link>
          </Button>
        ))}
      </div>
    </Card>
  );
}

export function UniversityImportScreen() {
  const { t } = useI18n();
  const [file, setFile] = useState<File | null>(null);
  const [dryRunJob, setDryRunJob] = useState<UniversityImportJob | null>(null);
  const [executeJob, setExecuteJob] = useState<UniversityImportJob | null>(null);
  const [action, setAction] = useState<ImportAction>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);

  async function pollJob(
    jobId: number,
    update: (job: UniversityImportJob) => void
  ): Promise<UniversityImportJob> {
    let latest = await getUniversityImportJobRequest(jobId);
    update(latest);
    for (let attempt = 0; attempt < 80 && !isTerminal(latest); attempt += 1) {
      await sleep(1500);
      latest = await getUniversityImportJobRequest(jobId);
      update(latest);
    }
    return latest;
  }

  async function runDryRun() {
    if (!file) return;
    setAction("dry_run");
    setActionError(null);
    setDryRunJob(null);
    setExecuteJob(null);
    try {
      const job = await createUniversityImportDryRunRequest(file);
      setDryRunJob(job);
      if (!isTerminal(job)) {
        await pollJob(job.id, setDryRunJob);
      }
    } catch {
      setActionError(t("universityImport.error.actionFailed"));
    } finally {
      setAction(null);
    }
  }

  async function runExecute() {
    if (!file || dryRunJob?.status !== "completed") return;
    setConfirmOpen(false);
    setAction("execute");
    setActionError(null);
    setExecuteJob(null);
    try {
      const job = await createUniversityImportExecuteRequest(file);
      setExecuteJob(job);
      if (!isTerminal(job)) {
        await pollJob(job.id, setExecuteJob);
      }
    } catch {
      setActionError(t("universityImport.error.actionFailed"));
    } finally {
      setAction(null);
    }
  }

  const canExecute = Boolean(file && dryRunJob?.status === "completed" && !action);

  return (
    <div className="space-y-6">
      <section className="rounded-sm border bg-card p-6 shadow-card sm:p-9">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary-hover">
          {t("universityImport.eyebrow")}
        </p>
        <h1 className="mt-3 text-3xl font-semibold sm:text-5xl">
          {t("universityImport.title")}
        </h1>
        <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
          {t("universityImport.description")}
        </p>
      </section>

      <section className="grid gap-6 xl:grid-cols-[24rem_1fr]">
        <Card>
          <div className="flex items-start gap-3">
            <FileSpreadsheet aria-hidden className="mt-1 size-5 text-primary-hover" />
            <div>
              <h2 className="text-xl font-semibold">{t("universityImport.upload.title")}</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {t("universityImport.upload.description")}
              </p>
            </div>
          </div>

          <label className="mt-5 block">
            <span className="text-sm font-semibold">
              {t("universityImport.upload.fileLabel")}
            </span>
            <input
              accept=".xlsx"
              className={`${fieldClassName} mt-2`}
              onChange={(event) => {
                const selectedFile = event.target.files?.[0] ?? null;
                setFile(selectedFile);
                setDryRunJob(null);
                setExecuteJob(null);
                setActionError(null);
              }}
              type="file"
            />
          </label>

          <p className="mt-3 text-sm text-muted-foreground">
            {file
              ? t("universityImport.upload.selected", { filename: file.name })
              : t("universityImport.upload.none")}
          </p>

          {actionError ? (
            <p className="mt-4 rounded-sm border border-danger/35 bg-danger/10 p-3 text-sm text-danger">
              {actionError}
            </p>
          ) : null}

          <div className="mt-6 flex flex-col gap-3">
            <Button
              disabled={!file || action !== null}
              onClick={() => void runDryRun()}
              type="button"
            >
              {action === "dry_run" ? (
                <RefreshCw aria-hidden className="mr-2 size-4 animate-spin" />
              ) : (
                <Upload aria-hidden className="mr-2 size-4" />
              )}
              {action === "dry_run"
                ? t("universityImport.actions.running")
                : t("universityImport.actions.dryRun")}
            </Button>
            <Button
              disabled={!canExecute}
              onClick={() => setConfirmOpen(true)}
              type="button"
              variant="secondary"
            >
              {action === "execute" ? (
                <RefreshCw aria-hidden className="mr-2 size-4 animate-spin" />
              ) : (
                <CheckCircle2 aria-hidden className="mr-2 size-4" />
              )}
              {action === "execute"
                ? t("universityImport.actions.running")
                : t("universityImport.actions.execute")}
            </Button>
          </div>

          <p className="mt-4 text-xs leading-5 text-muted-foreground">
            {t("universityImport.safety")}
          </p>
        </Card>

        <div className="space-y-6">
          <ImportReport
            description={t("universityImport.dryRun.description")}
            job={dryRunJob}
            title={t("universityImport.dryRun.title")}
          />
          <ImportReport
            description={t("universityImport.execute.description")}
            job={executeJob}
            title={t("universityImport.execute.title")}
          />
        </div>
      </section>

      <VerificationLinks />

      {confirmOpen ? (
        <div
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-background/70 p-4 backdrop-blur-sm"
          role="dialog"
        >
          <div className="w-full max-w-lg rounded-sm border bg-card p-6 shadow-card">
            <h2 className="text-xl font-semibold">{t("universityImport.confirm.title")}</h2>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              {t("universityImport.confirm.body")}
            </p>
            <div className="mt-6 flex flex-wrap justify-end gap-3">
              <Button
                onClick={() => setConfirmOpen(false)}
                type="button"
                variant="secondary"
              >
                {t("universityImport.confirm.cancel")}
              </Button>
              <Button onClick={() => void runExecute()} type="button">
                {t("universityImport.confirm.execute")}
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
