import io
import tempfile
import shutil
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.encoding import force_str
from network.models import Post, Like, Comment
from accounts.models import Follow

User = get_user_model()


def tiny_png():
    # 1×1 прозрачный PNG
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0bIDATx\x9cc``\x00\x00\x00\x02\x00\x01"
        b"\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class PostLikeCommentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.u1 = User.objects.create_user(username="alice", password="pass123")
        cls.u2 = User.objects.create_user(username="bob", password="pass123")

    def setUp(self):
        self.client.login(username="alice", password="pass123")

    def test_create_post_with_image(self):
        url = reverse("post_create")
        img = SimpleUploadedFile("p.png", tiny_png(), content_type="image/png")
        resp = self.client.post(url, {"text": "hello", "image": img}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Post.objects.filter(author=self.u1, text="hello").exists())

    def test_home_feed_all_and_subscriptions(self):
        # u2 пишет пост
        p = Post.objects.create(author=self.u2, text="from bob")
        # без подписки — видим во «Все»
        resp = self.client.get(reverse("home"))
        self.assertContains(resp, "from bob")
        # подписываемся
        Follow.objects.create(follower=self.u1, following=self.u2)
        # «Подписки»
        resp = self.client.get(reverse("home") + "?feed=sub")
        self.assertContains(resp, "from bob")

    def test_like_toggle_ajax(self):
        p = Post.objects.create(author=self.u2, text="like me")
        url = reverse("toggle_like_ajax", args=[p.pk])
        resp = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Like.objects.filter(user=self.u1, post=p).exists())

        # повторный клик — снимает лайк
        resp = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Like.objects.filter(user=self.u1, post=p).exists())

    def test_add_comment_ajax(self):
        p = Post.objects.create(author=self.u2, text="comment me")
        url = reverse("add_comment", args=[p.pk])
        resp = self.client.post(
            url,
            {"text": "first"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Comment.objects.filter(post=p, text="first", parent__isnull=True).exists())

    def test_add_reply_ajax(self):
        p = Post.objects.create(author=self.u2, text="comment me")
        c = Comment.objects.create(author=self.u2, post=p, text="root")
        url = reverse("add_reply", args=[c.pk])
        resp = self.client.post(
            url,
            {"text": "answer"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Comment.objects.filter(post=p, parent=c, text="answer").exists())
