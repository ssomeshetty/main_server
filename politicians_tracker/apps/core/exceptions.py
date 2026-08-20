"""
Custom exception handlers for the Karnataka Politicians Tracker.

This module provides custom exception handling for API responses.
Suppresses internal details in production to prevent information leakage.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that adds additional context to error responses.

    This handler:
    - Logs all exceptions with context
    - Adds machine-readable error code to responses
    - Provides consistent error format
    - HIDES sensitive info in production (no ORM field names, no stack traces)
    """
    # Call DRF's default exception handler
    response = exception_handler(exc, context)

    if response is not None:
        error_code = get_error_code(exc)

        # Log the full error for debugging (server-side only)
        view = context.get('view', None)
        view_name = view.__class__.__name__ if view else 'unknown'
        logger.warning(
            'API Error [%s] in %s: %s',
            error_code, view_name, str(exc),
            exc_info=not settings.DEBUG  # Full traceback in production logs
        )

        # Build safe error response
        error_data = {
            'error': {
                'code': error_code,
                'message': _get_safe_message(exc, response),
            }
        }

        # Only include details in DEBUG mode (never in production)
        if settings.DEBUG:
            error_data['error']['details'] = response.data

        response.data = error_data

    return response


def _get_safe_message(exc, response):
    """
    Return a user-safe error message.
    In production, map to generic messages to prevent information leakage.
    """
    if settings.DEBUG:
        return response.data.get('detail', str(exc))

    # Safe generic messages for production
    status_messages = {
        400: 'Invalid request.',
        401: 'Authentication required.',
        403: 'Access denied.',
        404: 'Resource not found.',
        405: 'Method not allowed. This is a read-only API.',
        429: 'Too many requests. Please try again later.',
        500: 'An internal error occurred. Please try again later.',
    }
    return status_messages.get(
        response.status_code,
        'An error occurred.'
    )


def get_error_code(exception):
    """
    Get a machine-readable error code from an exception.

    Args:
        exception: The exception instance

    Returns:
        str: A machine-readable error code
    """
    # Map specific exception types to error codes
    error_map = {
        'DoesNotExist': 'not_found',
        'ValidationError': 'validation_error',
        'PermissionDenied': 'permission_denied',
        'MethodNotAllowed': 'method_not_allowed',
        'NotAuthenticated': 'authentication_required',
        'AuthenticationFailed': 'authentication_failed',
        'Throttled': 'rate_limit_exceeded',
        'NotFound': 'not_found',
    }

    # Get exception class name
    exception_class = exception.__class__.__name__

    # Look up error code
    for exc_type, error_code in error_map.items():
        if exc_type in exception_class:
            return error_code

    # Default to server error
    return 'server_error'


class APIException(Exception):
    """
    Base exception for API-related errors.

    Usage:
        raise APIException('Error message', code='error_code', http_status=400)
    """

    def __init__(self, message, code=None, http_status_code=None, details=None):
        self.message = message
        self.code = code or 'api_error'
        self.http_status_code = http_status_code or 500
        self.details = details or {}
        super().__init__(message)


class BadRequestException(APIException):
    """Exception for bad request errors."""

    def __init__(self, message='Bad request', details=None):
        super().__init__(message, code='bad_request', http_status_code=400, details=details)


class NotFoundException(APIException):
    """Exception for resource not found errors."""

    def __init__(self, resource='Resource', identifier=None):
        message = f'{resource} not found'
        if identifier:
            message += f' with identifier {identifier}'
        super().__init__(message, code='not_found', http_status_code=404)


class PermissionDeniedException(APIException):
    """Exception for permission denied errors."""

    def __init__(self, message='Permission denied'):
        super().__init__(message, code='permission_denied', http_status_code=403)


class ReadOnlyModeException(APIException):
    """Exception for read-only mode violations."""

    def __init__(self, operation='Operation'):
        super().__init__(
            f'{operation} not allowed in read-only mode',
            code='read_only_mode',
            http_status_code=405
        )
