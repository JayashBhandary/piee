"""
PIEE — Provider Registry

Maps provider names to BaseProvider instances.
Handles lazy initialization and decryption of provider API keys.
"""

from __future__ import annotations

from typing import Dict, Optional

from app.config import Settings
from app.providers.base import BaseProvider


class ProviderRegistry:
    """
    Central registry of all available provider adapters.

    Providers are lazily instantiated on first access.
    API keys are decrypted from DB or loaded from env at instantiation time.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._providers: Dict[str, BaseProvider] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Load provider configs from DB and bootstrap from env."""
        if self._initialized:
            return

        # Bootstrap from environment variables
        await self._bootstrap_from_env()

        # Load from database
        await self._load_from_db()

        self._initialized = True

    async def _bootstrap_from_env(self) -> None:
        """Create providers from environment variables (first-run convenience)."""
        from app.providers.openai_provider import OpenAIProvider
        from app.providers.anthropic_provider import AnthropicProvider
        from app.providers.local_provider import LocalProvider

        if self.settings.openai_api_key:
            self._providers["openai"] = OpenAIProvider(
                api_key=self.settings.openai_api_key,
            )

        if self.settings.anthropic_api_key:
            self._providers["anthropic"] = AnthropicProvider(
                api_key=self.settings.anthropic_api_key,
            )

        # Local provider is always available
        self._providers["local"] = LocalProvider(
            base_url=self.settings.local_inference_url,
        )

    async def _load_from_db(self) -> None:
        """Load provider configs from ProviderConfig table."""
        try:
            from prisma import Prisma
            from app.auth.service import AuthService

            db = Prisma()
            await db.connect()
            try:
                configs = await db.providerconfig.find_many(where={"isActive": True})
                auth_service = AuthService(self.settings)

                for config in configs:
                    if config.providerName in self._providers:
                        continue  # Env-bootstrapped providers take precedence

                    api_key = None
                    if config.apiKeyEncrypted:
                        try:
                            api_key = auth_service.decrypt(config.apiKeyEncrypted)
                        except Exception:
                            continue  # Skip if decryption fails

                    provider = self._create_provider(
                        config.providerName,
                        api_key=api_key,
                        base_url=config.baseUrl,
                    )
                    if provider:
                        self._providers[config.providerName] = provider
            finally:
                await db.disconnect()
        except Exception:
            pass  # DB not available — rely on env-bootstrapped providers

    def _create_provider(
        self, name: str, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> Optional[BaseProvider]:
        """Factory method to create a provider by name."""
        from app.providers.openai_provider import OpenAIProvider
        from app.providers.anthropic_provider import AnthropicProvider
        from app.providers.local_provider import LocalProvider

        provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "local": LocalProvider,
        }

        cls = provider_map.get(name)
        if cls:
            return cls(api_key=api_key, base_url=base_url)
        return None

    def get(self, provider_name: str) -> Optional[BaseProvider]:
        """Get an initialized provider by name."""
        return self._providers.get(provider_name)

    def list_providers(self) -> list[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    def is_available(self, provider_name: str) -> bool:
        """Check if a provider is registered and available."""
        return provider_name in self._providers

    async def register(
        self, name: str, provider: BaseProvider, persist: bool = False
    ) -> None:
        """Register a new provider at runtime."""
        self._providers[name] = provider

        if persist:
            try:
                from prisma import Prisma
                from app.auth.service import AuthService

                db = Prisma()
                await db.connect()
                try:
                    auth_service = AuthService(self.settings)
                    encrypted_key = None
                    if provider.api_key:
                        encrypted_key = auth_service.encrypt(provider.api_key)

                    await db.providerconfig.upsert(
                        where={"providerName": name},
                        data={
                            "create": {
                                "providerName": name,
                                "displayName": name.title(),
                                "baseUrl": provider.base_url or "",
                                "apiKeyEncrypted": encrypted_key,
                            },
                            "update": {
                                "baseUrl": provider.base_url or "",
                                "apiKeyEncrypted": encrypted_key,
                                "isActive": True,
                            },
                        },
                    )
                finally:
                    await db.disconnect()
            except Exception:
                pass  # Best effort persistence
