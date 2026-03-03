"""
PIEE — Billing / Credit Wallet Service

Credit wallet logic for cloud mode.
In local mode, returns unlimited balance (guarded by feature flag).
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BillingService:
    """Manages credit wallet operations."""

    @staticmethod
    async def get_balance(user_id: str) -> dict:
        """Get wallet balance for a user."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                wallet = await db.creditwallet.find_unique(where={"userId": user_id})
                if wallet:
                    return {
                        "balance": wallet.balance,
                        "currency": wallet.currency,
                        "unlimited": False,
                    }
                else:
                    # Auto-create wallet
                    wallet = await db.creditwallet.create(
                        data={"userId": user_id, "balance": 0}
                    )
                    return {
                        "balance": 0,
                        "currency": "USD",
                        "unlimited": False,
                    }
            finally:
                await db.disconnect()
        except Exception as e:
            logger.warning(f"Failed to get balance: {e}")
            return {"balance": 0, "currency": "USD", "unlimited": False}

    @staticmethod
    async def deduct_credits(
        user_id: str, amount: float, reference_id: Optional[str] = None
    ) -> bool:
        """Deduct credits from wallet. Returns False if insufficient."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                wallet = await db.creditwallet.find_unique(where={"userId": user_id})
                if not wallet:
                    wallet = await db.creditwallet.create(
                        data={"userId": user_id, "balance": 0}
                    )

                if wallet.balance < amount:
                    return False

                await db.creditwallet.update(
                    where={"userId": user_id},
                    data={"balance": wallet.balance - amount},
                )

                # Record transaction
                await db.credittransaction.create(
                    data={
                        "walletId": wallet.id,
                        "amount": -amount,
                        "type": "usage",
                        "description": f"Model usage charge",
                        "referenceId": reference_id,
                    }
                )

                return True
            finally:
                await db.disconnect()
        except Exception as e:
            logger.warning(f"Failed to deduct credits: {e}")
            return False

    @staticmethod
    async def add_credits(
        user_id: str,
        amount: float,
        transaction_type: str = "topup",
        description: Optional[str] = None,
    ) -> bool:
        """Add credits to wallet."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                wallet = await db.creditwallet.find_unique(where={"userId": user_id})
                if not wallet:
                    wallet = await db.creditwallet.create(
                        data={"userId": user_id, "balance": 0}
                    )

                await db.creditwallet.update(
                    where={"userId": user_id},
                    data={"balance": wallet.balance + amount},
                )

                await db.credittransaction.create(
                    data={
                        "walletId": wallet.id,
                        "amount": amount,
                        "type": transaction_type,
                        "description": description or f"Credit top-up: ${amount}",
                    }
                )

                return True
            finally:
                await db.disconnect()
        except Exception as e:
            logger.warning(f"Failed to add credits: {e}")
            return False

    @staticmethod
    async def get_transactions(user_id: str, limit: int = 50) -> list:
        """Get transaction history."""
        try:
            from prisma import Prisma

            db = Prisma()
            await db.connect()
            try:
                wallet = await db.creditwallet.find_unique(where={"userId": user_id})
                if not wallet:
                    return []

                transactions = await db.credittransaction.find_many(
                    where={"walletId": wallet.id},
                    order={"createdAt": "desc"},
                    take=limit,
                )
                return transactions
            finally:
                await db.disconnect()
        except Exception:
            return []
