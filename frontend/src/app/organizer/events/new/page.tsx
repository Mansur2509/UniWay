import { ProtectedRoute } from "@/features/auth";
import { OrganizerEventFormScreen } from "@/screens/organizer-events/event-form";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["organizer", "admin"]}>
      <OrganizerEventFormScreen />
    </ProtectedRoute>
  );
}
