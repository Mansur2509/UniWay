import { ProtectedRoute } from "@/features/auth";
import { AdminReportsScreen } from "@/screens/admin-reports";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AdminReportsScreen />
    </ProtectedRoute>
  );
}
