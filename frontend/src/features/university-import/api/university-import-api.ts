import type { UniversityImportJob } from "@/entities/university-import";
import { apiRequest } from "@/shared/api/client";

function uploadImportWorkbook(path: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest<UniversityImportJob>(path, {
    base: "universityImport",
    method: "POST",
    body: formData,
    timeoutMs: 120_000
  });
}

export function createUniversityImportDryRunRequest(file: File) {
  return uploadImportWorkbook("/dry-run/", file);
}

export function createUniversityImportExecuteRequest(file: File) {
  return uploadImportWorkbook("/execute/", file);
}

export function getUniversityImportJobRequest(id: number) {
  return apiRequest<UniversityImportJob>(`/jobs/${id}/`, {
    base: "universityImport"
  });
}
