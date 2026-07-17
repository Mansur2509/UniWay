"use client";

import Link from "next/link";
import { CheckCircle2, CircleAlert, LoaderCircle, Mail, Send } from "lucide-react";
import { type FormEvent, useState } from "react";

import { ApiError, getApiErrorMessage } from "@/shared/api/client";
import { useI18n } from "@/shared/i18n";
import { cn } from "@/shared/lib/cn";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { fieldClassName } from "@/shared/ui/field";
import { AppIcon } from "@/shared/ui/icon";

import { requestPasswordResetRequest } from "../api/auth-api";

export function ForgotPasswordForm() {
  const { t } = useI18n();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!email) {
      setError(t("auth.error.emailRequired"));
      return;
    }

    setError(null);
    setIsSubmitting(true);
    try {
      await requestPasswordResetRequest(email);
      setIsSubmitted(true);
    } catch (submitError) {
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

  if (isSubmitted) {
    return (
      <Card className="w-full max-w-md p-6 sm:p-8">
        <div className="flex flex-col items-center gap-3 text-center">
          <AppIcon className="size-10 text-success" icon={CheckCircle2} />
          <h1 className="text-2xl font-semibold">{t("auth.forgotPassword.successTitle")}</h1>
          <p className="text-sm leading-6 text-muted-foreground">
            {t("auth.forgotPassword.successDescription")}
          </p>
          <Link className="mt-3 font-semibold text-primary-hover hover:underline" href="/login">
            {t("auth.forgotPassword.backToLogin")}
          </Link>
        </div>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md p-6 sm:p-8">
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary-hover">
        {t("auth.forgotPassword.eyebrow")}
      </p>
      <h1 className="mt-2 text-3xl font-semibold">{t("auth.forgotPassword.title")}</h1>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        {t("auth.forgotPassword.description")}
      </p>

      <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
        <label className="block text-sm font-semibold">
          {t("auth.email")}
          <span className="relative block">
            <AppIcon className="absolute bottom-3 left-3 text-muted-foreground" icon={Mail} />
            <input
              autoComplete="email"
              className={cn(fieldClassName, "pl-10")}
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </span>
        </label>

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
            icon={isSubmitting ? LoaderCircle : Send}
          />
          {isSubmitting ? t("auth.forgotPassword.submitting") : t("auth.forgotPassword.submit")}
        </Button>
      </form>

      <p className="mt-5 text-center text-sm text-muted-foreground">
        <Link className="font-semibold text-primary-hover hover:underline" href="/login">
          {t("auth.forgotPassword.backToLogin")}
        </Link>
      </p>
    </Card>
  );
}
