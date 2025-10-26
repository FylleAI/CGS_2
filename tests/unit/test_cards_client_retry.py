"""
Unit tests for Cards Client retry logic.

Tests:
- Retry on 429 (rate limit)
- Retry on 5xx (server errors)
- No retry on 4xx (client errors, except 429)
- Retry on timeout
"""

import pytest
from unittest.mock import Mock, patch
import httpx

from fylle_cards_client.client import _should_retry_on_error


class TestRetryLogic:
    """Test retry logic for Cards API client."""
    
    def test_should_retry_on_timeout(self):
        """Test retry on timeout exception."""
        exception = httpx.TimeoutException("Request timeout")
        assert _should_retry_on_error(exception) is True
    
    def test_should_retry_on_429(self):
        """Test retry on 429 (rate limit)."""
        response = Mock()
        response.status_code = 429
        exception = httpx.HTTPStatusError(
            "Rate limit exceeded",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is True
    
    def test_should_retry_on_500(self):
        """Test retry on 500 (internal server error)."""
        response = Mock()
        response.status_code = 500
        exception = httpx.HTTPStatusError(
            "Internal server error",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is True
    
    def test_should_retry_on_502(self):
        """Test retry on 502 (bad gateway)."""
        response = Mock()
        response.status_code = 502
        exception = httpx.HTTPStatusError(
            "Bad gateway",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is True
    
    def test_should_retry_on_503(self):
        """Test retry on 503 (service unavailable)."""
        response = Mock()
        response.status_code = 503
        exception = httpx.HTTPStatusError(
            "Service unavailable",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is True
    
    def test_should_not_retry_on_400(self):
        """Test no retry on 400 (bad request)."""
        response = Mock()
        response.status_code = 400
        exception = httpx.HTTPStatusError(
            "Bad request",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is False
    
    def test_should_not_retry_on_401(self):
        """Test no retry on 401 (unauthorized)."""
        response = Mock()
        response.status_code = 401
        exception = httpx.HTTPStatusError(
            "Unauthorized",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is False
    
    def test_should_not_retry_on_403(self):
        """Test no retry on 403 (forbidden)."""
        response = Mock()
        response.status_code = 403
        exception = httpx.HTTPStatusError(
            "Forbidden",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is False
    
    def test_should_not_retry_on_404(self):
        """Test no retry on 404 (not found)."""
        response = Mock()
        response.status_code = 404
        exception = httpx.HTTPStatusError(
            "Not found",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is False
    
    def test_should_not_retry_on_422(self):
        """Test no retry on 422 (unprocessable entity)."""
        response = Mock()
        response.status_code = 422
        exception = httpx.HTTPStatusError(
            "Unprocessable entity",
            request=Mock(),
            response=response,
        )
        assert _should_retry_on_error(exception) is False
    
    def test_should_not_retry_on_other_exception(self):
        """Test no retry on other exceptions."""
        exception = ValueError("Some other error")
        assert _should_retry_on_error(exception) is False

