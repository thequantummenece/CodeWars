from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase

from .models import Contact

SIGNUP = {
    "inputfname": "Ada",
    "inputlname": "Lovelace",
    "username": "ada",
    "inputemail": "ada@example.com",
    "password1": "k3yb0ard-Brawl!",
    "password2": "k3yb0ard-Brawl!",
}


def message_texts(response):
    return [str(m) for m in get_messages(response.wsgi_request)]


class LoginTests(TestCase):
    def test_missing_field_redirects_with_error(self):
        response = self.client.post("/login/", {"lusername": "ada"})
        self.assertRedirects(response, "/")
        self.assertIn("Username and password are required", message_texts(response))


class SignupTests(TestCase):
    def test_missing_field_redirects_with_error(self):
        response = self.client.post("/signup/", {"username": "ada"})
        self.assertRedirects(response, "/")
        self.assertIn("All fields are required", message_texts(response))
        self.assertFalse(User.objects.exists())

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            "/signup/", {**SIGNUP, "password1": "1", "password2": "1"}
        )
        self.assertRedirects(response, "/")
        self.assertFalse(User.objects.exists())
        self.assertTrue(any("too short" in m for m in message_texts(response)))

    def test_valid_signup_creates_user(self):
        self.client.post("/signup/", SIGNUP)
        self.assertTrue(User.objects.filter(username="ada").exists())


class ContactTests(TestCase):
    def test_post_saves_contact(self):
        response = self.client.post(
            "/contact/",
            {
                "name": "Ada",
                "email": "ada@example.com",
                "subject": "Hi",
                "message": "Hello",
            },
        )
        self.assertContains(response, "TRANSMISSION RECEIVED")
        contact = Contact.objects.get()
        self.assertEqual((contact.name, contact.content), ("Ada", "Hi\n\nHello"))

    def test_missing_field_saves_nothing(self):
        self.client.post("/contact/", {"name": "Ada"})
        self.assertFalse(Contact.objects.exists())
