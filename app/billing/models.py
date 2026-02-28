"""
PIEE — Billing Pydantic Schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class WalletBalance(BaseModel):
    balance: float
    currency: str = "USD"
    unlimited: bool = False  # True in local mode


class Transaction(BaseModel):
    id: str
    amount: float
    type: str  # topup | usage | refund | adjustment
    description: Optional[str]
    reference_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionList(BaseModel):
    transactions: List[Transaction]
    total_count: int


class TopupRequest(BaseModel):
    amount: float
    payment_method: Optional[str] = None
