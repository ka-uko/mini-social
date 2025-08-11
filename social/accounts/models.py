from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import F, Q

class User(AbstractUser):
    # на будущее: avatar, bio и т.п.
    pass


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',   # на кого Я подписан
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',   # кто подписан на МЕНЯ
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # один раз на одного пользователя
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_follow',
            ),
            # запрет на подписку на себя
            models.CheckConstraint(
                check=~Q(follower=F('following')),
                name='prevent_self_follow',
            ),
        ]
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]

    def __str__(self):
        return f"{self.follower} -> {self.following}"
