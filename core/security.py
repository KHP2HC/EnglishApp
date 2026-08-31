"""Authentication and authorization for EnglishCoach Pro.

Validates Supabase-issued JWT access tokens and extracts user identity.
Supports role-based authorization (user / admin).

Flow:
    Request
      → Extract Bearer token from Authorization header
      → Validate JWT signature, expiry, audience
      → Extract user identity (sub, email, role)
      → Return AuthenticatedUser
      → Route handler receives authenticated user

The authenticated user identity ALWAYS comes from the validated JWT,
never from request bodies or client-supplied data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import Settings, get_settings

logger = logging.getLogger("englishcoach.security")

# ── Security scheme ─────────────────────────────────────
# auto_error=False so we can return a custom 401 response.
_bearer_scheme = HTTPBearer(auto_error=False)


# ── Authenticated user representation ───────────────────
@dataclass(frozen=True)
class AuthenticatedUser:
    """Safe representation of an authenticated user.

    Only contains non-sensitive fields extracted from the validated JWT.
    Never includes tokens, passwords, or internal identifiers beyond
    what the route handler needs.
    """

    id: str
    email: str | None = None
    role: str = "user"
    # Raw claims for advanced use (never exposed to clients).
    _claims: dict | None = None


# ── JWT validation ─────────────────────────────────────


def _validate_token(token: str, settings: Settings) -> dict:
    """Validate a JWT token and return its claims.

    Raises HTTPException(401) for any validation failure.
    Internal error details are logged but NOT returned to the client.
    """
    if not settings.JWT_SECRET:
        logger.error("JWT_SECRET is not configured — cannot validate tokens")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is not properly configured.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            options={"require": ["exp", "iat", "sub"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.info("Rejected expired JWT")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidAudienceError:
        logger.info("Rejected JWT with invalid audience")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        logger.info("Rejected invalid JWT")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _extract_bearer_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    """Extract and validate the Bearer token from credentials.

    Raises HTTPException(401) if missing or malformed.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if not token or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token.strip()


def _build_user_from_claims(claims: dict) -> AuthenticatedUser:
    """Build an AuthenticatedUser from validated JWT claims.

    The `sub` claim is the canonical user identifier in Supabase JWTs.
    The `role` claim may be present in Supabase JWTs when custom claims
    are configured via a database trigger or auth hook.

    If the `role` claim is absent, the user is treated as a standard
    "user". Admin role assignment should be managed server-side via
    Supabase auth metadata or a database lookup.
    """
    user_id = claims.get("sub", "")
    if not user_id:
        logger.error("JWT payload missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = claims.get("email")
    role = claims.get("role", "user")

    # Normalize role to known values.
    if role not in ("user", "admin"):
        role = "user"

    return AuthenticatedUser(
        id=str(user_id),
        email=email,
        role=role,
        _claims=claims,
    )


# ── Dependencies ────────────────────────────────────────


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> AuthenticatedUser:
    """Validate the Bearer token and return the authenticated user.

    Raises:
        HTTPException(401): Missing, malformed, or invalid token.
    """
    token = _extract_bearer_token(credentials)
    claims = _validate_token(token, settings)
    return _build_user_from_claims(claims)


def get_current_user_id(
    user: AuthenticatedUser = Depends(get_current_user),
) -> str:
    """Return the authenticated user's ID.

    Use this dependency when a route only needs the user ID.
    """
    return user.id


def require_admin(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Require the authenticated user to have the 'admin' role.

    Raises:
        HTTPException(403): User is authenticated but not an admin.
    """
    if user.role != "admin":
        logger.info("Denied admin access to user %s (role=%s)", user.id, user.role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions.",
        )
    return user


def require_roles(*allowed_roles: str):
    """Create a dependency that requires one of the specified roles.

    Usage:
        @app.get(
            "/api/v1/manager-only",
            dependencies=[Depends(require_roles("admin", "manager"))],
        )
        def manager_endpoint(
            user: AuthenticatedUser = Depends(get_current_user),
        ):
            ...
    """
    allowed = set(allowed_roles)

    def _check_role(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if user.role not in allowed:
            logger.info(
                "Denied access to user %s (role=%s, required=%s)",
                user.id,
                user.role,
                allowed,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return user

    return _check_role


# ── Optional auth (for endpoints that work with or without auth) ──


def get_optional_user(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> AuthenticatedUser | None:
    """Return the authenticated user if a valid token is present, else None.

    Useful for endpoints that behave differently for authenticated vs
    anonymous users (e.g., public reading tests with optional personalization).
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:].strip()
    if not token:
        return None

    try:
        claims = _validate_token(token, settings)
        return _build_user_from_claims(claims)
    except HTTPException:
        return None
