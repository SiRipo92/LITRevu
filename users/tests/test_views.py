from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationViewTests(TestCase):
    """View-level tests for the registration flow (US01)."""

    def test_register_get_renders_form(self):
        """GET /register/ renders the registration page with required fields."""

        url = reverse("register")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Inscrivez-vous")
        # field presence (basic smoke)
        self.assertContains(resp, "password1")
        self.assertContains(resp, "password2")

    def test_register_post_success_redirects_with_qs(self):
        """POST valid data to /register/ creates a user and redirects to home with query params."""

        url = reverse("register")
        data = {
            "username": "eve",
            "password1": "StrongPassw0rd!",
            "password2": "StrongPassw0rd!",
        }
        resp = self.client.post(url, data, follow=False)
        self.assertEqual(resp.status_code, 302)
        location = resp["Location"]
        self.assertTrue(location.startswith(reverse("home")))
        self.assertIn("registered=1", location)
        self.assertIn("u=eve", location)
        self.assertTrue(User.objects.filter(username="eve").exists())

    def test_register_post_invalid_shows_errors(self):
        """POST invalid data re-renders the form with field errors; no user is created."""

        url = reverse("register")
        data = {
            "username": "frank",
            "password1": "Mismatch123!",
            "password2": "Different456!",
        }
        resp = self.client.post(url, data)
        # re-render the same template with errors
        self.assertEqual(resp.status_code, 200)

        # Prefer checking the form object in the context rather than strings
        self.assertIn("form", resp.context)
        form = resp.context["form"]
        self.assertFalse(form.is_valid())
        # UserCreationForm puts the mismatch error on password2
        self.assertIn("password2", form.errors)

        # Optional: smoke checks on the HTML rather than exact wording
        self.assertContains(resp, 'id="id_password2"')
        self.assertIn(b'aria-invalid="true"', resp.content)

        # No user created
        self.assertFalse(User.objects.filter(username="frank").exists())


class HomeViewTests(TestCase):
    """Homepage behavior in US01: login UI visible, but no authentication occurs."""

    def test_home_shows_login_form_but_does_not_process_login(self):
        """POSTing credentials to / does not authenticate; login form remains visible."""

        # Create a real user
        User.objects.create_user(username="gina", password="P@ssw0rd!!")
        # Post credentials to home — US01 should not authenticate yet
        url = reverse("home")
        resp = self.client.post(url, {"username": "gina", "password": "P@ssw0rd!!"})
        self.assertEqual(resp.status_code, 200)
        # Still anonymous on subsequent request
        resp2 = self.client.get(url)
        self.assertTrue(resp2.wsgi_request.user.is_anonymous)
        # Login form still present
        self.assertContains(resp2, "Connectez-vous")
