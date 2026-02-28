"""
PIEE — Billing Router

Endpoints for credit wallet management.
Cloud-only features are guarded by feature flags.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.billing.models import TopupRequest, Transaction, TransactionList, WalletBalance
from app.billing.service import BillingService
from app.config import Settings, get_settings
from app.dependencies import get_current_user
from app.flags.service import FeatureFlagService

router = APIRouter(prefix="/billing", tags=["Billing"])


async def _check_billing_enabled(settings: Settings = Depends(get_settings)):
    """Guard: billing must be enabled."""
    flag_service = FeatureFlagService(settings)
    if not await flag_service.is_enabled("billing_enabled"):
        # In local mode, return unlimited
        return False
    return True


@router.get("/balance", response_model=WalletBalance)
async def get_balance(
    user=Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Get current credit balance."""
    flag_service = FeatureFlagService(settings)
    billing_enabled = await flag_service.is_enabled("billing_enabled")

    if not billing_enabled:
        return WalletBalance(balance=0, unlimited=True)

    result = await BillingService.get_balance(user.id)
    return WalletBalance(**result)


@router.get("/transactions", response_model=TransactionList)
async def get_transactions(
    user=Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Get credit transaction history."""
    flag_service = FeatureFlagService(settings)
    if not await flag_service.is_enabled("billing_enabled"):
        return TransactionList(transactions=[], total_count=0)

    records = await BillingService.get_transactions(user.id)
    return TransactionList(
        transactions=[
            Transaction(
                id=r.id,
                amount=r.amount,
                type=r.type,
                description=r.description,
                reference_id=r.referenceId,
                created_at=r.createdAt,
            )
            for r in records
        ],
        total_count=len(records),
    )


@router.post("/topup", response_model=WalletBalance)
async def topup_credits(
    body: TopupRequest,
    user=Depends(get_current_user),
    settings: Settings = Depends(get_settings),
):
    """Top up credits (cloud only)."""
    flag_service = FeatureFlagService(settings)
    if not await flag_service.is_enabled("billing_enabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Billing is not enabled in this deployment mode.",
        )

    if body.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive.",
        )

    success = await BillingService.add_credits(user.id, body.amount)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process top-up.",
        )

    result = await BillingService.get_balance(user.id)
    return WalletBalance(**result)
