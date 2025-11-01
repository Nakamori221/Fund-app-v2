"""Custom exception classes for error handling"""

from typing import Optional, Dict, Any


class APIException(Exception):
    """Base API Exception"""

    status_code = 500
    error_code = "INTERNAL_ERROR"
    message = "An error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """Validation error"""

    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Validation failed"


class AuthenticationException(APIException):
    """Authentication error"""

    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    message = "Authentication failed"


class AuthorizationException(APIException):
    """Authorization error"""

    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    message = "Permission denied"


class NotFoundException(APIException):
    """Resource not found"""

    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class ConflictException(APIException):
    """Data conflict"""

    status_code = 409
    error_code = "CONFLICT_ERROR"
    message = "Data conflict occurred"


class RateLimitException(APIException):
    """Rate limit exceeded"""

    status_code = 429
    error_code = "RATE_LIMIT_ERROR"
    message = "Too many requests"


class RetryableError(Exception):
    """Base class for retryable errors"""

    pass


class TemporaryError(RetryableError):
    """Temporary errors like timeouts"""

    pass
