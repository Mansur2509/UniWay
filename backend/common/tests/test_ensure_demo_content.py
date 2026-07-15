from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from common.demo_accounts import CANONICAL_STUDENT_DEMO_EMAIL, ensure_canonical_student_demo_account
from common.demo_content import (
    DEMO_ESSAY_DRAFT_TEXT,
    DEMO_ESSAY_TITLE,
    DEMO_UNIVERSITY_SLUG,
    ensure_canonical_demo_content,
)
from services.application_service.models import ApplicationTrackerItem
from services.essay_service.models import (
    AIEssayScoreReport,
    EssayFeedback,
    EssayRevisionTask,
    EssayWorkspace,
)
from services.university_service.models import University, UniversityProgram

User = get_user_model()


def _run(user_model=User):
    return ensure_canonical_demo_content(
        user_model,
        University,
        UniversityProgram,
        ApplicationTrackerItem,
        EssayWorkspace,
        EssayFeedback,
        EssayRevisionTask,
        AIEssayScoreReport,
    )


class EnsureCanonicalDemoContentTests(TestCase):
    def setUp(self):
        ensure_canonical_student_demo_account(User)
        self.demo_user = User.objects.get(email=CANONICAL_STUDENT_DEMO_EMAIL)

    def test_requires_canonical_account_to_already_exist(self):
        User.objects.filter(email=CANONICAL_STUDENT_DEMO_EMAIL).delete()

        with self.assertRaises(LookupError):
            _run()

    def test_first_run_creates_university_application_and_essay(self):
        report = _run()

        self.assertEqual(report["essay_action"], "created")
        self.assertEqual(report["application_action"], "created")
        self.assertTrue(University.objects.filter(slug=DEMO_UNIVERSITY_SLUG).exists())
        university = University.objects.get(slug=DEMO_UNIVERSITY_SLUG)
        self.assertTrue(university.is_demo)

        application = ApplicationTrackerItem.objects.get(user=self.demo_user, university=university)
        essay = EssayWorkspace.objects.get(user=self.demo_user, title=DEMO_ESSAY_TITLE)
        self.assertEqual(essay.application_id, application.id)
        self.assertEqual(essay.draft_text, DEMO_ESSAY_DRAFT_TEXT)

    def test_second_run_changes_nothing(self):
        _run()
        essay_before = EssayWorkspace.objects.get(user=self.demo_user, title=DEMO_ESSAY_TITLE)
        app_before = ApplicationTrackerItem.objects.get(user=self.demo_user)

        report = _run()

        self.assertEqual(report["essay_action"], "already_present")
        self.assertEqual(report["application_action"], "already_present")
        self.assertEqual(EssayWorkspace.objects.filter(user=self.demo_user).count(), 1)
        self.assertEqual(ApplicationTrackerItem.objects.filter(user=self.demo_user).count(), 1)
        essay_after = EssayWorkspace.objects.get(pk=essay_before.pk)
        app_after = ApplicationTrackerItem.objects.get(pk=app_before.pk)
        self.assertEqual(essay_after.draft_text, essay_before.draft_text)
        self.assertEqual(app_after.status, app_before.status)

    def test_duplicate_essay_is_not_created_on_repeated_runs(self):
        for _ in range(3):
            _run()

        self.assertEqual(
            EssayWorkspace.objects.filter(user=self.demo_user, title=DEMO_ESSAY_TITLE).count(), 1
        )

    def test_restores_corrupted_draft_and_clears_stale_feedback(self):
        _run()
        essay = EssayWorkspace.objects.get(user=self.demo_user, title=DEMO_ESSAY_TITLE)
        essay.draft_text = "some other content a tester typed in during manual QA"
        essay.save(update_fields=["draft_text"])
        EssayFeedback.objects.create(
            essay=essay, overall_label="weak", word_count=1, word_limit_status="too_short"
        )
        EssayRevisionTask.objects.create(essay=essay, title="stale", category="structure")
        AIEssayScoreReport.objects.create(
            essay=essay,
            user=self.demo_user,
            essay_text_hash="a" * 10,
            context_hash="b" * 10,
            model_name="test-model",
            overall_essay_readiness=1,
            prompt_fit=1,
            structure=1,
            specificity_evidence=1,
            authenticity=1,
            language_clarity=1,
            confidence="low",
            word_count=1,
            word_limit_status="under",
            ai_paraphrase_style_signal="low",
            generic_language_signal="low",
            unsupported_claims_signal="low",
        )

        report = _run()

        self.assertEqual(report["essay_action"], "restored")
        essay.refresh_from_db()
        self.assertEqual(essay.draft_text, DEMO_ESSAY_DRAFT_TEXT)
        self.assertEqual(EssayFeedback.objects.filter(essay=essay).count(), 0)
        self.assertEqual(EssayRevisionTask.objects.filter(essay=essay).count(), 0)
        self.assertEqual(AIEssayScoreReport.objects.filter(essay=essay).count(), 0)

    def test_real_user_remains_completely_untouched(self):
        real_user = User.objects.create_user(
            username="real.student@example.com",
            email="real.student@example.com",
            password="a-real-users-password",
            role=User.Role.STUDENT,
        )
        real_user.first_name = "Real"
        real_user.save()

        _run()

        real_user.refresh_from_db()
        self.assertEqual(real_user.first_name, "Real")
        self.assertFalse(
            EssayWorkspace.objects.filter(user=real_user).exists(),
            "ensure_demo_content must never create content for a non-demo user",
        )

    def test_similarly_named_non_demo_user_essay_is_untouched(self):
        lookalike = User.objects.create_user(
            username="student.demo2@uniway.local",
            email="student.demo2@uniway.local",
            password="whatever",
            role=User.Role.STUDENT,
        )
        lookalike_essay = EssayWorkspace.objects.create(
            user=lookalike,
            title=DEMO_ESSAY_TITLE,
            draft_text="this belongs to a different, real account and must never change",
        )

        _run()

        lookalike_essay.refresh_from_db()
        self.assertEqual(
            lookalike_essay.draft_text,
            "this belongs to a different, real account and must never change",
        )

    def test_demo_role_remains_student_after_running(self):
        _run()

        self.demo_user.refresh_from_db()
        self.assertEqual(self.demo_user.role, User.Role.STUDENT)

    def test_admin_and_organizer_access_remain_denied_after_running(self):
        _run()

        self.demo_user.refresh_from_db()
        self.assertFalse(self.demo_user.is_staff)
        self.assertFalse(self.demo_user.is_superuser)
        self.assertNotEqual(self.demo_user.role, User.Role.ADMIN)
        self.assertNotEqual(self.demo_user.role, User.Role.ORGANIZER)

    def test_command_output_never_prints_essay_text_or_password(self):
        out = StringIO()
        call_command("ensure_demo_content", stdout=out)

        output = out.getvalue()
        self.assertNotIn(DEMO_ESSAY_DRAFT_TEXT, output)
        self.assertNotIn("UniWay-Demo-842!", output)
        self.assertIn(CANONICAL_STUDENT_DEMO_EMAIL, output)
