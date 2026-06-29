from datetime import date
from decimal import Decimal

from django.test import TestCase

from services.university_service import xlsx_import
from services.university_service.models import (
    University,
    UniversityFieldVerification,
)
from services.university_service.xlsx_import import import_rows, parse_date

HEADERS = xlsx_import.EXPECTED_HEADERS


def make_row(**overrides) -> dict:
    row = {header: "" for header in HEADERS}
    row.update(
        {
            "Name": "Example University",
            "Country": "USA",
            "City": "Boston, MA",
            "Official Website": "https://example.edu",
            "Admissions URL": "https://admissions.example.edu",
            "Majors": "Computer Science, Economics, Physics",
            "Deadlines": "Early Action (EA): Nov 1, 2024\nRegular Decision (RD): Jan 1, 2025",
            "SAT 25th": 1400,
            "SAT 50th": 1480,
            "SAT 75th": 1540,
            "IELTS Minimum": 7.0,
            "IELTS Competitive": 7.5,
            "Average GPA": 3.9,
            "Acceptance Rate": 0.15,
            "Tuition": 55000,
            "Scholarships": "Need-based aid; merit scholarship for top applicants",
            "AP Recommendations by Major": "CS: AP Calc BC, AP CS A",
            "Application Requirements": "Common App; transcript; 2 recommendations",
            "Essays": "Common App essay (650 words) + 2 supplements (250 words each)",
            "Financial Aid": "International students eligible for need-based aid.",
            "Source URLs": "https://example.edu/apply\nhttps://example.edu/facts",
            "Last Verified Date": "2024-10-01",
        }
    )
    row.update(overrides)
    return row


