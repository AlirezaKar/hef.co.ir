"""Replace Django technical error pages with safe user-facing responses."""

from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from config import error_views

logger = logging.getLogger(__name__)


class FriendlyErrorMiddleware(MiddlewareMixin):
    """
    Show friendly Persian error pages instead of yellow technical screens,
    but ONLY when DEBUG=False.  When DEBUG=True the default Django debug
    screens (yellow traceback) are preserved so developers can debug.
    """

    def process_exception(self, request, exception):
        # Let Django's built-in debug views handle everything in dev mode.
        from django.conf import settings
        if settings.DEBUG:
            return None

        if isinstance(exception, Http404):
            return error_views.not_found(request, exception)

        if isinstance(exception, PermissionDenied):
            return error_views.permission_denied(request, exception)

        if isinstance(exception, SuspiciousOperation):
            return error_views.bad_request(request, exception)

        # Unexpected errors: log server-side only
        logger.exception("Unhandled exception on %s", request.path)
        return error_views.server_error(request)
