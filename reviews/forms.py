# reviews/forms.py
from django import forms
from .models import Ticket


# Base class to remove trailing colons from labels
class NoColonLabelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label_suffix = ""  # removes the colon automatically


class CreateTicketForm(NoColonLabelForm):  # inherit from NoColonLabelForm
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
                    "class": "w-full mt-4 border border-gray-300 rounded p-2 "
                             "focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full mt-4 border border-gray-300 rounded p-2 min-h-[250px] "
                             "focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "hidden",
                    "accept": "image/*",
                    "id": "id_image",
                }
            ),
        }
