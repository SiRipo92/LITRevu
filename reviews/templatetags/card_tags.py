from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from reviews.models import Ticket, Review

register = template.Library()


@register.simple_tag(takes_context=True)
def render_card_grid(context, item):
    """
    Render a single feed item (Ticket or Review) with the correct card template.

    - On feed: show review actions (e.g. "Créer une critique") but no edit/delete.
    - On "Mes Posts": show Modifier / Supprimer buttons for the user's own posts.
    """
    request = context.get("request")
    is_my_posts_page = context.get("is_my_posts_page", False)

    if isinstance(item, Ticket):
        html = render_to_string(
            "reviews/components/ticket_card.html",
            {
                "ticket": item,
                "request": request,
                "show_actions": True,                      # base actions zone
                "allow_review": not is_my_posts_page,      # feed: True, my posts: False
                "allow_edit_delete": is_my_posts_page,     # feed: False, my posts: True
            },
        )
        return mark_safe(html)

    if isinstance(item, Review):
        html = render_to_string(
            "reviews/components/review_card.html",
            {
                "review": item,
                "request": request,
                "show_ticket": True,
                "allow_edit_delete": is_my_posts_page,     # only on "Mes Posts"
            },
        )
        return mark_safe(html)

    return ""
