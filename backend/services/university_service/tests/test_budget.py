from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from services.university_service.budget import (
    STATUS_ABOVE_BUDGET,
    STATUS_COST_UNAVAILABLE,
    STATUS_NEEDS_AID,
    STATUS_UNKNOWN_BUDGET,
    STATUS_WITHIN_BUDGET,
    compare_cost_to_budget,
)
from services.university_service.models import ExchangeRate
from services.university_service.tests.test_universities import create_university
from services.user_profile_service.services import ensure_profile_records

User = get_user_model()


class BudgetComparisonTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="budgetstudent", email="budgetstudent@test.com", password="testpass123"
        )
        self.profile, _ = ensure_profile_records(self.user)

    def test_missing_budget_reports_unknown_budget(self):
        university = create_university("no-budget-entered", tuition_usd_amount=Decimal("30000"))
        result = compare_cost_to_budget(university, self.profile)
        self.assertEqual(result["status"], STATUS_UNKNOWN_BUDGET)

    def test_missing_currency_does_not_crash(self):
        self.profile.annual_budget_amount = Decimal("20000")
        self.profile.annual_budget_currency = ""
        self.profile.save()
        university = create_university(
            "missing-currency-university",
            tuition_original_amount=Decimal("15000"),
            tuition_original_currency="",
            tuition_currency="",
        )
        result = compare_cost_to_budget(university, self.profile)
        # Empty currency means the cost can't be converted, so cost_usd stays
        # None rather than crashing or guessing a value.
        self.assertIsNone(result["cost_usd"])

    def test_missing_exchange_rate_does_not_crash(self):
        self.profile.annual_budget_amount = Decimal("20000")
        self.profile.annual_budget_currency = "USD"
        self.profile.save()
        university = create_university(
            "no-exchange-rate-university",
            tuition_original_amount=Decimal("15000"),
            tuition_original_currency="XYZ",
        )
        result = compare_cost_to_budget(university, self.profile)
        self.assertIsNone(result["cost_usd"])
        self.assertEqual(result["status"], STATUS_COST_UNAVAILABLE)

    def test_budget_comparison_only_runs_when_both_available(self):
        university = create_university("cost-unset-university")
        result = compare_cost_to_budget(university, self.profile)
        self.assertEqual(result["status"], STATUS_UNKNOWN_BUDGET)

        self.profile.annual_budget_amount = Decimal("10000")
        self.profile.annual_budget_currency = "USD"
        self.profile.save()
        result = compare_cost_to_budget(university, self.profile)
        self.assertEqual(result["status"], STATUS_COST_UNAVAILABLE)

    def test_within_budget_status(self):
        self.profile.annual_budget_amount = Decimal("40000")
        self.profile.annual_budget_currency = "USD"
        self.profile.save()
        university = create_university(
            "affordable-university",
            tuition_original_amount=Decimal("30000"),
            tuition_original_currency="USD",
        )
        result = compare_cost_to_budget(university, self.profile)
        self.assertEqual(result["status"], STATUS_WITHIN_BUDGET)

    def test_above_budget_status_without_aid_signal(self):
        self.profile.annual_budget_amount = Decimal("10000")
        self.profile.annual_budget_currency = "USD"
        self.profile.scholarship_need = self.profile.ScholarshipNeed.NO
        self.profile.save()
        university = create_university(
            "expensive-university",
            tuition_original_amount=Decimal("50000"),
            tuition_original_currency="USD",
        )
        result = compare_cost_to_budget(university, self.profile)
        self.assertEqual(result["status"], STATUS_ABOVE_BUDGET)

    def test_needs_aid_status_when_above_budget_and_aid_needed(self):
        self.profile.annual_budget_amount = Decimal("10000")
        self.profile.annual_budget_currency = "USD"
        self.profile.scholarship_need = self.profile.ScholarshipNeed.YES
        self.profile.save()
        university = create_university(
            "needs-aid-university",
            tuition_original_amount=Decimal("50000"),
            tuition_original_currency="USD",
        )
        result = compare_cost_to_budget(university, self.profile)
        self.assertEqual(result["status"], STATUS_NEEDS_AID)

    def test_budget_in_foreign_currency_converts_before_comparing(self):
        ExchangeRate.objects.create(
            currency_code="EUR",
            usd_rate=Decimal("1.10"),
            effective_date=date.today(),
            source="Test fixture rate",
            confidence="high",
        )
        self.profile.annual_budget_amount = Decimal("10000")
        self.profile.annual_budget_currency = "EUR"
        self.profile.save()
        university = create_university(
            "eur-budget-university",
            tuition_original_amount=Decimal("9000"),
            tuition_original_currency="USD",
        )
        # 10000 EUR -> 11000 USD, which comfortably covers 9000 USD tuition.
        result = compare_cost_to_budget(university, self.profile)
        self.assertEqual(result["status"], STATUS_WITHIN_BUDGET)
        self.assertEqual(result["budget_usd"], Decimal("11000.00"))

    def test_no_misleading_affordability_label_without_budget(self):
        university = create_university(
            "no-affordability-label-university",
            tuition_original_amount=Decimal("5000"),
            tuition_original_currency="USD",
        )
        result = compare_cost_to_budget(university, self.profile)
        self.assertNotIn(result["status"], {STATUS_WITHIN_BUDGET, STATUS_ABOVE_BUDGET, STATUS_NEEDS_AID})
