from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        ORGANIZER = "organizer", "Organizer"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, db_index=True)

    @property
    def is_organizer(self) -> bool:
        return self.role == self.Role.ORGANIZER

    @property
    def is_admin_role(self) -> bool:
        return self.is_staff or self.is_superuser or self.role == self.Role.ADMIN

