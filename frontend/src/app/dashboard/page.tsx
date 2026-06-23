import { ProtectedRoute } from "@/features/auth/ui/protected-route";
import { DashboardScreen } from "@/screens/dashboard";

export default function Page() {
  return (
    <ProtectedRoute>
      <DashboardScreen />
    </ProtectedRoute>
  );
}
