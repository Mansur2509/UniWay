import { ProtectedRoute } from "@/features/auth/ui/protected-route";
import { ProfileScreen } from "@/screens/profile";

export default function Page() {
  return (
    <ProtectedRoute>
      <ProfileScreen />
    </ProtectedRoute>
  );
}
