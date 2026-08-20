from django.utils import translation
from django.conf import settings


class LanguageDetectionMiddleware:
    """
    Middleware to detect and set the language preference for the request.
    
    Priority order:
    1. URL query parameter: ?lang=en or ?lang=kn
    2. Custom header: X-Language: en or kn
    3. Accept-Language header (Django's default language negotiation)
    4. Default language from settings
    
    This middleware activates the appropriate language for the current request
    and makes it available as request.language for serializer-level language selection.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.available_languages = [lang[0] for lang in settings.LANGUAGES]
    
    def __call__(self, request):
        # Get language preference from various sources
        language = self._get_language_from_request(request)
        
        # Validate language
        if language and language in self.available_languages:
            # Activate the language for this request
            translation.activate(language)
            request.language = language
        else:
            # Use default language
            language = settings.LANGUAGE_CODE
            request.language = language.split('-')[0]  # e.g., 'en' from 'en-us'
        
        response = self.get_response(request)
        
        # Deactivate language after response is sent
        translation.deactivate()
        
        return response
    
    def _get_language_from_request(self, request):
        """Extract language preference from request."""
        # Priority 1: Query parameter ?lang=en or ?lang=kn
        lang_param = request.GET.get('lang')
        if lang_param in self.available_languages:
            return lang_param
        
        # Priority 2: Custom header X-Language
        custom_header = request.META.get('HTTP_X_LANGUAGE')
        if custom_header and custom_header in self.available_languages:
            return custom_header
        
        # Priority 3: Accept-Language header (Django's default)
        return translation.get_language_from_request(request)


class ReadOnlyModeMiddleware:
    """
    Middleware to enforce read-only mode for the PUBLIC API.

    Rejects all POST, PUT, PATCH, DELETE requests on API endpoints.
    Returns 405 Method Not Allowed for write operations.
    Exempts admin panel to allow database management.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.read_only_methods = ['POST', 'PUT', 'PATCH', 'DELETE', 'TRACE', 'CONNECT']

    def __call__(self, request):
        # Exempt admin panel from read-only enforcement
        if request.path.startswith('/mgmt-') or request.path.startswith('/admin/'):
            return self.get_response(request)

        # Enforce read-only on all other paths
        if request.method in self.read_only_methods:
            from django.http import HttpResponseNotAllowed
            return HttpResponseNotAllowed(
                ['GET', 'HEAD', 'OPTIONS'],
                content='This API is read-only. No write operations are permitted.'
            )

        return self.get_response(request)


class RequestSanitizationMiddleware:
    """
    Sanitize incoming requests to prevent injection attacks.
    - Strips null bytes from query parameters
    - Rejects requests with suspicious patterns
    - Validates Content-Length header
    """

    BLOCKED_PATTERNS = [
        '\x00',        # Null bytes
        '\r\n\r\n',    # HTTP response splitting
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check query string for null bytes and injection patterns
        query_string = request.META.get('QUERY_STRING', '')
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in query_string:
                from django.http import HttpResponseBadRequest
                return HttpResponseBadRequest('Invalid request parameters.')

        # Validate Content-Length if present
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                cl = int(content_length)
                if cl < 0 or cl > 10 * 1024 * 1024:  # 10MB max
                    from django.http import HttpResponse
                    return HttpResponse('Request too large.', status=413)
            except (ValueError, TypeError):
                from django.http import HttpResponseBadRequest
                return HttpResponseBadRequest('Invalid Content-Length.')

        return self.get_response(request)


class SecurityHeadersMiddleware:
    """
    Add comprehensive security headers to all responses.
    OWASP recommended headers for API protection.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        # Control referrer information
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Restrict browser features
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), '
            'payment=(), usb=(), magnetometer=()'
        )
        # Content Security Policy for API responses
        response['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none'"
        # Prevent caching of sensitive data
        if request.path.startswith('/mgmt-'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'

        return response


class RequestSizeLimitMiddleware:
    """
    Limit query string and URI length to prevent buffer overflow attempts.
    """
    MAX_QUERY_STRING_LENGTH = 2048
    MAX_URI_LENGTH = 4096

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        query_string = request.META.get('QUERY_STRING', '')
        if len(query_string) > self.MAX_QUERY_STRING_LENGTH:
            from django.http import HttpResponse
            return HttpResponse('Query string too long.', status=414)

        request_uri = request.get_full_path()
        if len(request_uri) > self.MAX_URI_LENGTH:
            from django.http import HttpResponse
            return HttpResponse('URI too long.', status=414)

        return self.get_response(request)