from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Follow

User = get_user_model()


class AuthAndFollowTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="alice", password="pass123")
        self.u2 = User.objects.create_user(username="bob", password="pass123")

    def test_signup_and_login(self):
        # signup (проверяем, что форма рендерится и успешная регистрация логинит)
        resp = self.client.get(reverse("signup"))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(reverse("signup"), {
            "username": "charlie",
            "password1": "Sup3rS3cret_pass!",
            "password2": "Sup3rS3cret_pass!",
            "email": "c@example.com",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(username="charlie").exists())
        # после signup — пользователь залогинен
        self.assertTrue(resp.context["user"].is_authenticated)

    def test_login_logout(self):
        resp = self.client.post(reverse("login"), {
            "username": "alice",
            "password": "pass123"
        }, follow=True)
        self.assertTrue(resp.context["user"].is_authenticated)

        resp = self.client.post(reverse("logout"), follow=True)
        self.assertFalse(resp.context["user"].is_authenticated)

    def test_toggle_follow(self):
        self.client.login(username="alice", password="pass123")
        url = reverse("toggle_follow", args=[self.u2.username])
        # follow
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Follow.objects.filter(follower=self.u1, following=self.u2).exists())
        # unfollow
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Follow.objects.filter(follower=self.u1, following=self.u2).exists())

    def test_profile_page(self):
        url = reverse("profile", args=[self.u1.username])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "@alice")
