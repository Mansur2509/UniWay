from datetime import date

from django.db import migrations, models

DATASET_RECORDED_ON = date(2026, 7, 1)
SAT_SOURCE_URL = "https://satsuite.collegeboard.org/sat/dates-deadlines"
AP_DATES_SOURCE_URL = (
    "https://apcentral.collegeboard.org/exam-administration-ordering-scores/exam-dates"
)
AP_ORDER_SOURCE_URL = (
    "https://apcentral.collegeboard.org/exam-administration-ordering-scores/"
    "ordering-fees/ordering-deadlines"
)
PARTIAL_NOTE = (
    "Founder-provided 2026 dataset; verify exact current details with the official "
    "College Board page before booking. Marked partial until exact official URL "
    "verification is completed."
)
AP_INTERNATIONAL_NOTE = (
    " International students, including Uzbekistan students, must verify local "
    "availability, fees, payment rules, and collection deadlines with an authorized "
    "AP test center."
)

SAT_DATES = [
    ("March SAT 2026", date(2026, 3, 14), date(2026, 2, 27), date(2026, 3, 3)),
    ("May SAT 2026", date(2026, 5, 2), date(2026, 4, 17), date(2026, 4, 21)),
    ("June SAT 2026", date(2026, 6, 6), date(2026, 5, 22), date(2026, 5, 26)),
    ("August SAT 2026", date(2026, 8, 22), date(2026, 8, 7), date(2026, 8, 11)),
    ("September SAT 2026", date(2026, 9, 12), date(2026, 8, 28), date(2026, 9, 1)),
    ("October SAT 2026", date(2026, 10, 3), date(2026, 9, 18), date(2026, 9, 22)),
    ("November SAT 2026", date(2026, 11, 7), date(2026, 10, 23), date(2026, 10, 27)),
    ("December SAT 2026", date(2026, 12, 5), date(2026, 11, 20), date(2026, 11, 24)),
]

AP_ORDERING_EVENTS = [
    (
        "AP preferred ordering deadline",
        "ordering_deadline",
        date(2025, 10, 3),
        "",
        "Preferred ordering deadline for AP 2026 exams.",
    ),
    (
        "AP final ordering deadline",
        "ordering_deadline",
        date(2025, 11, 14),
        "11:59 p.m. ET",
        "Final ordering deadline for AP 2026 exams.",
    ),
    (
        "AP late order fee period begins",
        "ordering_deadline",
        date(2025, 11, 15),
        "",
        "Late order fee period begins; provided dataset lists an extra $40 per exam.",
    ),
    (
        "AP spring orders and fall-order changes deadline",
        "ordering_deadline",
        date(2026, 3, 13),
        "11:59 p.m. ET",
        "Spring orders and fall-order changes deadline for AP 2026 exams.",
    ),
]

