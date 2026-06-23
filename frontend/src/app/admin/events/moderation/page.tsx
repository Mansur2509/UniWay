import { ProtectedRoute } from "@/features/auth";
import { EventModerationScreen } from "@/screens/event-moderation";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <EventModerationScreen />
    </ProtectedRoute>
  );
}
