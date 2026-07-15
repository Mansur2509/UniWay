from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from services.application_service.models import ApplicationTrackerItem
from services.essay_service.models import EssayWorkspace
from services.institution_service.models import (
    Institution,
    InstitutionAuditLogEntry,
    InstitutionMembership,
)
from services.university_service.models import University

User = get_user_model()
STRONG_PASSWORD = "Strong-Development-Password-842!"


def _create_institution_with_manager(manager_email="manager@example.com"):
    manager = User.objects.create_user(
        username=manager_email, email=manager_email, password=STRONG_PASSWORD
    )
    admin, _ = User.objects.get_or_create(
        email="platformadmin@example.com",
        defaults={
            "username": "platformadmin@example.com",
            "role": User.Role.ADMIN,
        },
    )
    if not admin.check_password(STRONG_PASSWORD):
        admin.set_password(STRONG_PASSWORD)
        admin.save(update_fields=["password"])

    from rest_framework.test import APIClient

    client = APIClient()
    client.force_authenticate(admin)
    slug = f"school-{manager_email.split('@')[0]}"
    response = client.post(
        "/api/v1/institutions/",
        {
            "name": "Example International School",
            "slug": slug,
            "manager_email": manager_email,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED, response.data
    institution = Institution.objects.get(slug=slug)
    return institution, manager


class InstitutionCreationTests(APITestCase):
    def test_non_admin_cannot_create_an_institution(self):
        user = User.objects.create_user(
            username="notadmin@example.com", email="notadmin@example.com", password=STRONG_PASSWORD
        )
        self.client.force_authenticate(user)

        response = self.client.post(
            "/api/v1/institutions/",
            {"name": "X", "slug": "x", "manager_email": "notadmin@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_creates_institution_and_manager_membership_is_active(self):
        institution, manager = _create_institution_with_manager()

        membership = InstitutionMembership.objects.get(institution=institution, user=manager)
        self.assertEqual(membership.role, InstitutionMembership.MemberRole.SCHOOL_MANAGER)
        self.assertEqual(membership.status, InstitutionMembership.Status.ACTIVE)


class InvitationAndAcceptanceTests(APITestCase):
    def setUp(self):
        self.institution, self.manager = _create_institution_with_manager()
        self.student = User.objects.create_user(
            username="student@example.com", email="student@example.com", password=STRONG_PASSWORD
        )
        self.counselor = User.objects.create_user(
            username="counselor@example.com", email="counselor@example.com", password=STRONG_PASSWORD
        )

    def test_manager_can_invite_student_and_counselor(self):
        self.client.force_authenticate(self.manager)

        student_response = self.client.post(
            f"/api/v1/institutions/{self.institution.slug}/invitations/",
            {"email": "student@example.com", "role": "student_member"},
            format="json",
        )
        counselor_response = self.client.post(
            f"/api/v1/institutions/{self.institution.slug}/invitations/",
            {"email": "counselor@example.com", "role": "counselor"},
            format="json",
        )

        self.assertEqual(student_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(counselor_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            InstitutionMembership.objects.get(institution=self.institution, user=self.student).status,
            InstitutionMembership.Status.INVITED,
        )

    def test_non_manager_cannot_invite(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            f"/api/v1/institutions/{self.institution.slug}/invitations/",
            {"email": "counselor@example.com", "role": "counselor"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invited_student_can_accept(self):
        self.client.force_authenticate(self.manager)
        self.client.post(
            f"/api/v1/institutions/{self.institution.slug}/invitations/",
            {"email": "student@example.com", "role": "student_member"},
            format="json",
        )

        self.client.force_authenticate(self.student)
        response = self.client.post(
            f"/api/v1/institutions/{self.institution.slug}/memberships/mine/accept/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data["status"], "active")

    def test_a_user_cannot_accept_someone_elses_invitation(self):
        self.client.force_authenticate(self.manager)
        self.client.post(
            f"/api/v1/institutions/{self.institution.slug}/invitations/",
            {"email": "student@example.com", "role": "student_member"},
            format="json",
        )

        self.client.force_authenticate(self.counselor)
        response = self.client.post(
            f"/api/v1/institutions/{self.institution.slug}/memberships/mine/accept/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ConsentGatedVisibilityTests(APITestCase):
    """The core safety property of this module: a counselor sees a
    student's private data only after the student explicitly consents."""

    def setUp(self):
        self.institution, self.manager = _create_institution_with_manager()
        self.counselor = User.objects.create_user(
            username="counselor2@example.com", email="counselor2@example.com", password=STRONG_PASSWORD
        )
        self.student = User.objects.create_user(
            username="student2@example.com", email="student2@example.com", password=STRONG_PASSWORD
        )
        InstitutionMembership.objects.create(
            institution=self.institution,
            user=self.counselor,
            role=InstitutionMembership.MemberRole.COUNSELOR,
            status=InstitutionMembership.Status.ACTIVE,
        )
        self.student_membership = InstitutionMembership.objects.create(
            institution=self.institution,
            user=self.student,
            role=InstitutionMembership.MemberRole.STUDENT_MEMBER,
            status=InstitutionMembership.Status.ACTIVE,
        )
        university = University.objects.create(
            slug="consent-test-university",
            name="Consent Test University",
            country="Demoland",
            city="Sample City",
            official_website="https://example.com/consent-test-university",
            is_published=True,
        )
        ApplicationTrackerItem.objects.create(user=self.student, university=university)
        EssayWorkspace.objects.create(user=self.student, title="Private essay", draft_text="secret")

    def test_student_not_visible_with_detail_before_consent(self):
        self.client.force_authenticate(self.counselor)

        response = self.client.get(f"/api/v1/institutions/{self.institution.slug}/students/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = response.data["results"][0]
        self.assertIsNone(row["applications_by_status"])
        self.assertIsNone(row["essay_count"])

    def test_student_application_status_visible_after_consent(self):
        self.client.force_authenticate(self.student)
        self.client.patch(
            f"/api/v1/institutions/{self.institution.slug}/memberships/mine/",
            {"shares_application_status": True},
            format="json",
        )

        self.client.force_authenticate(self.counselor)
        response = self.client.get(f"/api/v1/institutions/{self.institution.slug}/students/")

        row = response.data["results"][0]
        self.assertIsNotNone(row["applications_by_status"])
        self.assertIsNone(row["essay_count"])

    def test_essay_count_never_exposes_essay_text(self):
        self.client.force_authenticate(self.student)
        self.client.patch(
            f"/api/v1/institutions/{self.institution.slug}/memberships/mine/",
            {"shares_essays": True},
            format="json",
        )

        self.client.force_authenticate(self.counselor)
        response = self.client.get(f"/api/v1/institutions/{self.institution.slug}/students/")

        self.assertNotIn("secret", str(response.data))
        row = response.data["results"][0]
        self.assertEqual(row["essay_count"], 1)

    def test_student_alone_can_set_their_own_consent(self):
        self.client.force_authenticate(self.counselor)

        response = self.client.patch(
            f"/api/v1/institutions/{self.institution.slug}/memberships/mine/",
            {"shares_application_status": True},
            format="json",
        )

        # Counselor has their own membership row -- this only ever touches
        # *their own* membership, never the student's.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_membership.refresh_from_db()
        self.assertFalse(self.student_membership.shares_application_status)

    def test_viewing_student_list_writes_an_audit_log_entry(self):
        self.client.force_authenticate(self.counselor)

        self.client.get(f"/api/v1/institutions/{self.institution.slug}/students/")

        self.assertTrue(
            InstitutionAuditLogEntry.objects.filter(
                institution=self.institution, actor=self.counselor, action="view_student_list"
            ).exists()
        )


class StudentListQueryCountTests(APITestCase):
    """Regression guard for POST-V1-021 Phase 11: this endpoint's query
    count must stay flat as the roster grows, never scale per student
    (see institution_service.services.student_summary_rows)."""

    def _seed_students(self, institution, count):
        existing = InstitutionMembership.objects.filter(institution=institution).count()
        for i in range(existing, existing + count):
            email = f"roster-{institution.slug}-{i}@example.com"
            student = User.objects.create_user(username=email, email=email, password=STRONG_PASSWORD)
            InstitutionMembership.objects.create(
                institution=institution,
                user=student,
                role=InstitutionMembership.MemberRole.STUDENT_MEMBER,
                status=InstitutionMembership.Status.ACTIVE,
                shares_application_status=True,
                shares_essays=True,
            )

    def test_query_count_does_not_grow_with_roster_size(self):
        institution, _manager = _create_institution_with_manager()
        counselor = User.objects.create_user(
            username="rostercounselor@example.com",
            email="rostercounselor@example.com",
            password=STRONG_PASSWORD,
        )
        InstitutionMembership.objects.create(
            institution=institution,
            user=counselor,
            role=InstitutionMembership.MemberRole.COUNSELOR,
            status=InstitutionMembership.Status.ACTIVE,
        )
        self.client.force_authenticate(counselor)

        self._seed_students(institution, 3)
        with self.assertNumQueries(6):
            small_response = self.client.get(f"/api/v1/institutions/{institution.slug}/students/")
        self.assertEqual(small_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(small_response.data["results"]), 3)

        self._seed_students(institution, 5)
        with self.assertNumQueries(6):
            large_response = self.client.get(f"/api/v1/institutions/{institution.slug}/students/")
        self.assertEqual(large_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(large_response.data["results"]), 8)


class CrossInstitutionAccessTests(APITestCase):
    def test_staff_from_one_institution_cannot_read_another_institutions_students(self):
        institution_a, manager_a = _create_institution_with_manager("managera@example.com")
        institution_b, _ = _create_institution_with_manager("managerb@example.com")

        self.client.force_authenticate(manager_a)
        response = self.client.get(f"/api/v1/institutions/{institution_b.slug}/students/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_removed_membership_loses_staff_access(self):
        institution, manager = _create_institution_with_manager()
        counselor = User.objects.create_user(
            username="removedcounselor@example.com",
            email="removedcounselor@example.com",
            password=STRONG_PASSWORD,
        )
        membership = InstitutionMembership.objects.create(
            institution=institution,
            user=counselor,
            role=InstitutionMembership.MemberRole.COUNSELOR,
            status=InstitutionMembership.Status.ACTIVE,
        )
        membership.status = InstitutionMembership.Status.REMOVED
        membership.save(update_fields=["status"])

        self.client.force_authenticate(counselor)
        response = self.client.get(f"/api/v1/institutions/{institution.slug}/students/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
