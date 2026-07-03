from __future__ import annotations

from .currency import normalize_amount_to_usd, normalize_university_costs

STATUS_WITHIN_BUDGET = "within_budget"
STATUS_ABOVE_BUDGET = "above_budget"
STATUS_NEEDS_AID = "needs_aid"
STATUS_UNKNOWN_BUDGET = "unknown_budget"
STATUS_COST_UNAVAILABLE = "cost_unavailable"


def compare_cost_to_budget(university, profile) -> dict:
    """Compare a university's known USD cost against the student's entered
    budget. Only ever compares when both a verified/converted cost and a
    budget amount are available — otherwise reports why comparison isn't
    possible instead of guessing.
    """

    normalize_university_costs(university)
    cost_usd = university.total_cost_usd_amount or university.tuition_usd_amount
    cost_confidence = university.currency_conversion_confidence or None

    budget_amount = getattr(profile, "annual_budget_amount", None)
    if budget_amount is None:
        return {
            "status": STATUS_UNKNOWN_BUDGET,
            "cost_usd": cost_usd,
            "cost_confidence": cost_confidence,
            "budget_usd": None,
        }

    budget_currency = getattr(profile, "annual_budget_currency", "") or "USD"
    budget_usd, _rate, _status = normalize_amount_to_usd(budget_amount, budget_currency)
    if budget_usd is None:
        # Budget was entered but couldn't be converted (e.g. no exchange rate
        # on file yet) — this is still "unknown", never a guessed comparison.
        return {
            "status": STATUS_UNKNOWN_BUDGET,
            "cost_usd": cost_usd,
            "cost_confidence": cost_confidence,
            "budget_usd": None,
        }

    if cost_usd is None:
        return {
            "status": STATUS_COST_UNAVAILABLE,
            "cost_usd": None,
            "cost_confidence": cost_confidence,
            "budget_usd": budget_usd,
        }

    needs_aid_signal = profile.scholarship_need == profile.ScholarshipNeed.YES
    if cost_usd <= budget_usd:
        status = STATUS_WITHIN_BUDGET
    elif needs_aid_signal:
        status = STATUS_NEEDS_AID
    else:
        status = STATUS_ABOVE_BUDGET

    return {
        "status": status,
        "cost_usd": cost_usd,
        "cost_confidence": cost_confidence,
        "budget_usd": budget_usd,
    }
