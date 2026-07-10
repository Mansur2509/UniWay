import { ProtectedRoute } from "@/features/auth";
import { AdminOrganizersScreen } from "@/screens/admin-organizers";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <AdminOrganizersScreen />
    </ProtectedRoute>
  );
}
