from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from services.user_profile_service.models import (
    Activity,
    Honor,
)

User = get_user_model()


class ProfileItemCRUDTestCase(APITestCase):
    """Test CRUD operations for structured profile items"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123",
            role=User.Role.STUDENT,
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123",
            role=User.Role.STUDENT,
        )

    def test_create_activity_authenticated(self):
        """Test creating an activity requires authentication"""
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "Student Government",
            "role": "President",
            "organization": "School Council",
            "description": "Led school council",
        }
        response = self.client.post("/api/profile/activities/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activity.objects.filter(user=self.user1).count(), 1)

    def test_create_activity_unauthenticated(self):
        """Test creating an activity without auth fails"""
        data = {"title": "Student Government", "role": "President"}
        response = self.client.post("/api/profile/activities/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_self_only_activities(self):
        """Test user can only see their own activities"""
        Activity.objects.create(user=self.user1, title="Activity 1")
        Activity.objects.create(user=self.user2, title="Activity 2")

        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/profile/activities/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Activity 1")

    def test_cannot_update_another_users_item(self):
        """Test user cannot update another user's item"""
        activity = Activity.objects.create(user=self.user2, title="Original Title")

        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            f"/api/profile/activities/{activity.id}/",
            {"title": "New Title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_another_users_item(self):
        """Test user cannot delete another user's item"""
        activity = Activity.objects.create(user=self.user2, title="Activity")

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/profile/activities/{activity.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Activity.objects.filter(id=activity.id).exists())

    def test_field_validation_title_required(self):
        """Test title field is required"""
        self.client.force_authenticate(user=self.user1)
        data = {"role": "President"}  # Missing title
        response = self.client.post("/api/profile/activities/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_honor(self):
        """Test creating an honor"""
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "National Merit",
            "issuing_organization": "National Association",
            "level": "National",
            "year": 2023,
        }
        response = self.client.post("/api/profile/honors/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Honor.objects.filter(user=self.user1).count(), 1)

    def test_create_olympiad(self):
        """Test creating an olympiad entry"""
        self.client.force_authenticate(user=self.user1)
        data = {"name": "Math Olympiad", "subject": "Mathematics", "year": 2023}
        response = self.client.post("/api/profile/olympiads/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_sport(self):
        """Test creating a sport entry"""
        self.client.force_authenticate(user=self.user1)
        data = {
            "sport_name": "Basketball",
            "level": "Varsity",
            "years_trained": "4 years",
        }
        response = self.client.post("/api/profile/sports/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_research(self):
        """Test creating a research project"""
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "Climate Research",
            "field": "Environmental Science",
            "current_stage": "active",
        }
        response = self.client.post("/api/profile/research-projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_essay(self):
        """Test creating an essay"""
        self.client.force_authenticate(user=self.user1)
        data = {"essay_type": "Why School", "school_program": "Harvard"}
        response = self.client.post("/api/profile/essays/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_portfolio(self):
        """Test creating a portfolio project"""
        self.client.force_authenticate(user=self.user1)
        data = {"title": "Web App", "project_type": "Full Stack"}
        response = self.client.post(
            "/api/profile/portfolio-projects/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_item(self):
        """Test deleting an item"""
        activity = Activity.objects.create(user=self.user1, title="Test Activity")

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/profile/activities/{activity.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Activity.objects.filter(id=activity.id).exists())

    def test_update_item(self):
        """Test updating an item"""
        activity = Activity.objects.create(user=self.user1, title="Original Title")

        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(
            f"/api/profile/activities/{activity.id}/",
            {"title": "Updated Title"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity.refresh_from_db()
        self.assertEqual(activity.title, "Updated Title")
