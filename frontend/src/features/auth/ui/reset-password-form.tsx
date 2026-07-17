"use client";

import Link from "next/link";
import {
  CheckCircle2,
  CircleAlert,
  Eye,
  EyeOff,
  KeyRound,
  LoaderCircle,
  LockKeyhole,
  TriangleAlert
} from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";

import { ApiError, getApiErrorMessage } from "@/shared/api/client";
import { useI18n } from "@/shared/i18n";
import { cn } from "@/shared/lib/cn";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { fieldClassName } from "@/shared/ui/field";
import { AppIcon } from "@/shared/ui/icon";
import { IconButton } from "@/shared/ui/icon-button";

import { confirmPasswordResetRequest } from "../api/auth-api";

type ViewState = "checking" | "missing" | "form" | "success" | "invalid" | "expired";

function readTokenFromLocation(): string {
  return new URLSearchParams(window.location.search).get("token") ?? "";
}

function ResetOutcomeCard({
  icon,
  tone,
  title,
  description
}: {
  icon: typeof CheckCircle2;
  tone: "success" | "danger";
  title: string;
  description: string;
}) {
  const { t } = useI18n();
  return (
    <Card className="w-full max-w-md p-6 sm:p-8">
      <div className="flex flex-col items-center gap-3 text-center">
        <AppIcon className={cn("size-10", tone === "success" ? "text-success" : "text-danger")} icon={icon} />
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p className="text-sm leading-6 text-muted-foreground">{description}</p>
        {tone === "success" ? (
          <Link className="mt-3 font-semibold text-primary-hover hover:underline" href="/login">
            {t("auth.resetPassword.goToLogin")}
          </Link>
        ) : (
          <Link
            className="mt-3 font-semibold text-primary-hover hover:underline"
            href="/forgot-password"
          >
            {t("auth.resetPassword.requestNewLink")}
          </Link>
        )}
      </div>
    </Card>
  );
}

export function ResetPasswordForm() {
  const { t } = useI18n();
  const [viewState, setViewState] = useState<ViewState>("checking");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const foundToken = readTokenFromLocation();
    if (!foundToken) {
      setViewState("missing");
      return;
    }
    setToken(foundToken);
    setViewState("form");
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!newPassword || !confirmPassword) {
      setError(t("auth.error.passwordRequired"));
      return;
    }
    if (newPassword !== confirmPassword) {
      setError(t("auth.passwordMismatch"));
      return;
    }
    if (newPassword.length < 8) {
      setError(t("auth.passwordTooShort"));
      return;
    }

    setIsSubmitting(true);
    try {
      await confirmPasswordResetRequest({
        token,
        new_password: newPassword,
        new_password_confirm: confirmPassword
      });
      setViewState("success");
    } catch (submitError) {
      if (submitError instanceof ApiError && typeof submitError.data === "object" && submitError.data !== null) {
        const code = Reflect.get(submitError.data, "code");
        const codeValue = Array.isArray(code) ? code[0] : code;
        if (codeValue === "expired") {
          setViewState("expired");
          return;
        }
        if (codeValue === "invalid") {
          setViewState("invalid");
          return;
        }
      }

      let errorMessage = t("common.error.generic");
      if (submitError instanceof ApiError) {
        if (submitError.errorCode === "timeout") {
          errorMessage = t("common.error.timeout");
        } else if (submitError.errorCode === "network") {
          errorMessage = t("common.error.network");
        } else {
          errorMessage = getApiErrorMessage(submitError, errorMessage);
        }
      }
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (viewState === "checking") {
    return null;
  }

  if (viewState === "missing") {
    return (
      <ResetOutcomeCard
        description={t("auth.resetPassword.missingTokenDescription")}
        icon={TriangleAlert}
        title={t("auth.resetPassword.missingTokenTitle")}
        tone="danger"
      />
    );
  }

  if (viewState === "invalid") {
    return (
      <ResetOutcomeCard
        description={t("auth.resetPassword.invalidTokenDescription")}
        icon={TriangleAlert}
        title={t("auth.resetPassword.invalidTokenTitle")}
        tone="danger"
      />
    );
  }

  if (viewState === "expired") {
    return (
      <ResetOutcomeCard
        description={t("auth.resetPassword.expiredTokenDescription")}
        icon={TriangleAlert}
        title={t("auth.resetPassword.expiredTokenTitle")}
        tone="danger"
      />
    );
  }

  if (viewState === "success") {
    return (
      <ResetOutcomeCard
        description={t("auth.resetPassword.successDescription")}
        icon={CheckCircle2}
        title={t("auth.resetPassword.successTitle")}
        tone="success"
      />
    );
  }

  return (
    <Card className="w-full max-w-md p-6 sm:p-8">
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary-hover">
        {t("auth.resetPassword.eyebrow")}
      </p>
      <h1 className="mt-2 text-3xl font-semibold">{t("auth.resetPassword.title")}</h1>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        {t("auth.resetPassword.description")}
      </p>

      <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="block text-sm font-semibold" htmlFor="reset-new-password">
            {t("auth.resetPassword.newPasswordLabel")}
          </label>
          <span className="relative block">
            <AppIcon className="absolute bottom-3 left-3 text-muted-foreground" icon={LockKeyhole} />
            <input
              autoComplete="new-password"
              className={cn(fieldClassName, "pl-10 pr-11")}
              id="reset-new-password"
              minLength={8}
              onChange={(event) => setNewPassword(event.target.value)}
              required
              type={showPassword ? "text" : "password"}
              value={newPassword}
            />
            <IconButton
              className="absolute bottom-0 right-0 size-10 min-h-10"
              label={t(showPassword ? "auth.hidePassword" : "auth.showPassword")}
              onClick={() => setShowPassword((current) => !current)}
            >
              <AppIcon icon={showPassword ? EyeOff : Eye} />
            </IconButton>
          </span>
          <span className="mt-1.5 block text-xs font-normal leading-5 text-muted-foreground">
            {t("auth.passwordHelp")}
          </span>
        </div>

        <div>
          <label className="block text-sm font-semibold" htmlFor="reset-confirm-password">
            {t("auth.resetPassword.confirmPasswordLabel")}
          </label>
          <span className="relative block">
            <AppIcon className="absolute bottom-3 left-3 text-muted-foreground" icon={LockKeyhole} />
            <input
              autoComplete="new-password"
              className={cn(fieldClassName, "pl-10 pr-11")}
              id="reset-confirm-password"
              minLength={8}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              type={showConfirmPassword ? "text" : "password"}
              value={confirmPassword}
            />
            <IconButton
              className="absolute bottom-0 right-0 size-10 min-h-10"
              label={t(showConfirmPassword ? "auth.hidePassword" : "auth.showPassword")}
              onClick={() => setShowConfirmPassword((current) => !current)}
            >
              <AppIcon icon={showConfirmPassword ? EyeOff : Eye} />
            </IconButton>
          </span>
        </div>

        {error ? (
          <p
            className="flex items-start gap-2 rounded-sm border border-danger/35 bg-danger/10 p-3 text-sm text-danger"
            role="alert"
          >
            <AppIcon className="mt-0.5" icon={CircleAlert} />
            <span>{error}</span>
          </p>
        ) : null}

        <Button className="w-full" disabled={isSubmitting} type="submit">
          <AppIcon
            className={cn("mr-2", isSubmitting && "animate-spin motion-reduce:animate-none")}
            icon={isSubmitting ? LoaderCircle : KeyRound}
          />
          {isSubmitting ? t("auth.resetPassword.submitting") : t("auth.resetPassword.submit")}
        </Button>
      </form>
    </Card>
  );
}
