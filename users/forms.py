"""Defines Registration and Login Form logic for landing page and form pages."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class RegistrationForm(UserCreationForm):
    """
    User registration form based on Django's UserCreationForm.

    Exposes only the `username` field (password1/password2 are provided by
    the base class) and applies Tailwind-compatible widget classes for
    consistent styling in templates.
    """

    class Meta:
        """
        Metadata linking the form to the custom User model.

        Fields:
            username: The unique username for the new account.
            (password1/password2 are inherited from UserCreationForm.)
        """

        model = User
        fields = ('username',)  # password1/password2 come from UserCreationForm

    # Tailwind-friendly widgets
    def __init__(self, *args, **kwargs):
        """
        Attach Tailwind utility classes to all rendered widgets.

        This keeps templates clean: templates can render {{ form.* }} without
        repeating CSS classes. Adjust here if you change your design system.
        """
        super().__init__(*args, **kwargs)
        # Common Tailwind classes for all inputs
        base_classes = (
            "border border-gray-300 rounded-md px-4 py-2 w-full "
            "text-left placeholder:text-center "
            "text-gray-800 placeholder-gray-400 bg-white "
            "focus:outline-none focus:ring-2 focus:ring-blue-500 "
            "focus:border-blue-500 transition"
        )

        # Assign consistent styling + placeholders
        self.fields["username"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "Nom d'utilisateur",
        })
        self.fields["password1"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "Mot de passe",
        })
        self.fields["password2"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "Confirmer mot de passe",
        })


class LoginForm(AuthenticationForm):
    """Custom login form with Tailwind CSS styling and placeholders."""

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        }),
        label="Se souvenir de moi"
    )

    def __init__(self, *args, **kwargs):
        """Initialize the LoginForm."""
        super().__init__(*args, **kwargs)

        base_classes = (
            "border border-gray-300 rounded-md px-4 py-2 w-full "
            "text-left placeholder:text-center "
            "text-gray-800 placeholder-gray-400 bg-white "
            "focus:outline-none focus:ring-2 focus:ring-blue-500 "
            "focus:border-blue-500 transition"
        )

        # Apply consistent classes and placeholders
        self.fields["username"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "Nom d'utilisateur",
            "aria-label": "Nom d'utilisateur",
        })
        self.fields["password"].widget.attrs.update({
            "class": base_classes,
            "placeholder": "Mot de passe",
            "aria-label": "Mot de passe",
        })