class XlsxImportTests(TestCase):
    def test_valid_row_imports_with_parsed_fields(self):
        report = import_rows([make_row()])
        self.assertEqual(report.created, 1)
        uni = University.objects.get(slug="example-university")
        self.assertEqual(uni.sat_p25, 1400)
        self.assertEqual(uni.sat_average, 1480)
        self.assertEqual(uni.sat_p75, 1540)
        self.assertEqual(uni.gpa_average, Decimal("3.90"))
        self.assertEqual(uni.ielts_minimum, Decimal("7.0"))
        self.assertEqual(uni.ielts_competitive, Decimal("7.5"))
        self.assertEqual(uni.application_deadline, date(2025, 1, 1))  # RD chosen
        self.assertTrue(uni.is_published)
        self.assertFalse(uni.is_demo)
        self.assertEqual(uni.programs.count(), 3)

    def test_acceptance_rate_decimal_fraction(self):
        import_rows([make_row(**{"Acceptance Rate": 0.038})])
        uni = University.objects.get(slug="example-university")
        self.assertEqual(uni.acceptance_rate, Decimal("3.80"))

    def test_acceptance_rate_percent_string(self):
        import_rows([make_row(**{"Acceptance Rate": "28.0%"})])
        uni = University.objects.get(slug="example-university")
        self.assertEqual(uni.acceptance_rate, Decimal("28.00"))

    def test_tuition_string_with_symbol_and_commas(self):
        import_rows([make_row(**{"Tuition": "$59,750"})])
        uni = University.objects.get(slug="example-university")
        self.assertEqual(uni.tuition_amount, Decimal("59750.00"))
        self.assertEqual(uni.tuition_currency, "USD")

    def test_excel_serial_date_parsing(self):
        serial = (date(2024, 10, 1) - date(1899, 12, 30)).days
        parsed, warning = parse_date(str(serial))
        self.assertEqual(parsed, date(2024, 10, 1))
        self.assertIsNone(warning)

    def test_sat_placeholder_detection_drops_values(self):
        report = import_rows(
            [make_row(**{"SAT 25th": 550, "SAT 50th": 550, "SAT 75th": 550})]
        )
        uni = University.objects.get(slug="example-university")
        self.assertIsNone(uni.sat_p25)
        self.assertIsNone(uni.sat_average)
        self.assertIsNone(uni.sat_p75)
        self.assertEqual(report.placeholder_sat, 1)
        self.assertIn("placeholder", uni.data_quality_notes.lower())

    def test_sat_placeholder_kept_when_flag_set(self):
        import_rows(
            [make_row(**{"SAT 25th": 550, "SAT 50th": 550, "SAT 75th": 550})],
            include_questionable=True,
        )
        uni = University.objects.get(slug="example-university")
        self.assertEqual(uni.sat_average, 550)
        verification = uni.field_verifications.filter(field_name="sat_average").first()
        self.assertIsNotNone(verification)
        self.assertEqual(verification.status, "estimated")

    def test_multiline_sources_create_records(self):
        import_rows([make_row()])
        uni = University.objects.get(slug="example-university")
        self.assertEqual(uni.data_sources.count(), 2)

    def test_raw_deadline_and_essay_preserved(self):
        import_rows([make_row()])
        uni = University.objects.get(slug="example-university")
        self.assertIn("Early Action", uni.deadlines_text)
        self.assertIn("650 words", uni.essay_requirements)

    def test_source_verification_created(self):
        import_rows([make_row()])
        uni = University.objects.get(slug="example-university")
        verification = uni.field_verifications.filter(field_name="acceptance_rate").first()
        self.assertIsNotNone(verification)
        self.assertEqual(verification.status, "partial")
        self.assertEqual(verification.source_url, "https://example.edu/apply")
        self.assertEqual(verification.last_verified_date, date(2024, 10, 1))

    def test_no_source_means_no_verification(self):
        import_rows([make_row(**{"Source URLs": ""})])
        uni = University.objects.get(slug="example-university")
        self.assertEqual(uni.field_verifications.count(), 0)
        self.assertIn("unverified", uni.data_quality_notes.lower())

    def test_textual_gpa_stored_as_note_not_float(self):
        report = import_rows([make_row(**{"Average GPA": "AAA A-Levels"})])
        uni = University.objects.get(slug="example-university")
        self.assertIsNone(uni.gpa_average)
        self.assertIn("AAA A-Levels", uni.data_quality_notes)
        self.assertEqual(report.created, 1)

    def test_repeated_import_is_idempotent(self):
        import_rows([make_row()])
        import_rows([make_row()])
        self.assertEqual(University.objects.filter(slug="example-university").count(), 1)
        uni = University.objects.get(slug="example-university")
        # Related records are not duplicated on re-run.
        self.assertEqual(uni.programs.count(), 3)
        self.assertEqual(uni.data_sources.count(), 2)

    def test_parenthetical_name_matches_clean_slug(self):
        # A curated row exists with the clean slug; importing "(MIT)" must upsert it.
        University.objects.create(
            name="Massachusetts Institute of Technology",
            slug="massachusetts-institute-of-technology",
            official_website="https://web.mit.edu",
            is_published=True,
        )
        report = import_rows(
            [make_row(Name="Massachusetts Institute of Technology (MIT)")]
        )
        self.assertEqual(report.updated, 1)
        self.assertEqual(
            University.objects.filter(
                slug="massachusetts-institute-of-technology"
            ).count(),
            1,
        )

    def test_curated_verification_preserved_without_replace(self):
        uni = University.objects.create(
            name="Example University",
            slug="example-university",
            official_website="https://example.edu",
            is_published=True,
        )
        UniversityFieldVerification.objects.create(
            university=uni,
            field_name="acceptance_rate",
            status="verified",
            source_url="https://example.edu/curated",
            last_verified_date=date(2023, 1, 1),
        )
        import_rows([make_row()])
        verification = uni.field_verifications.get(field_name="acceptance_rate")
        # Curated "verified" row is preserved, not downgraded to "partial".
        self.assertEqual(verification.status, "verified")
        self.assertEqual(verification.source_url, "https://example.edu/curated")

    def test_row_without_name_is_ignored(self):
        report = import_rows([make_row(Name="")])
        self.assertEqual(report.created, 0)
        self.assertEqual(University.objects.count(), 0)

    def test_row_without_website_is_skipped(self):
        report = import_rows([make_row(**{"Official Website": "", "Admissions URL": ""})])
        self.assertEqual(report.skipped, 1)
        self.assertEqual(University.objects.count(), 0)
