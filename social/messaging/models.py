from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


class Thread(models.Model):
    """
    Диалог 1:1 между двумя пользователями.
    Гарантируем уникальность пары (min(user1_id, user2_id), max(...)).
    """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # обновляется при новых сообщениях

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user1', 'user2']),
            models.Index(fields=['updated_at']),
        ]

    def clean(self):
        if self.user1_id == self.user2_id:
            raise ValidationError("Нельзя создать диалог с самим собой.")

    def save(self, *args, **kwargs):
        # нормализуем порядок, чтобы user1_id < user2_id
        if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    def participants(self):
        return (self.user1, self.user2)

    def other(self, user):
        return self.user2 if user == self.user1 else self.user1

    def __str__(self):
        return f"Thread({self.user1} & {self.user2})"


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['thread', 'created_at']),
        ]

    def __str__(self):
        return f"m#{self.id} by {self.sender} in t#{self.thread_id}"
