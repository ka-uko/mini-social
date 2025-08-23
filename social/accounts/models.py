from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import F, Q  # если используешь в других местах

class User(AbstractUser):
    class Roles(models.TextChoices):
        PROVIDER   = "provider",   "Банные услуги"
        BUILDER    = "builder",    "Строительство бань"
        SELLER     = "seller",     "Продажа товаров"
        ENTHUSIAST = "enthusiast", "Люблю попариться"

    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="Фотография (аватар)"
    )
    bio = models.TextField(
        blank=True, max_length=500, verbose_name="О себе"
    )
    role = models.CharField(
        max_length=20, choices=Roles.choices, blank=True, verbose_name="Тип пользователя"
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name="Город"
    )
    services = models.ManyToManyField(
        "ServiceTag", blank=True, related_name="users", verbose_name="Специализации"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class ServiceTag(models.Model):
    code = models.CharField(max_length=32, unique=True, verbose_name="Код")
    title = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        ordering = ["title"]
        verbose_name = "Специализация"
        verbose_name_plural = "Специализации"

    def __str__(self):
        return self.title



class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following'
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow'),
            models.CheckConstraint(check=~Q(follower=F('following')), name='prevent_self_follow'),
        ]
        indexes = [models.Index(fields=['follower']), models.Index(fields=['following'])]

    def __str__(self):
        return f"{self.follower} -> {self.following}"

