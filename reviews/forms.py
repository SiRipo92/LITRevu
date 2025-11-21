from django import forms
from django.core.exceptions import ValidationError
from .models import Ticket, Review


# Base class to remove trailing colons from labels
class NoColonLabelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label_suffix = ""  # removes the colon automatically


class CreateTicketForm(NoColonLabelForm):  # inherit from NoColonLabelForm
    # Explicitly define the image field to avoid ClearableFileInput
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                "id": "id_image",
                "class": "hidden",  # you keep it hidden, JS drives it
                "accept": "image/*",
            }
        ),
        label="Image",  # keeps the label text consistent if you ever call .label_tag
    )

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]

        labels = {
            "title": "Titre",
            "description": "Description",
            "image": "Image",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "id": "id_title",
                    "class": "w-full mt-4 border border-gray-300 rounded p-2 "
                             "focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "id": "id_description",
                    "class": "w-full mt-4 border border-gray-300 rounded p-2 min-h-[250px] "
                             "focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                }
            ),
        }


class ReviewForm(NoColonLabelForm):
    """
    Form to create a review either in response to a ticket or as a standalone.

    When instantiated with keyword arguments `user` and `ticket`, the form
    validates that the user has not already reviewed the given ticket, raising a
    ValidationError before the DB unique constraint.
    """

    # Use a TypedChoiceField to control choices/labels and coerce to int
    rating = forms.TypedChoiceField(
        label="Note",
        choices=[(i, f"- {i}") for i in range(6)],  # "- 0" … "- 5"
        coerce=int,
        widget=forms.RadioSelect(),
    )

    class Meta:
        model = Review
        fields = ("headline", "rating", "body")
        labels = {
            "headline": "Titre",
            "body": "Commentaire",
        }
        widgets = {
            "headline": forms.TextInput(attrs={
                "class": "border border-gray-300 rounded-md px-4 py-2 w-full"
            }),
            "body": forms.Textarea(attrs={
                "class": "border border-gray-300 rounded-md px-4 py-2 w-full",
                "rows": 5
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.ticket = kwargs.pop("ticket", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        if self.user and self.ticket:
            if Review.objects.filter(user=self.user, ticket=self.ticket).exists():
                raise ValidationError("Vous avez déjà publié une critique pour ce ticket.")
        return data