AP_EXAM_DATES = [
    ("AP African American Studies", date(2026, 5, 7), "12 p.m. local time", date(2026, 5, 19), "12 p.m. local time"),
    ("AP Art History", date(2026, 5, 14), "8 a.m. local time", date(2026, 5, 21), "12 p.m. local time"),
    ("AP Biology", date(2026, 5, 4), "8 a.m. local time", date(2026, 5, 20), "12 p.m. local time"),
    ("AP Calculus AB", date(2026, 5, 11), "8 a.m. local time", date(2026, 5, 21), "12 p.m. local time"),
    ("AP Calculus BC", date(2026, 5, 11), "8 a.m. local time", date(2026, 5, 21), "12 p.m. local time"),
    ("AP Chemistry", date(2026, 5, 5), "8 a.m. local time", date(2026, 5, 20), "12 p.m. local time"),
    ("AP Chinese Language and Culture", date(2026, 5, 8), "12 p.m. local time", date(2026, 5, 21), "8 a.m. local time"),
    ("AP Comparative Government and Politics", date(2026, 5, 6), "12 p.m. local time", date(2026, 5, 18), "8 a.m. local time"),
    ("AP Computer Science A", date(2026, 5, 15), "12 p.m. local time", date(2026, 5, 22), "12 p.m. local time"),
    ("AP Computer Science Principles", date(2026, 5, 14), "12 p.m. local time", date(2026, 5, 21), "8 a.m. local time"),
    ("AP English Language and Composition", date(2026, 5, 13), "8 a.m. local time", date(2026, 5, 21), "8 a.m. local time"),
    ("AP English Literature and Composition", date(2026, 5, 6), "8 a.m. local time", date(2026, 5, 18), "12 p.m. local time"),
    ("AP Environmental Science", date(2026, 5, 15), "8 a.m. local time", date(2026, 5, 22), "8 a.m. local time"),
    ("AP European History", date(2026, 5, 4), "12 p.m. local time", date(2026, 5, 18), "8 a.m. local time"),
    ("AP French Language and Culture", date(2026, 5, 12), "8 a.m. local time", date(2026, 5, 20), "12 p.m. local time"),
    ("AP German Language and Culture", date(2026, 5, 13), "8 a.m. local time", date(2026, 5, 22), "12 p.m. local time"),
    ("AP Human Geography", date(2026, 5, 5), "8 a.m. local time", date(2026, 5, 18), "12 p.m. local time"),
    ("AP Italian Language and Culture", date(2026, 5, 8), "8 a.m. local time", date(2026, 5, 21), "12 p.m. local time"),
    ("AP Japanese Language and Culture", date(2026, 5, 12), "12 p.m. local time", date(2026, 5, 19), "8 a.m. local time"),
    ("AP Latin", date(2026, 5, 4), "8 a.m. local time", date(2026, 5, 18), "12 p.m. local time"),
    ("AP Macroeconomics", date(2026, 5, 8), "12 p.m. local time", date(2026, 5, 20), "12 p.m. local time"),
    ("AP Microeconomics", date(2026, 5, 4), "12 p.m. local time", date(2026, 5, 20), "8 a.m. local time"),
    ("AP Music Theory", date(2026, 5, 11), "12 p.m. local time", date(2026, 5, 21), "8 a.m. local time"),
    ("AP Physics 1: Algebra-Based", date(2026, 5, 6), "12 p.m. local time", date(2026, 5, 22), "8 a.m. local time"),
    ("AP Physics 2: Algebra-Based", date(2026, 5, 7), "8 a.m. local time", date(2026, 5, 21), "12 p.m. local time"),
    ("AP Physics C: Mechanics", date(2026, 5, 13), "12 p.m. local time", date(2026, 5, 21), "12 p.m. local time"),
    ("AP Physics C: Electricity and Magnetism", date(2026, 5, 14), "12 p.m. local time", date(2026, 5, 22), "12 p.m. local time"),
    ("AP Precalculus", date(2026, 5, 12), "8 a.m. local time", date(2026, 5, 21), "8 a.m. local time"),
    ("AP Psychology", date(2026, 5, 12), "12 p.m. local time", date(2026, 5, 22), "12 p.m. local time"),
    ("AP Seminar", date(2026, 5, 11), "12 p.m. local time", date(2026, 5, 20), "8 a.m. local time"),
    ("AP Spanish Language and Culture", date(2026, 5, 14), "8 a.m. local time", date(2026, 5, 22), "8 a.m. local time"),
    ("AP Spanish Literature and Culture", date(2026, 5, 13), "12 p.m. local time", date(2026, 5, 22), "8 a.m. local time"),
    ("AP Statistics", date(2026, 5, 7), "12 p.m. local time", date(2026, 5, 20), "8 a.m. local time"),
    ("AP United States Government and Politics", date(2026, 5, 5), "12 p.m. local time", date(2026, 5, 19), "8 a.m. local time"),
    ("AP United States History", date(2026, 5, 8), "8 a.m. local time", date(2026, 5, 19), "12 p.m. local time"),
    ("AP World History: Modern", date(2026, 5, 7), "8 a.m. local time", date(2026, 5, 18), "8 a.m. local time"),
]

AP_PERFORMANCE_EVENTS = [
    ("AP Seminar performance tasks", "performance_task", date(2026, 4, 30), "11:59 p.m. ET"),
    ("AP Research performance tasks", "performance_task", date(2026, 4, 30), "11:59 p.m. ET"),
    ("AP Computer Science Principles Create task", "performance_task", date(2026, 4, 30), "11:59 p.m. ET"),
    ("AP Art and Design portfolio", "portfolio_deadline", date(2026, 5, 8), "8 p.m. ET"),
]


def _upsert_exam_date(OfficialExamDate, payload):
    lookup = {
        "exam_type": payload["exam_type"],
        "name": payload["name"],
        "academic_year": payload["academic_year"],
        "event_kind": payload["event_kind"],
    }
    defaults = {key: value for key, value in payload.items() if key not in lookup}
    OfficialExamDate.objects.update_or_create(**lookup, defaults=defaults)


