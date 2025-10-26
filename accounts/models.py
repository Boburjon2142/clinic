from django.contrib.auth.models import AbstractUser
from django.db import models


class Roles(models.TextChoices):
    CREATOR = 'creator', 'Creator'
    ADMIN = 'admin', 'Admin (To\'liq)'
    ADMIN1 = 'admin1', 'Admin 1 (Menejer)'
    ADMIN2 = 'admin2', 'Admin 2 (Narx belgilovchi)'
    ADMIN3 = 'admin3', 'Admin 3 (Kassir)'
    DOCTOR = 'doctor', 'Shifokor'
    STAFF = 'staff', 'Qabulxona'


class User(AbstractUser):
    role = models.CharField("Rol", max_length=20, choices=Roles.choices, default=Roles.STAFF)
    avatar = models.ImageField("Avatar", upload_to='avatars/', null=True, blank=True)

    @property
    def avatar_url(self):
        try:
            if self.avatar and hasattr(self.avatar, 'url'):
                return self.avatar.url
        except Exception:
            return None
        return None

    def is_creator(self):
        return self.role == Roles.CREATOR

    def is_admin(self):
        return self.role in (Roles.ADMIN, Roles.ADMIN1, Roles.ADMIN2, Roles.ADMIN3)

    def is_doctor(self):
        return self.role == Roles.DOCTOR

    def is_staff_role(self):
        return self.role == Roles.STAFF

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
