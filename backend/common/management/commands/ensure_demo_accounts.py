from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from common.demo_accounts import (
    CANONICAL_STUDENT_DEMO_EMAIL,
    ensure_canonical_student_demo_account,
)

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Idempotently ensure the canonical public student demo account "
        f"({CANONICAL_STUDENT_DEMO_EMAIL}) exists and is student-only, migrating "
        "it in place from any known legacy email rather than creating a second "
        "account. Safe to run repeatedly (including against production) and to "
        "run before the canonical email has ever existed. Never touches any "
        "other account, never prints credentials, never creates or modifies "
        "organizer/admin/staff/superuser access."
    )

    def handle(self, *args, **options):
        with transaction.atomic():
            report = ensure_canonical_student_demo_account(User)

        self.stdout.write(self.style.SUCCESS(f"Demo account: {report['email']} ({report['action']})."))
        for email in report["deactivated_duplicates"]:
            self.stdout.write(
                self.style.WARNING(f"Deactivated duplicate legacy demo account: {email}")
            )
