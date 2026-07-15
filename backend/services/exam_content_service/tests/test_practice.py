from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from services.exam_content_service.models import (
    AnswerChoice,
    Exam,
    ExamSection,
    PracticeAnswer,
    Question,
    QuestionBookmark,
    Skill,
    SkillMastery,
)

User = get_user_model()
STRONG_PASSWORD = "Strong-Development-Password-842!"


def _make_published_question(section, skill=None, correct_label="A"):
    question = Question.objects.create(
        section=section,
        skill=skill,
        prompt="2 + 2 = ?",
        origin=Question.Origin.ORIGINAL,
        review_status=Question.ReviewStatus.PUBLISHED,
        is_published=True,
    )
    for label, text, is_correct in (("A", "4", True), ("B", "5", False)):
        AnswerChoice.objects.create(
            question=question, label=label, text=text, is_correct=is_correct
        )
    return question


class PracticeSessionFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="practice@example.com", email="practice@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(self.user)
        self.exam = Exam.objects.create(name="SAT Practice", slug="sat-practice", is_published=True)
        self.section = ExamSection.objects.create(exam=self.exam, name="Math", slug="math")
        self.skill = Skill.objects.create(section=self.section, name="Arithmetic", slug="arithmetic")
        self.question = _make_published_question(self.section, skill=self.skill)
        self.correct_choice = self.question.answer_choices.get(is_correct=True)
        self.wrong_choice = self.question.answer_choices.get(is_correct=False)

    def test_starting_a_session_scopes_it_to_the_requesting_user(self):
        response = self.client.post("/api/v1/practice-sessions/", {"exam": self.exam.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        other_user = User.objects.create_user(
            username="other@example.com", email="other@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(other_user)
        list_response = self.client.get("/api/v1/practice-sessions/")
        self.assertEqual(list_response.data["results"] if "results" in list_response.data else list_response.data, [])

    def test_answering_correctly_updates_skill_mastery(self):
        session = self.client.post(
            "/api/v1/practice-sessions/", {"exam": self.exam.id}, format="json"
        ).data

        response = self.client.post(
            f"/api/v1/practice-sessions/{session['id']}/answer/",
            {"question_id": self.question.id, "choice_id": self.correct_choice.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data["is_correct"])
        mastery = SkillMastery.objects.get(user=self.user, skill=self.skill)
        self.assertEqual(mastery.attempt_count, 1)
        self.assertEqual(mastery.correct_count, 1)

    def test_answering_incorrectly_still_records_the_attempt(self):
        session = self.client.post(
            "/api/v1/practice-sessions/", {"exam": self.exam.id}, format="json"
        ).data

        self.client.post(
            f"/api/v1/practice-sessions/{session['id']}/answer/",
            {"question_id": self.question.id, "choice_id": self.wrong_choice.id},
            format="json",
        )

        mastery = SkillMastery.objects.get(user=self.user, skill=self.skill)
        self.assertEqual(mastery.attempt_count, 1)
        self.assertEqual(mastery.correct_count, 0)
        self.assertEqual(mastery.accuracy_percent, 0.0)

    def test_re_answering_the_same_question_does_not_double_count_mastery(self):
        session = self.client.post(
            "/api/v1/practice-sessions/", {"exam": self.exam.id}, format="json"
        ).data

        self.client.post(
            f"/api/v1/practice-sessions/{session['id']}/answer/",
            {"question_id": self.question.id, "choice_id": self.wrong_choice.id},
            format="json",
        )
        self.client.post(
            f"/api/v1/practice-sessions/{session['id']}/answer/",
            {"question_id": self.question.id, "choice_id": self.correct_choice.id},
            format="json",
        )

        self.assertEqual(PracticeAnswer.objects.filter(session_id=session["id"]).count(), 1)

    def test_completing_a_session_sets_completed_at_once(self):
        session = self.client.post(
            "/api/v1/practice-sessions/", {"exam": self.exam.id}, format="json"
        ).data

        first = self.client.post(f"/api/v1/practice-sessions/{session['id']}/complete/")
        second = self.client.post(f"/api/v1/practice-sessions/{session['id']}/complete/")

        self.assertIsNotNone(first.data["completed_at"])
        self.assertEqual(first.data["completed_at"], second.data["completed_at"])

    def test_cannot_answer_a_completed_session(self):
        session = self.client.post(
            "/api/v1/practice-sessions/", {"exam": self.exam.id}, format="json"
        ).data
        self.client.post(f"/api/v1/practice-sessions/{session['id']}/complete/")

        response = self.client.post(
            f"/api/v1/practice-sessions/{session['id']}/answer/",
            {"question_id": self.question.id, "choice_id": self.correct_choice.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


class QuestionVisibilityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="visibility@example.com", email="visibility@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(self.user)
        exam = Exam.objects.create(name="AP Stats Practice", slug="ap-stats-practice", is_published=True)
        self.section = ExamSection.objects.create(exam=exam, name="Statistics", slug="statistics")

    def test_draft_question_never_reaches_the_public_endpoint(self):
        Question.objects.create(
            section=self.section,
            prompt="Draft-only question",
            review_status=Question.ReviewStatus.DRAFT,
            is_published=False,
        )

        response = self.client.get("/api/v1/questions/")

        prompts = [q["prompt"] for q in response.data.get("results", response.data)]
        self.assertNotIn("Draft-only question", prompts)

    def test_archived_question_never_reaches_the_public_endpoint(self):
        Question.objects.create(
            section=self.section,
            prompt="Archived question",
            review_status=Question.ReviewStatus.ARCHIVED,
            is_published=False,
        )

        response = self.client.get("/api/v1/questions/")

        prompts = [q["prompt"] for q in response.data.get("results", response.data)]
        self.assertNotIn("Archived question", prompts)

    def test_published_reviewed_question_does_reach_the_endpoint(self):
        _make_published_question(self.section)

        response = self.client.get("/api/v1/questions/")

        prompts = [q["prompt"] for q in response.data.get("results", response.data)]
        self.assertIn("2 + 2 = ?", prompts)


class QuestionBookmarkTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bookmark@example.com", email="bookmark@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(self.user)
        exam = Exam.objects.create(name="Bookmark Exam", slug="bookmark-exam", is_published=True)
        section = ExamSection.objects.create(exam=exam, name="Math", slug="math")
        self.question = _make_published_question(section)

    def test_bookmarking_is_idempotent(self):
        first = self.client.post(
            "/api/v1/question-bookmarks/", {"question": self.question.id}, format="json"
        )
        second = self.client.post(
            "/api/v1/question-bookmarks/", {"question": self.question.id}, format="json"
        )

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            QuestionBookmark.objects.filter(user=self.user, question=self.question).count(), 1
        )

    def test_bookmarks_are_scoped_to_the_requesting_user(self):
        self.client.post("/api/v1/question-bookmarks/", {"question": self.question.id}, format="json")
        other_user = User.objects.create_user(
            username="otherbookmark@example.com",
            email="otherbookmark@example.com",
            password=STRONG_PASSWORD,
        )

        self.client.force_authenticate(other_user)
        response = self.client.get("/api/v1/question-bookmarks/")

        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 0)
