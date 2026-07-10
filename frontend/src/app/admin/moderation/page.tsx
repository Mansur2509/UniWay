import { ProtectedRoute } from "@/features/auth";
import { AdminModerationScreen } from "@/screens/admin-moderation";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AdminModerationScreen />
    </ProtectedRoute>
  );
}
