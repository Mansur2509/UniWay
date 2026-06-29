import { ProtectedRoute } from "@/features/auth";
import { UniversityImportScreen } from "@/screens/university-import";

export default function Page() {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <UniversityImportScreen />
    </ProtectedRoute>
  );
}