def seed_exam_dates(apps, schema_editor):
    OfficialExamDate = apps.get_model("exam_content_service", "OfficialExamDate")
    for name, test_date, registration_deadline, late_deadline in SAT_DATES:
        _upsert_exam_date(
            OfficialExamDate,
            {
                "exam_type": "SAT",
                "event_kind": "exam",
                "name": name,
                "test_date": test_date,
                "test_time": "",
                "registration_deadline": registration_deadline,
                "late_registration_deadline": late_deadline,
                "late_test_date": None,
                "late_test_time": "",
                "score_release_window": "",
                "academic_year": "2026-2027",
                "region": "International",
                "source_url": SAT_SOURCE_URL,
                "last_verified_date": DATASET_RECORDED_ON,
                "verification_status": "partial",
                "notes": PARTIAL_NOTE,
            },
        )

    for name, event_kind, test_date, test_time, note in AP_ORDERING_EVENTS:
        _upsert_exam_date(
            OfficialExamDate,
            {
                "exam_type": "AP",
                "event_kind": event_kind,
                "name": name,
                "test_date": test_date,
                "test_time": test_time,
                "registration_deadline": None,
                "late_registration_deadline": None,
                "late_test_date": None,
                "late_test_time": "",
                "score_release_window": "",
                "academic_year": "2025-2026",
                "region": "International",
                "source_url": AP_ORDER_SOURCE_URL,
                "last_verified_date": DATASET_RECORDED_ON,
                "verification_status": "partial",
                "notes": f"{PARTIAL_NOTE} {note}{AP_INTERNATIONAL_NOTE}",
            },
        )

    for name, test_date, test_time, late_date, late_time in AP_EXAM_DATES:
        _upsert_exam_date(
            OfficialExamDate,
            {
                "exam_type": "AP",
                "event_kind": "exam",
                "name": name,
                "test_date": test_date,
                "test_time": test_time,
                "registration_deadline": date(2026, 3, 13),
                "late_registration_deadline": date(2026, 3, 13),
                "late_test_date": late_date,
                "late_test_time": late_time,
                "score_release_window": "",
                "academic_year": "2025-2026",
                "region": "International",
                "source_url": AP_DATES_SOURCE_URL,
                "last_verified_date": DATASET_RECORDED_ON,
                "verification_status": "partial",
                "notes": (
                    f"{PARTIAL_NOTE} Regular AP exams run May 4-8 and May 11-15, "
                    f"2026; late testing runs May 18-22, 2026. Early testing is not allowed."
                    f"{AP_INTERNATIONAL_NOTE}"
                ),
            },
        )

    for name, event_kind, test_date, test_time in AP_PERFORMANCE_EVENTS:
        _upsert_exam_date(
            OfficialExamDate,
            {
                "exam_type": "AP",
                "event_kind": event_kind,
                "name": name,
                "test_date": test_date,
                "test_time": test_time,
                "registration_deadline": None,
                "late_registration_deadline": None,
                "late_test_date": None,
                "late_test_time": "",
                "score_release_window": "",
                "academic_year": "2025-2026",
                "region": "International",
                "source_url": AP_DATES_SOURCE_URL,
                "last_verified_date": DATASET_RECORDED_ON,
                "verification_status": "partial",
                "notes": f"{PARTIAL_NOTE}{AP_INTERNATIONAL_NOTE}",
            },
        )


def remove_seed_exam_dates(apps, schema_editor):
    OfficialExamDate = apps.get_model("exam_content_service", "OfficialExamDate")
    OfficialExamDate.objects.filter(notes__contains="Founder-provided 2026 dataset").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("exam_content_service", "0002_officialexamdate"),
    ]

    operations = [
        migrations.AddField(
            model_name="officialexamdate",
            name="event_kind",
            field=models.CharField(
                choices=[
                    ("exam", "Exam"),
                    ("ordering_deadline", "Ordering deadline"),
                    ("performance_task", "Performance task"),
                    ("portfolio_deadline", "Portfolio deadline"),
                ],
                db_index=True,
                default="exam",
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name="officialexamdate",
            name="test_time",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddField(
            model_name="officialexamdate",
            name="late_test_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="officialexamdate",
            name="late_test_time",
            field=models.CharField(blank=True, max_length=40),
        ),
        migrations.AddIndex(
            model_name="officialexamdate",
            index=models.Index(
                fields=["exam_type", "event_kind", "test_date"],
                name="exam_conten_exam_ty_f10e58_idx",
            ),
        ),
        migrations.RunPython(seed_exam_dates, remove_seed_exam_dates),
    ]
