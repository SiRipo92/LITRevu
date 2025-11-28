"""Toast redirect with messaging for User-Friendly UI."""
from urllib.parse import urlencode

from django.shortcuts import redirect


def redirect_with_toast(request, type_, message, to=None):
    """
    Redirect to a given URL (or the current page) with toast parameters.

    Args:
        request: HttpRequest
        type_: 'success' | 'info' | 'error'
        message: string
        to: optional URL string (default: request.path)

    Returns:
        HttpResponseRedirect
    """
    base_url = to or request.path
    qs = urlencode({"toast_type": type_, "toast_msg": message})
    return redirect(f"{base_url}?{qs}")
