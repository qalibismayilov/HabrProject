
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        ADMIN = "admin", "Admin"
        USER = "user", "User"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name="İstifadəçi rolu",
    )

    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Bloklanıb",
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
