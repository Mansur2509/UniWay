import type {
  AdminAnalyticsActivity,
  AdminAnalyticsSummary,
  AdminFeatureUsage,
  UserAnalytics
} from "@/entities/analytics";
import { apiRequest } from "@/shared/api/client";

export function getMyAnalyticsRequest() {
  return apiRequest<UserAnalytics>("/me/", { base: "analytics" });
}

export function getAdminAnalyticsSummaryRequest() {
  return apiRequest<AdminAnalyticsSummary>("/summary/", { base: "adminAnalytics" });
}

export function getAdminAnalyticsFeatureUsageRequest() {
  return apiRequest<AdminFeatureUsage>("/feature-usage/", { base: "adminAnalytics" });
}

export function getAdminAnalyticsActivityRequest() {
  return apiRequest<AdminAnalyticsActivity>("/activity/", { base: "adminAnalytics" });
}
