from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from services.university_service import xlsx_import
from services.university_service.models import University, UniversityImportJob

User = get_user_model()


def workbook_upload(name: str = "Universities Data.xlsx"):
    from django.core.files.uploadedfile import SimpleUploadedFile
    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = xlsx_import.DEFAULT_SHEET_NAME
    worksheet.append(xlsx_import.EXPECTED_HEADERS)
    row = {header: "" for header in xlsx_import.EXPECTED_HEADERS}
    row.update(
        {
            "Name": "Admin Import University",
            "Country": "USA",
            "City": "Boston, MA",
            "Official Website": "https://admin-import.example.edu",
            "Admissions URL": "https://admin-import.example.edu/admissions",
            "Majors": "Computer Science, Economics",
            "Deadlines": "Regular Decision (RD): Jan 1, 2027",
            "SAT 25th": 1400,
            "SAT 50th": 1480,
            "SAT 75th": 1540,
            "IELTS Minimum": 7.0,
            "IELTS Competitive": 7.5,
            "Average GPA": 3.9,
            "Acceptance Rate": "12%",
            "Tuition": "$55,000",
            "Scholarships": "Need-based aid and merit scholarship",
            "AP Recommendations by Major": "CS: AP Calculus BC; AP Computer Science A",
            "Application Requirements": "Common App; transcript; recommendations",
            "Essays": "Common App essay (650 words)",
            "Financial Aid": "International students may apply for need-based aid.",
            "Source URLs": "https://admin-import.example.edu/admissions",
            "Last Verified Date": "2026-01-15",
        }
    )
    worksheet.append([row[header] for header in xlsx_import.EXPECTED_HEADERS])
    buffer = BytesIO()
    workbook.save(buffer)
    return SimpleUploadedFile(
        name,
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@override_settings(UNIVERSITY_IMPORT_RUN_INLINE=True)
class AdminUniversityImportApiTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="student-import@example.com",
            email="student-import@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.STUDENT,
        )
        self.organizer = User.objects.create_user(
            username="organizer-import@example.com",
            email="organizer-import@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ORGANIZER,
        )
        self.admin = User.objects.create_user(
            username="admin-import@example.com",
            email="admin-import@example.com",
            password="Strong-Development-Password-842!",
            role=User.Role.ADMIN,
        )
        self.dry_run_url = reverse("university-import:dry-run")
        self.execute_url = reverse("university-import:execute")

    def test_unauthenticated_upload_is_blocked(self):
        response = self.client.post(
            self.dry_run_url,
            {"file": workbook_upload()},
            format="multipart",
        )
        self.assertIn(response.status_code, (401, 403))

    def test_student_and_organizer_uploads_are_forbidden(self):
        for user in (self.student, self.organizer):
            with self.subTest(user=user.email):
                self.client.force_authenticate(user)
                response = self.client.post(
                    self.dry_run_url,
                    {"file": workbook_upload()},
                    format="multipart",
                )
                self.assertEqual(response.status_code, 403)

    def test_admin_can_create_dry_run_job_without_writing_universities(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.dry_run_url,
            {"file": workbook_upload()},
            format="multipart",
        )

        self.assertEqual(response.status_code, 202, response.data)
        self.assertEqual(response.data["status"], UniversityImportJob.Status.COMPLETED)
        self.assertEqual(response.data["mode"], UniversityImportJob.Mode.DRY_RUN)
        self.assertEqual(response.data["row_count"], 1)
        self.assertEqual(response.data["created_count"], 1)
        self.assertEqual(response.data["source_url_count"], 1)
        self.assertEqual(response.data["field_verification_count"], 11)
        self.assertEqual(University.objects.count(), 0)

    def test_invalid_file_extension_is_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.dry_run_url,
            {"file": SimpleUploadedFile("universities.csv", b"name,country\n")},
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(UniversityImportJob.objects.count(), 0)

    def test_execute_writes_and_job_detail_returns_summary(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            self.execute_url,
            {"file": workbook_upload()},
            format="multipart",
        )

        self.assertEqual(response.status_code, 202, response.data)
        self.assertEqual(response.data["status"], UniversityImportJob.Status.COMPLETED)
        self.assertEqual(response.data["created_count"], 1)
        self.assertEqual(University.objects.filter(slug="admin-import-university").count(), 1)

        detail = self.client.get(
            reverse("university-import:job-detail", kwargs={"pk": response.data["id"]})
        )
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["summary_json"]["summary"]["created"], 1)

    def test_duplicate_execute_does_not_create_duplicate_universities(self):
        self.client.force_authenticate(self.admin)

        first = self.client.post(
            self.execute_url,
            {"file": workbook_upload()},
            format="multipart",
        )
        second = self.client.post(
            self.execute_url,
            {"file": workbook_upload()},
            format="multipart",
        )

        self.assertEqual(first.status_code, 202, first.data)
        self.assertEqual(second.status_code, 202, second.data)
        self.assertEqual(University.objects.filter(slug="admin-import-university").count(), 1)
        self.assertEqual(second.data["created_count"], 0)
        self.assertEqual(second.data["updated_count"], 1)

    def test_failed_import_records_error_on_job(self):
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.dry_run_url,
            {"file": SimpleUploadedFile("broken.xlsx", b"not an xlsx")},
            format="multipart",
        )

        self.assertEqual(response.status_code, 202, response.data)
        self.assertEqual(response.data["status"], UniversityImportJob.Status.FAILED)
        self.assertTrue(response.data["error_message"])
        self.assertEqual(University.objects.count(), 0)
