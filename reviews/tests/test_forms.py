"""Tests behavior for Ticket form."""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from reviews.forms import CreateTicketForm


class CreateTicketFormTests(TestCase):
    """Unit tests validating the behavior and presentation of CreateTicketForm."""

    def test_valid_without_image(self):
        """Form is valid when only title and description are provided (no image)."""
        form = CreateTicketForm(data={"title": "A title", "description": "desc"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_with_image(self):
        """Form accepts a small valid image upload and remains valid."""
        fake_img = SimpleUploadedFile(
            "tiny.gif",
            b"GIF89a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff!\xf9\x04"
            b"\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",  # 1x1 gif
            content_type="image/gif",
        )
        form = CreateTicketForm(
            data={"title": "With image", "description": "ok"},
            files={"image": fake_img},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_title_is_required(self):
        """Blank title should invalidate the form and surface an error on 'title'."""
        form = CreateTicketForm(data={"title": "", "description": "x"})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_title_max_length_enforced(self):
        """Titles longer than 128 chars are rejected with an error on 'title'."""
        form = CreateTicketForm(data={"title": "x" * 129, "description": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_colon_removed_from_labels_and_widget_attrs_present(self):
        """
        Labels are rendered without trailing colons and widgets expose expected attrs.

        - Verifies human-friendly labels ("Titre", "Description", "Image").
        - Spot-checks Tailwind classes on text inputs.
        - Confirms image input has id, 'hidden' class, and accept='image/*'.
        """
        form = CreateTicketForm()
        # No trailing colon on labels
        self.assertEqual(form.fields["title"].label, "Titre")
        self.assertEqual(form.fields["description"].label, "Description")
        self.assertEqual(form.fields["image"].label, "Image")

        # CSS classes present (spot-check one per field)
        self.assertIn("w-full", form.fields["title"].widget.attrs.get("class", ""))
        self.assertIn("w-full", form.fields["description"].widget.attrs.get("class", ""))

        # Image input is hidden with id/accept attributes (used by your JS)
        img_attrs = form.fields["image"].widget.attrs
        self.assertEqual(img_attrs.get("id"), "id_image")
        self.assertIn("hidden", img_attrs.get("class", ""))
        self.assertEqual(img_attrs.get("accept"), "image/*")
