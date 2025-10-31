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
    """Homepage behavior in US02: login form processes authentication."""

    def test_home_processes_login_and_redirects(self):
        """POST valid credentials logs user in and redirects to feed."""
        User.objects.create_user(username="gina", password="P@ssw0rd!!")
        url = reverse("home")
        resp = self.client.post(url, {"username": "gina", "password": "P@ssw0rd!!"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("feed"), resp.url)


class HomeViewLoginTests(TestCase):
    """View-level tests for login functionality (US02)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="ivy",
            password="StrongPassw0rd!"
        )
        self.url = reverse("home")

    def test_get_home_renders_login_form(self):
        """GET / renders homepage with login form fields."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Connectez-vous")
        self.assertContains(resp, "id=\"id_username\"")
        self.assertContains(resp, "id=\"id_password\"")

    def test_inputs_have_aria_labels(self):
        """Login form inputs should include ARIA labels for accessibility."""
        resp = self.client.get(self.url)
        html = resp.content.decode()

        # accept both escaped and unescaped forms
        self.assertTrue(
            'aria-label="Nom d&#x27;utilisateur"' in html or 'aria-label="Nom d\'utilisateur"' in html,
            "Missing aria-label for username input"
        )
        self.assertIn('aria-label="Mot de passe"', html)

    def test_post_valid_login_redirects_to_feed(self):
        """Valid credentials authenticate user and redirect to /feed."""
        data = {"username": "ivy", "password": "StrongPassw0rd!", "remember_me": True}
        resp = self.client.post(self.url, data)
        # Redirect after login
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("feed"), resp.url)

    def test_post_invalid_login_stays_on_page_with_error(self):
        """Invalid credentials re-render homepage and show error message."""
        data = {"username": "ivy", "password": "wrongpass"}
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        # Non-field error message from messages framework or form
        self.assertContains(resp, "correct username and password")
        self.assertTrue(resp.wsgi_request.user.is_anonymous)

    def test_session_expires_on_browser_close_if_remember_me_unchecked(self):
        """When 'remember_me' is unchecked, session should expire on browser close."""
        data = {"username": "ivy", "password": "StrongPassw0rd!"}
        resp = self.client.post(self.url, data, follow=True)
        session = resp.wsgi_request.session
        print("Expire on browser close:", session.get_expire_at_browser_close())
        self.assertTrue(
            session.get_expire_at_browser_close(),
            "Expected session to expire at browser close, but it does not."
        )

    def test_session_persists_if_remember_me_checked(self):
        """Checked 'remember_me' sets a 2-week session expiry."""
        data = {"username": "ivy", "password": "StrongPassw0rd!", "remember_me": True}
        resp = self.client.post(self.url, data, follow=True)
        session = resp.wsgi_request.session
        expiry = session.get_expiry_age()
        self.assertEqual(expiry, 1209600, f"Expected 1209600, got {expiry}")
