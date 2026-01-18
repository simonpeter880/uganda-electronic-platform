"""
Shared HTTP client utilities for payment APIs
Provides retry logic, error handling, and structured responses
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests
import logging

logger = logging.getLogger(__name__)


class PaymentAPIError(Exception):
    """Base exception for payment API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, payload: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def __str__(self):
        if self.status_code:
            return f"{self.message} (HTTP {self.status_code})"
        return self.message


@dataclass
class HTTPResponse:
    """Structured HTTP response"""
    status_code: int
    data: Any
    headers: Dict[str, str]


class RetryingSession:
    """
    HTTP client with automatic retry logic:
    - Retries on network errors + 429/5xx status codes
    - Exponential backoff between retries
    - Configurable timeouts
    - Request/response logging
    """

    def __init__(
        self,
        timeout: Tuple[float, float] = (5.0, 30.0),
        max_retries: int = 3,
        backoff: float = 0.6
    ):
        """
        Initialize retry session

        Args:
            timeout: Tuple of (connect_timeout, read_timeout) in seconds
            max_retries: Maximum number of retry attempts
            backoff: Base backoff time in seconds (multiplied by 2^attempt)
        """
        self.s = requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        json_body: Any = None
    ) -> HTTPResponse:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            headers: Request headers
            json_body: Optional JSON body for POST/PUT requests

        Returns:
            HTTPResponse with status, data, and headers

        Raises:
            PaymentAPIError: On network error or max retries exceeded
        """
        last_err: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                # Log request details
                logger.info(f"{method} {url} (attempt {attempt + 1}/{self.max_retries + 1})")

                r = self.s.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_body,
                    timeout=self.timeout,
                )

                # Log response status
                logger.info(f"Response: HTTP {r.status_code} from {url}")

                # Retry on rate limit / server issues
                if r.status_code in (429, 500, 502, 503, 504) and attempt < self.max_retries:
                    retry_after = r.headers.get('Retry-After')
                    wait_time = self.backoff * (2 ** attempt)

                    if retry_after:
                        try:
                            wait_time = float(retry_after)
                        except ValueError:
                            pass

                    logger.warning(
                        f"HTTP {r.status_code} from {url}, retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                # Parse JSON if possible
                try:
                    data = r.json()
                except Exception:
                    data = r.text

                return HTTPResponse(
                    status_code=r.status_code,
                    data=data,
                    headers=dict(r.headers)
                )

            except requests.RequestException as e:
                last_err = e
                logger.error(f"Request exception calling {url}: {e}")

                if attempt < self.max_retries:
                    wait_time = self.backoff * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                raise PaymentAPIError(
                    f"Network error calling {url}: {e}"
                ) from e

        raise PaymentAPIError(f"Request failed after {self.max_retries} retries: {last_err}")


def new_idempotency_key(prefix: str = "pay") -> str:
    """
    Generate unique idempotency key for payment requests

    Args:
        prefix: Prefix for the key (e.g., 'mtn', 'airtel', 'pay')

    Returns:
        Unique idempotency key string
    """
    return f"{prefix}_{uuid.uuid4().hex}"


def safe_json_parse(text: str, default: Any = None) -> Any:
    """
    Safely parse JSON with fallback

    Args:
        text: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(text)
    except Exception:
        return default
