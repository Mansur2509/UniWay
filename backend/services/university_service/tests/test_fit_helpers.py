from django.test import SimpleTestCase

from services.university_service.services import (
    best_sat_score,
    ielts_gap_severity,
    normalize_gpa_to_4,
    sat_gap_severity,
)


class NormalizeGpaTests(SimpleTestCase):
    def test_returns_none_when_gpa_missing(self):
        self.assertIsNone(normalize_gpa_to_4(None, "4.00"))

    def test_returns_none_when_scale_missing(self):
        self.assertIsNone(normalize_gpa_to_4("3.50", None))

    def test_returns_none_when_scale_is_zero(self):
        self.assertIsNone(normalize_gpa_to_4("3.50", "0"))

    def test_normalizes_to_4_scale(self):
        self.assertAlmostEqual(normalize_gpa_to_4("4.50", "5.00"), 3.6)

    def test_returns_same_value_when_already_on_4_scale(self):
        self.assertAlmostEqual(normalize_gpa_to_4("3.80", "4.00"), 3.8)

    def test_normalizes_with_clean_decimal_result(self):
        # 4.50 / 5.00 * 4.0 == 3.6 exactly in decimal arithmetic; float division can
        # land at 3.5999999999999996, so callers must round before threshold checks.
        self.assertEqual(round(normalize_gpa_to_4("4.50", "5.00"), 4), 3.6)


class BestSatScoreTests(SimpleTestCase):
    def test_returns_none_for_missing_key(self):
        self.assertIsNone(best_sat_score({}))

    def test_returns_none_for_non_dict(self):
        self.assertIsNone(best_sat_score(None))

    def test_reads_lowercase_key(self):
        self.assertEqual(best_sat_score({"sat": 1450}), 1450)

    def test_reads_uppercase_key(self):
        self.assertEqual(best_sat_score({"SAT": 1500}), 1500)

    def test_returns_none_for_non_numeric_value(self):
        self.assertIsNone(best_sat_score({"sat": "not-a-number"}))


class GapSeverityTests(SimpleTestCase):
    def test_ielts_severity_never_marks_below_threshold_on_track(self):
        self.assertEqual(ielts_gap_severity(6.0, 6.5), "near_target")
        self.assertEqual(ielts_gap_severity(6.0, 7.0), "moderate_gap")
        self.assertEqual(ielts_gap_severity(6.5, 6.5), "on_track")
        self.assertEqual(ielts_gap_severity(6.5, 7.0), "near_target")
        self.assertEqual(ielts_gap_severity(7.0, 7.0), "on_track")

    def test_sat_severity_distinguishes_small_and_large_gaps(self):
        self.assertEqual(sat_gap_severity(1460, 1510), "near_target")
        self.assertEqual(sat_gap_severity(1410, 1510), "moderate_gap")
        self.assertEqual(sat_gap_severity(1360, 1510), "substantial_gap")
        self.assertEqual(sat_gap_severity(1220, 1510), "significant_gap")
