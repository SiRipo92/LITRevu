from django.test import TestCase
from django.contrib.auth import get_user_model

from users.forms import RegistrationForm, LoginForm

User = get_user_model()


class RegistrationFormTests(TestCase):
    """Form-level tests for RegistrationForm (UserCreationForm-based)."""

    def test_form_valid_creates_user(self):
        """Valid data yields a saved user with a hashed password."""
        form = RegistrationForm(data={
            "username": "alice",
            "password1": "StrongPassw0rd!",
            "password2": "StrongPassw0rd!",
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsInstance(user, User)
        self.assertTrue(User.objects.filter(username="alice").exists())
        # password is hashed, not stored as plain text
        self.assertTrue(user.check_password("StrongPassw0rd!"))

    def test_username_required(self):
        """Blank username is invalid and raises a form error on 'username'."""
        form = RegistrationForm(data={
            "username": "",
            "password1": "StrongPassw0rd!",
            "password2": "StrongPassw0rd!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_passwords_must_match(self):
        """Mismatched passwords invalidate the form; error is attached to 'password2'."""
        form = RegistrationForm(data={
            "username": "bob",
            "password1": "StrongPassw0rd!",
            "password2": "Different123!",
        })
        self.assertFalse(form.is_valid())
        # UserCreationForm places mismatch error on password2
        self.assertIn("password2", form.errors)

    def test_password_strength_rules_apply(self):
        """Weak passwords fail default validators; error surfaces on 'password2'."""

        # Too simple password should fail default validators
        form = RegistrationForm(data={
            "username": "charlie",
            "password1": "12345678",
            "password2": "12345678",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)  # UserCreationForm aggregates here

    def test_duplicate_username_rejected(self):
        """An existing username causes a validation error on 'username'."""

        User.objects.create_user(username="dana", password="SomePassw0rd!")
        form = RegistrationForm(data={
            "username": "dana",
            "password1": "AnotherPassw0rd!",
            "password2": "AnotherPassw0rd!",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class LoginFormTests(TestCase):
    """Form-level tests for LoginForm (AuthenticationForm-based)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="henry",
            password="StrongPassw0rd!"
        )

    def test_valid_credentials_authenticate_user(self):
        """Valid username/password combination authenticates successfully."""
        form = LoginForm(request=None, data={
            "username": "henry",
            "password": "StrongPassw0rd!"
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.get_user()
        self.assertEqual(user, self.user)

    def test_invalid_credentials_rejected(self):
        """Incorrect password should invalidate the form and show non-field error."""
        form = LoginForm(request=None, data={
            "username": "henry",
            "password": "WrongPassword!"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_blank_username_is_invalid(self):
        """Missing username should trigger field error."""
        form = LoginForm(request=None, data={
            "username": "",
            "password": "StrongPassw0rd!"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_blank_password_is_invalid(self):
        """Missing password should trigger field error."""
        form = LoginForm(request=None, data={
            "username": "henry",
            "password": ""
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_remember_me_field_present_and_optional(self):
        """'Se souvenir de moi' checkbox should exist but not be required."""
        form = LoginForm()
        self.assertIn("remember_me", form.fields)
        self.assertFalse(form.fields["remember_me"].required)
