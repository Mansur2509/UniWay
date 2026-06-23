from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class InternalApiGuardTests(APITestCase):
    guarded_read_paths = (
        "/api/events/",
        "/api/v1/events/",
        "/api/v1/universities/",
        "/api/v1/exams/",
        "/api/v1/questions/",
        "/api/profile/me/",
        "/api/profile/completion/",
        "/api/events/my-registrations/",
        "/api/organizer/events/",
        "/api/admin/events/pending/",
    )

    def test_anonymous_users_cannot_read_internal_product_apis(self):
        for path in self.guarded_read_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertIn(response.status_code, (401, 403))

    def test_authenticated_student_can_open_catalog_reads(self):
        user = get_user_model().objects.create_user(
            username="guard-student@example.com",
            email="guard-student@example.com",
            password="Strong-Development-Password-842!",
        )
        self.client.force_authenticate(user)

        for path in (
            "/api/events/",
            "/api/v1/events/",
            "/api/v1/universities/",
            "/api/v1/exams/",
            "/api/v1/questions/",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
