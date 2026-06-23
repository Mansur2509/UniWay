import { ProtectedRoute } from "@/features/auth/ui/protected-route";
import { MyEventsScreen } from "@/screens/events/my-events";

export default function Page() {
  return (
    <ProtectedRoute>
      <MyEventsScreen />
    </ProtectedRoute>
  );
}

