from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from services.user_profile_service.curriculum_rigor import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    calculate_curriculum_rigor,
    calculate_major_curriculum_fit,
)
from services.user_profile_service.services import ensure_profile_records

User = get_user_model()


class CurriculumRigorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rigorstudent", email="rigorstudent@test.com", password="testpass123"
        )
        self.profile, _ = ensure_profile_records(self.user)

    def test_unknown_curriculum_and_no_course_data_lowers_confidence(self):
        result = calculate_curriculum_rigor(self.profile)
        self.assertEqual(result.rigor_confidence, CONFIDENCE_LOW)
        self.assertIn("curriculum_type", result.missing_curriculum_data)
        self.assertIn("advanced_course_counts", result.missing_curriculum_data)

    def test_ap_heavy_profile_raises_rigor_score(self):
        baseline = calculate_curriculum_rigor(self.profile).rigor_score

        self.profile.curriculum_type = self.profile.CurriculumType.AP
        self.profile.ap_courses_count = 7
        self.profile.honors_courses_count = 4
        self.profile.course_rigor_level = self.profile.CourseRigorLevel.HIGHLY_ADVANCED
        self.profile.save()

        result = calculate_curriculum_rigor(self.profile)
        self.assertGreater(result.rigor_score, baseline)
        self.assertEqual(result.rigor_confidence, CONFIDENCE_HIGH)

    def test_no_fake_official_equivalency_language(self):
        self.profile.curriculum_type = self.profile.CurriculumType.A_LEVEL
        self.profile.a_level_subjects_count = 3
        self.profile.save()
        result = calculate_curriculum_rigor(self.profile)
        # The dataclass never claims one diploma is officially "worth more"
        # than another — only "context"/"signal" framing is used.
        for forbidden in ("worth more", "official equivalent", "guarantee"):
            self.assertNotIn(forbidden, result.curriculum_context.lower())

    def test_curriculum_affects_major_fit_only_as_context(self):
        self.profile.intended_major = "Computer Science"
        self.profile.ap_courses_count = 5
        self.profile.save()
        fit = calculate_major_curriculum_fit(self.profile, self.profile.intended_major)
        self.assertEqual(fit["preparation_signal"], "strong_context")
        self.assertIn("not an official equivalency", fit["note"])

    def test_unrecognized_program_returns_unknown_signal(self):
        fit = calculate_major_curriculum_fit(self.profile, "")
        self.assertEqual(fit["preparation_signal"], "unknown")
