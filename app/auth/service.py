"""
PIEE — Auth Service

Business logic for authentication, JWT handling, API key management,
and provider API key encryption/decryption.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet, InvalidToken

from app.config import Settings


# ── Password Hashing ───────────────────────────


class AuthService:
    """Handles JWT, password hashing, API key operations, and encryption."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._fernet: Optional[Fernet] = None
        if settings.encryption_key:
            try:
                self._fernet = Fernet(settings.encryption_key.encode())
            except Exception:
                pass  # Encryption unavailable — logged at startup

    # ── Password ───────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    # ── JWT ─────────────────────────────────────

    def create_jwt(self, user_id: str, email: str, role: str) -> tuple[str, int]:
        """Create a JWT token. Returns (token, expires_in_seconds)."""
        expires_delta = timedelta(minutes=self.settings.jwt_expiration_minutes)
        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        token = jwt.encode(
            payload,
            self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )
        return token, int(expires_delta.total_seconds())

    def decode_jwt(self, token: str) -> Optional[dict]:
        """Decode and validate a JWT. Returns payload or None."""
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
            return payload
        except JWTError:
            return None

    async def verify_jwt(self, token: str):
        """Verify JWT and return the user record from DB."""
        payload = self.decode_jwt(token)
        if not payload or "sub" not in payload:
            return None

        from prisma import Prisma

        db = Prisma()
        await db.connect()
        try:
            user = await db.user.find_unique(where={"id": payload["sub"]})
            if user and user.isActive:
                return user
            return None
        finally:
            await db.disconnect()

    # ── API Keys ───────────────────────────────

    @staticmethod
    def generate_api_key() -> str:
        """Generate a random API key with 'pk-' prefix."""
        return f"pk-{secrets.token_urlsafe(48)}"

    @staticmethod
    def hash_api_key(key: str) -> str:
        """SHA-256 hash the API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def get_key_prefix(key: str) -> str:
        """Return first 11 chars for display (e.g., 'pk-aBcDeFg...')."""
        return key[:11] + "..."

    async def verify_api_key(self, key: str):
        """Verify an API key and return the owning user."""
        key_hash = self.hash_api_key(key)

        from prisma import Prisma

        db = Prisma()
        await db.connect()
        try:
            api_key = await db.apikey.find_unique(
                where={"keyHash": key_hash},
                include={"user": True},
            )
            if not api_key or not api_key.isActive:
                return None
            if api_key.expiresAt and api_key.expiresAt < datetime.now(timezone.utc):
                return None

            # Update last used timestamp
            await db.apikey.update(
                where={"id": api_key.id},
                data={"lastUsedAt": datetime.now(timezone.utc)},
            )

            return api_key.user if api_key.user and api_key.user.isActive else None
        finally:
            await db.disconnect()

    # ── Encryption (for provider API keys) ─────

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string using Fernet. Returns base64 ciphertext."""
        if not self._fernet:
            raise RuntimeError("Encryption key not configured")
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a Fernet-encrypted string."""
        if not self._fernet:
            raise RuntimeError("Encryption key not configured")
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken:
            raise ValueError("Failed to decrypt — invalid key or corrupted data")
