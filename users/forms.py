from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

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
        for name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "border border-gray-300 rounded-md px-4 py-2 w-full"
                         "focus:outline-none focus:ring-2 focus:ring-blue-500"
            })
        self.fields["password1"].widget.attrs.update({
            "class": "border border-gray-300 rounded-md px-4 py-2 w-full "
                     "focus:outline-none focus:ring-2 focus:ring-blue-500"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "border border-gray-300 rounded-md px-4 py-2 w-full "
                     "focus:outline-none focus:ring-2 focus:ring-blue-500"
        })
