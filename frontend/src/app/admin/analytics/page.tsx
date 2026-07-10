import { ProtectedRoute } from "@/features/auth";
import { AdminAnalyticsScreen } from "@/screens/admin-analytics";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AdminAnalyticsScreen />
    </ProtectedRoute>
  );
}
