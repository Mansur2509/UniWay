import { ProtectedRoute } from "@/features/auth";
import { OrganizerEventsScreen } from "@/screens/organizer-events";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["organizer", "admin"]}>
      <OrganizerEventsScreen />
    </ProtectedRoute>
  );
}
