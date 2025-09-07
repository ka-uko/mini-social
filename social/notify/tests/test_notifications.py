from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from network.models import Post, Comment
from notify.models import Notification

User = get_user_model()


class NotificationTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user(username="alice", password="pass123")
        self.b = User.objects.create_user(username="bob", password="pass123")
        self.post = Post.objects.create(author=self.b, text="hello")

    def test_notify_on_like(self):
        self.client.login(username="alice", password="pass123")
        url = reverse("toggle_like_ajax", args=[self.post.pk])
        self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        n = Notification.objects.filter(to_user=self.b, verb="like", post_id=self.post.id).first()
        self.assertIsNotNone(n)
        self.assertEqual(n.actor, self.a)

    def test_notify_on_comment(self):
        self.client.login(username="alice", password="pass123")
        url = reverse("add_comment", args=[self.post.pk])
        self.client.post(url, {"text": "nice"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        n = Notification.objects.filter(to_user=self.b, verb="comment", post_id=self.post.id).first()
        self.assertIsNotNone(n)
        self.assertEqual(n.actor, self.a)
