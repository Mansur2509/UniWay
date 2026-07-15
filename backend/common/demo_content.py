"""Shared definition of the canonical public demo student's sample content.

Separate from `demo_accounts.py` (which owns the account itself: email,
password, role, profile). This module owns the demo student's sample
essay + application, which have historically drifted because they were
created ad hoc through interactive testing rather than seeded deliberately.
`ensure_demo_content` (the management command) restores them to a fixed,
clearly-fictional, safe state and is idempotent.
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from common.demo_accounts import CANONICAL_STUDENT_DEMO_EMAIL

DEMO_UNIVERSITY_SLUG = "lakeview-institute-of-technology"
DEMO_UNIVERSITY_DEFAULTS = {
    "name": "Lakeview Institute of Technology",
    "country": "Demoland",
    "city": "Lakeview",
    "official_website": f"https://example.com/{DEMO_UNIVERSITY_SLUG}",
    "summary": (
        "Fictional development record used to demonstrate a fully populated "
        "university profile. Not a real institution."
    ),
    "acceptance_rate": "18.00",
    "gpa_average": "3.70",
    "sat_average": 1420,
    "tuition_amount": "42000.00",
    "tuition_currency": "USD",
    "scholarship_available": True,
    "is_published": True,
    "is_demo": True,
}

DEMO_PROGRAM_NAME = "Computer Science"
DEMO_PROGRAM_DEFAULTS = {
    "degree_level": "Bachelor",
    "official_url": f"https://example.com/{DEMO_UNIVERSITY_SLUG}/computer-science",
}

# Stable natural key for the demo essay -- not a suggestion-engine key, so
# matched by (user, title) instead of the suggestion_key uniqueness path.
DEMO_ESSAY_TITLE = "Sample Scholarship Essay (Demo)"

# Entirely fictional persona and scenario. No real person's story, no copied
# admission essay, no identifying details. Deliberately imperfect (some
# repetition, a plain closing line) so Essay AI feedback stays meaningful and
# this never reads as a polished, ready-to-submit essay.
DEMO_ESSAY_DRAFT_TEXT = """When I was thirteen, our neighborhood library started closing on weekends because the city cut its budget, and the after-school reading program my younger cousins depended on disappeared with it. I did not know anything about software then, but I knew the schedule spreadsheet the volunteers used was a mess: three different people kept three different versions, and nobody could tell which room was actually free on a given afternoon.

I asked my computer science teacher if there was a simple way to fix this, and she pointed me toward a free spreadsheet scripting guide. Over the next two months I built a small shared calendar tool, nothing sophisticated, that let the four remaining volunteers see the same schedule and book a room without double-booking it. It broke twice in the first week. I had never debugged anything under real pressure before, and I remember the exact feeling of opening the script at eleven at night trying to figure out why Saturday's session had vanished from everyone's view except mine.

That small, imperfect tool is the reason I want to study computer science at Lakeview. Not because I think code is glamorous, but because that spreadsheet taught me that most real problems are not solved by the cleverest algorithm, they are solved by paying attention to the people who are actually stuck, and building something boring and reliable enough that they can stop thinking about the tool and go back to focusing on the kids in the reading program. I think about that distinction a lot: impressive software versus useful software.

I am drawn to Lakeview's computer science program specifically because of its project-based first-year sequence, which seems to treat real deployment and real users as part of the coursework rather than an afterthought bolted onto a theory class. I want to keep building tools for small, under-resourced organizations, but I know I am still early. I have only worked on one real project outside of class assignments, and I have a lot to learn about testing, security, and writing code that other people besides me can maintain.

I am applying for the scholarship because my family's ability to cover tuition is genuinely uncertain year to year, and because I want to spend my undergraduate summers on more projects like the library scheduler rather than on unrelated paid work purely to cover costs. I do not have a dramatic turning-point story. I have a spreadsheet that broke on a Saturday night, and the stubbornness to keep fixing it."""

