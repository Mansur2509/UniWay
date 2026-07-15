from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from common.demo_content import DEMO_ESSAY_TITLE, ensure_canonical_demo_content
from services.application_service.models import ApplicationTrackerItem
from services.essay_service.models import (
    AIEssayScoreReport,
    EssayFeedback,
    EssayRevisionTask,
    EssayWorkspace,
)
from services.university_service.models import University, UniversityProgram

User = get_user_model()


class Command(BaseCommand):
    help = (
        f"Idempotently restore the canonical demo student's sample essay "
        f"('{DEMO_ESSAY_TITLE}') and application. Operates only on the "
        "canonical demo account (matched by exact email, never by similarity); "
        "requires ensure_demo_accounts to have run first. Never touches any "
        "other user's data, never creates duplicates, never prints essay "
        "text/feedback or credentials. Safe to run repeatedly, including "
        "against production."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            report = ensure_canonical_demo_content(
                User,
                University,
                UniversityProgram,
                ApplicationTrackerItem,
                EssayWorkspace,
                EssayFeedback,
                EssayRevisionTask,
                AIEssayScoreReport,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo content for {report['email']}: "
                f"university={report['university_slug']}, "
                f"application={report['application_action']}, "
                f"essay={report['essay_action']}."
            )
        )
