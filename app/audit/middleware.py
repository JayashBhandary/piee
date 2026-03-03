"""
PIEE — Request Logging Middleware

FastAPI middleware that logs every request:
method, path, user, latency, status code.
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("piee.audit")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all incoming requests with timing information.
    Also records audit trail for security-sensitive operations.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Extract basic info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Process the request
        response: Response = await call_next(request)

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Log the request
        logger.info(
            f"{method} {path} → {response.status_code} ({latency_ms}ms) "
            f"[{client_ip}]"
        )

        # Add timing header
        response.headers["X-Response-Time"] = f"{latency_ms}ms"

        # Audit log for sensitive endpoints
        if self._is_audit_worthy(method, path):
            try:
                from app.audit.service import AuditService

                await AuditService.log_audit(
                    action=f"{method.lower()}.{path.strip('/').replace('/', '.')}",
                    ip_address=client_ip,
                    user_agent=user_agent,
                    details={
                        "status_code": response.status_code,
                        "latency_ms": latency_ms,
                    },
                )
            except Exception:
                pass  # Best effort

        return response

    @staticmethod
    def _is_audit_worthy(method: str, path: str) -> bool:
        """Determine if a request should be audit-logged."""
        # Audit all auth operations
        if "/auth/" in path:
            return True
        # Audit all write operations to admin endpoints
        if method in ("POST", "PUT", "PATCH", "DELETE") and "/admin" in path:
            return True
        # Audit billing operations
        if "/billing/" in path:
            return True
        return False
