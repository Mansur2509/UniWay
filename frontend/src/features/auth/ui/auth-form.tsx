"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useEffect, useState } from "react";

import { getApiErrorMessage } from "@/shared/api/client";
import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";
import { fieldClassName } from "@/shared/ui/field";

import { useAuth } from "../model/auth-context";

type AuthFormProps = {
  mode: "login" | "register";
  onAuthenticated?: () => void;
  onModeChange?: (mode: "login" | "register") => void;
  showModeLink?: boolean;
};

export function AuthForm({
  mode,
  onAuthenticated,
  onModeChange,
  showModeLink = true
}: AuthFormProps) {
  const router = useRouter();
  const { login, register } = useAuth();
  const { t } = useI18n();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isRegister = mode === "register";

  useEffect(() => {
    setPassword("");
    setPasswordConfirm("");
    setError(null);
  }, [mode]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    // Validate form before submission
    if (!email || !password) {
      setError(t("common.error.requiredFields"));
      return;
    }

    if (isRegister && password !== passwordConfirm) {
      setError(t("auth.passwordMismatch"));
      return;
    }

    if (isRegister && password.length < 8) {
      setError(t("auth.passwordTooShort"));
      return;
    }

    setIsSubmitting(true);

    try {
      if (isRegister) {
        await register({
          email,
          full_name: fullName,
          password,
          password_confirm: passwordConfirm
        });
      } else {
        await login({ email, password });
      }
      if (onAuthenticated) {
        onAuthenticated();
      } else {
        router.replace("/dashboard");
      }
    } catch (submitError) {
      let errorMessage = t("common.error.generic");

      // Handle network errors
      if (submitError instanceof TypeError) {
        errorMessage = t("common.error.network");
      } else {
        errorMessage = getApiErrorMessage(submitError, errorMessage);
      }

      // Map common backend errors to user-friendly messages
      if (typeof submitError === "object" && submitError !== null) {
        const errorData = Reflect.get(submitError, "data");
        if (typeof errorData === "object" && errorData !== null) {
          if (Reflect.has(errorData, "email") && isRegister) {
            errorMessage = t("auth.emailAlreadyExists");
          }
        }
      }

      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Card className="w-full max-w-md p-6 sm:p-8">
      <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary-hover">
        {isRegister ? t("auth.register.eyebrow") : t("auth.login.eyebrow")}
      </p>
      <h1 className="mt-2 text-3xl font-semibold">
        {isRegister ? t("auth.register.title") : t("auth.login.title")}
      </h1>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        {isRegister ? t("auth.register.description") : t("auth.login.description")}
      </p>

      <form className="mt-7 space-y-4" onSubmit={handleSubmit}>
        {isRegister ? (
          <label className="block text-sm font-semibold">
            {t("auth.fullName")}
            <input
              autoComplete="name"
              className={fieldClassName}
              maxLength={180}
              onChange={(event) => setFullName(event.target.value)}
              required
              type="text"
              value={fullName}
            />
          </label>
        ) : null}

        <label className="block text-sm font-semibold">
          {t("auth.email")}
          <input
            autoComplete="email"
            className={fieldClassName}
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>

        <label className="block text-sm font-semibold">
          {t("auth.password")}
          <input
            autoComplete={isRegister ? "new-password" : "current-password"}
            className={fieldClassName}
            minLength={8}
            onChange={(event) => setPassword(event.target.value)}
            required
            type="password"
            value={password}
          />
          {isRegister ? (
            <span className="mt-1.5 block text-xs font-normal leading-5 text-muted-foreground">
              {t("auth.passwordHelp")}
            </span>
          ) : null}
        </label>

        {isRegister ? (
          <label className="block text-sm font-semibold">
            {t("auth.confirmPassword")}
            <input
              autoComplete="new-password"
              className={fieldClassName}
              minLength={8}
              onChange={(event) => setPasswordConfirm(event.target.value)}
              required
              type="password"
              value={passwordConfirm}
            />
          </label>
        ) : null}

        {error ? (
          <p
            className="rounded-sm border border-danger/35 bg-danger/10 p-3 text-sm text-danger"
            role="alert"
          >
            {error}
          </p>
        ) : null}

        <Button className="w-full" disabled={isSubmitting} type="submit">
          {isSubmitting
            ? t("auth.pleaseWait")
            : isRegister
              ? t("auth.createAccount")
              : t("auth.signIn")}
        </Button>
      </form>

      {showModeLink ? (
        <p className="mt-5 text-center text-sm text-muted-foreground">
          {isRegister ? t("auth.alreadyRegistered") : t("auth.newToEduVerse")}{" "}
          {onModeChange ? (
            <button
              className="font-semibold text-primary-hover hover:underline"
              onClick={() => onModeChange(isRegister ? "login" : "register")}
              type="button"
            >
              {isRegister ? t("auth.signIn") : t("auth.createAccount")}
            </button>
          ) : (
            <Link
              className="font-semibold text-primary-hover hover:underline"
              href={isRegister ? "/login" : "/register"}
            >
              {isRegister ? t("auth.signIn") : t("auth.createAccount")}
            </Link>
          )}
        </p>
      ) : null}
    </Card>
  );
}
