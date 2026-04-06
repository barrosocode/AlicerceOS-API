"""Testes unitários — Custom User com login por e-mail (RF01 / Módulo 0)."""

from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase


class CustomUserEmailLoginTests(TestCase):
    def test_login_por_email(self):
        User = get_user_model()
        User.objects.create_user(
            email="gestor@jell.com",
            password="senha-forte-123",
            role="gestor",
        )
        user = User.objects.get(email="gestor@jell.com")
        self.assertEqual(user.USERNAME_FIELD, "email")
        self.assertIsNone(user.username)
        authed = authenticate(email="gestor@jell.com", password="senha-forte-123")
        self.assertIsNotNone(authed)
        self.assertEqual(authed.pk, user.pk)
