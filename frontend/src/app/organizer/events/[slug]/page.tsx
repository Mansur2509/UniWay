import { ProtectedRoute } from "@/features/auth";
import { OrganizerEventFormScreen } from "@/screens/organizer-events/event-form";

export default async function Page({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return (
    <ProtectedRoute allowedRoles={["organizer", "admin"]}>
      <OrganizerEventFormScreen slug={slug} />
    </ProtectedRoute>
  );
}
