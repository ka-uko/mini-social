from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from messaging.models import Thread, Message

User = get_user_model()


class MessagingTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user(username="alice", password="pass123")
        self.b = User.objects.create_user(username="bob", password="pass123")

    def test_start_thread_and_send_message(self):
        self.client.login(username="alice", password="pass123")
        # start/open thread
        resp = self.client.get(reverse("start_thread", args=[self.b.username]), follow=True)
        self.assertEqual(resp.status_code, 200)
        thread = Thread.objects.first()
        self.assertIsNotNone(thread)

        # send message
        resp = self.client.post(reverse("thread_detail", args=[thread.pk]), {"text": "hi"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(thread.messages.filter(sender=self.a, text="hi").exists())

    def test_mark_incoming_as_read(self):
        # создаём тред и входящее сообщение для bob
        u1, u2 = (self.a, self.b) if self.a.id < self.b.id else (self.b, self.a)
        thread = Thread.objects.create(user1=u1, user2=u2)
        Message.objects.create(thread=thread, sender=self.a, text="ping")

        # bob открывает диалог → помечаем как прочитано
        self.client.login(username="bob", password="pass123")
        resp = self.client.get(reverse("thread_detail", args=[thread.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(thread.messages.first().read_at)