DEMO_ESSAY_FIELDS = {
    "essay_type": "scholarship",
    "prompt_text": (
        "Describe a challenge you have faced and how it shaped your academic "
        "and personal goals. (Fictional demonstration prompt.)"
    ),
    "word_limit": 650,
    "draft_text": DEMO_ESSAY_DRAFT_TEXT,
    "status": "needs_revision",
    "priority": "medium",
    "prompt_verification_status": "needs_verification",
    "prompt_confidence": "low",
}

DEMO_APPLICATION_FIELDS = {
    "application_round": "scholarship",
    "status": "shortlisted",
    "priority": "high",
    "essays_status": "needs_revision",
}


def _ensure_demo_university(university_model, program_model):
    """Get-or-create the dedicated demo showcase university/program.

    Uses get_or_create (not update_or_create): if `seed_demo --with-demo-data`
    already created this exact record, it is left untouched rather than
    fought over by two commands; if it does not exist yet (e.g. production,
    which never runs --with-demo-data), it is created here so this command
    never depends on university import or on seed_demo having run first.
    """
    university, _ = university_model.objects.get_or_create(
        slug=DEMO_UNIVERSITY_SLUG,
        defaults=DEMO_UNIVERSITY_DEFAULTS,
    )
    program_model.objects.get_or_create(
        university=university,
        name=DEMO_PROGRAM_NAME,
        defaults=DEMO_PROGRAM_DEFAULTS,
    )
    return university


def _ensure_demo_application(application_model, user, university):
    deadline = (timezone.now() + timedelta(days=150)).date()
    application, created = application_model.objects.update_or_create(
        user=user,
        university=university,
        archived_at=None,
        defaults={**DEMO_APPLICATION_FIELDS, "deadline": deadline},
    )
    return application, created


def _ensure_demo_essay(essay_model, feedback_model, revision_task_model, score_report_model, user, university, application):
    """Restore the canonical demo essay. Only ever touches an essay that
    already belongs to `user` (matched by FK, never by email similarity).

    Converges draft_text/status/etc. to the fixed canonical values every
    run ("restore"); if the text actually changed, clears stale AI feedback/
    scores/revision tasks tied to the *previous* draft so nothing displays
    mismatched history against the new content.
    """
    existing = essay_model.objects.filter(user=user, title=DEMO_ESSAY_TITLE).first()
    previous_draft_text = existing.draft_text if existing is not None else None

    essay, created = essay_model.objects.update_or_create(
        user=user,
        title=DEMO_ESSAY_TITLE,
        defaults={
            **DEMO_ESSAY_FIELDS,
            "university": university,
            "application": application,
        },
    )

    content_changed = (not created) and previous_draft_text != essay.draft_text
    if created or content_changed:
        feedback_model.objects.filter(essay=essay).delete()
        revision_task_model.objects.filter(essay=essay).delete()
        score_report_model.objects.filter(essay=essay).delete()

    return essay, created, content_changed


def ensure_canonical_demo_content(user_model, university_model, program_model, application_model, essay_model, feedback_model, revision_task_model, score_report_model) -> dict[str, object]:
    """Idempotently restore the canonical demo student's sample essay and
    application. Never creates the account itself (see `demo_accounts.py` /
    `ensure_demo_accounts`) -- raises if the canonical account does not exist
    yet, since account provisioning must run first.

    Returns a status report (no credentials, no essay text, no feedback).
    """
    user = user_model.objects.filter(email__iexact=CANONICAL_STUDENT_DEMO_EMAIL).first()
    if user is None:
        raise LookupError(
            f"Canonical demo account ({CANONICAL_STUDENT_DEMO_EMAIL}) does not exist. "
            "Run ensure_demo_accounts first."
        )

    university = _ensure_demo_university(university_model, program_model)
    application, application_created = _ensure_demo_application(application_model, user, university)
    essay, essay_created, content_restored = _ensure_demo_essay(
        essay_model, feedback_model, revision_task_model, score_report_model, user, university, application
    )

    return {
        "email": user.email,
        "university_slug": university.slug,
        "application_action": "created" if application_created else "already_present",
        "essay_action": "created" if essay_created else ("restored" if content_restored else "already_present"),
    }
