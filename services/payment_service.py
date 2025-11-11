"""Simulated external payment gateway integration layer."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Dict, Optional


class PaymentGatewayError(RuntimeError):
    """Represents failures returned by the remote payment provider."""


@dataclass(frozen=True)
class PaymentResult:
    transaction_id: str
    status: str
    amount: float
    patron_id: str
    description: Optional[str] = None


class PaymentGateway:
    """Simple in-memory payment gateway used to emulate a third-party API.

    The implementation is intentionally stateful so developers can manually
    exercise end-to-end flows, but tests should *always* mock this class to
    avoid calling the simulated network boundary.
    """

    def __init__(self) -> None:
        self._transactions: Dict[str, PaymentResult] = {}

    def process_payment(self, patron_id: str, amount: float, description: Optional[str] = None) -> PaymentResult:
        if amount <= 0:
            return PaymentResult(transaction_id="", status="declined", amount=0.0, patron_id=patron_id)
        transaction_id = str(uuid.uuid4())
        result = PaymentResult(transaction_id=transaction_id, status="success", amount=round(amount, 2), patron_id=patron_id, description=description)
        self._transactions[transaction_id] = result
        return result

    def refund_payment(self, transaction_id: str, amount: float) -> PaymentResult:
        if not transaction_id or transaction_id not in self._transactions:
            raise PaymentGatewayError("Transaction not found")
        if amount <= 0 or amount > self._transactions[transaction_id].amount:
            raise PaymentGatewayError("Invalid refund amount")
        refund_id = str(uuid.uuid4())
        return PaymentResult(transaction_id=refund_id, status="refunded", amount=round(amount, 2), patron_id=self._transactions[transaction_id].patron_id)
