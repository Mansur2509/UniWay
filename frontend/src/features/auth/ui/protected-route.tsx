"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect } from "react";

import type { UserRole } from "@/entities/user";
import { useI18n } from "@/shared/i18n";
import { Button } from "@/shared/ui/button";
import { Card } from "@/shared/ui/card";

import { useAuth } from "../model/auth-context";

export function ProtectedRoute({
  children,
  allowedRoles
}: {
  children: ReactNode;
  allowedRoles?: UserRole[];
}) {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();
  const { t } = useI18n();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <Card>
        <p className="text-sm text-muted-foreground">{t("auth.checkingSession")}</p>
      </Card>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return (
      <Card className="border-danger/35 bg-danger/10">
        <h1 className="text-xl font-semibold">{t("auth.accessDenied.title")}</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {t("auth.accessDenied.description")}
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/dashboard">{t("auth.accessDenied.dashboard")}</Link>
          </Button>
          <Button asChild variant="secondary">
            <Link href="/events">{t("auth.accessDenied.events")}</Link>
          </Button>
        </div>
      </Card>
    );
  }

  return children;
}
