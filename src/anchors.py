"""Mutual credit ledger logic and transaction validation.

This module keeps all pairwise credit accounting in one place and enforces the
fail-closed validation invariant: if a transaction cannot be proven valid, it
must be rejected before any state is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .crypto import hash_payload, verify_counter_regression, verify_nonce_reuse


class LedgerValidationError(RuntimeError):
    """Raised when a transaction violates the fail-closed ledger invariants."""


@dataclass
class CreditLine:
    """Local bilateral credit line for one pair of peers."""

    peer_hash: str
    local_hash: str
    credit_limit: int = 0
    balance: int = 0
    counter: int = 0
    prev_state_hash: str = "genesis"
    seen_nonces: set[str] = field(default_factory=set)
    recent_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TransactionRecord:
    """Signed bilateral transaction record."""

    sender_hash: str
    counterparty_hash: str
    amount: int
    timestamp: float
    counter: int
    nonce: str
    prev_state_hash: str
    payload: Dict[str, Any]
    signature: str


class Ledger:
    """Manage bilateral credit lines and local validation of state changes."""

    def __init__(self, local_hash: str) -> None:
        self.local_hash = local_hash
        self.credit_lines: Dict[str, CreditLine] = {}

    def get_or_create_credit_line(self, peer_hash: str, credit_limit: int = 0) -> CreditLine:
        """Create a pair credit line if it does not already exist."""

        if peer_hash not in self.credit_lines:
            self.credit_lines[peer_hash] = CreditLine(
                peer_hash=peer_hash,
                local_hash=self.local_hash,
                credit_limit=credit_limit,
            )
        return self.credit_lines[peer_hash]

    def validate_transaction(self, tx: TransactionRecord, counter_limit: Optional[int] = None) -> None:
        """Reject any non-valid transaction before state mutation."""

        line = self.credit_lines.get(tx.counterparty_hash)
        if line is None:
            raise LedgerValidationError("No bilateral credit line exists for this counterparty.")

        if tx.amount < 0:
            raise LedgerValidationError("Amounts must be non-negative.")

        if not verify_counter_regression(tx.counter, line.counter):
            raise LedgerValidationError("Counter regression detected; possible replay or desync.")

        if not verify_nonce_reuse(tx.nonce, line.seen_nonces):
            raise LedgerValidationError("Nonce reuse detected; reject and consider banning candidate.")

        if tx.prev_state_hash != line.prev_state_hash:
            raise LedgerValidationError("Previous state hash mismatch; chain continuity broken.")

        if counter_limit is not None and tx.counter > counter_limit:
            raise LedgerValidationError("Counter exceeds configured system limit.")

        if line.credit_limit > 0 and tx.amount > line.credit_limit:
            raise LedgerValidationError("Transaction exceeds configured creditor limit.")

        payload_hash = hash_payload(tx.payload)
        if payload_hash != hash_payload({
            "sender_hash": tx.sender_hash,
            "counterparty_hash": tx.counterparty_hash,
            "amount": tx.amount,
            "timestamp": tx.timestamp,
            "counter": tx.counter,
            "nonce": tx.nonce,
            "prev_state_hash": tx.prev_state_hash,
        }):
            raise LedgerValidationError("Transaction payload hash mismatch.")

    def apply_transaction(self, tx: TransactionRecord) -> Dict[str, Any]:
        """Apply an already-validated transaction to the local pair state."""

        self.validate_transaction(tx)

        line = self.credit_lines[tx.counterparty_hash]
        line.balance += tx.amount
        line.counter = max(line.counter, tx.counter)
        line.seen_nonces.add(tx.nonce)
        line.prev_state_hash = hash_payload(tx.payload)
        line.recent_history.append({
            "sender_hash": tx.sender_hash,
            "counterparty_hash": tx.counterparty_hash,
            "amount": tx.amount,
            "counter": tx.counter,
            "nonce": tx.nonce,
            "prev_state_hash": line.prev_state_hash,
        })

        return {
            "peer_hash": tx.counterparty_hash,
            "new_balance": line.balance,
            "new_counter": line.counter,
            "prev_state_hash": line.prev_state_hash,
        }

    def reconstruct_balance(self, peer_hash: str, history: List[Dict[str, Any]]) -> int:
        """Reconstruct the effective balance from a trusted history chain."""

        running_total = 0
        for event in history:
            running_total += int(event.get("amount", 0))
        return running_total

    def verify_pair_state(self, peer_hash: str, history: List[Dict[str, Any]], expected_balance: int) -> bool:
        """Verify that the reconstructed pair state matches the expected balance."""

        return self.reconstruct_balance(peer_hash, history) == expected_balance
