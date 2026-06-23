import { ProtectedRoute } from "@/features/auth";
import { OrganizerParticipantsScreen } from "@/screens/organizer-events/participants";

export default async function Page({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return (
    <ProtectedRoute allowedRoles={["organizer", "admin"]}>
      <OrganizerParticipantsScreen slug={slug} />
    </ProtectedRoute>
  );
}
