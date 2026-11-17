"""Reference node implementation for Reticulum-based communication and validation.

The node wraps persistent RNS identity management, local ledger state, witness
verification, and fail-closed transaction gating.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .anchors import AnchorManager
from .banlist import BanList
from .crypto import make_identity
from .ledger import Ledger, LedgerValidationError, TransactionRecord
from .protocol import Message
from .reputation import ReputationTracker
from .witness import WitnessManager, WitnessValidationError


class NodeValidationError(RuntimeError):
    """Raised when a node cannot safely accept or process a transaction."""


@dataclass
class Node:
    """A local Reticulum peer node."""

    name: str
    credit_limit: int = 1000
    min_quorum: int = 2
    witness_timeout: float = 15.0
    ledger: Ledger = field(default_factory=Ledger, init=False)
    witness_manager: WitnessManager = field(default_factory=lambda: WitnessManager(min_quorum=2, witness_timeout=15.0), init=False)
    anchors: AnchorManager = field(default_factory=AnchorManager, init=False)
    banlist: BanList = field(default_factory=BanList, init=False)
    reputation: ReputationTracker = field(default_factory=ReputationTracker, init=False)
    identity: Any = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.identity = make_identity()
        self.ledger = Ledger(local_hash=self.identity.hash)
        self.witness_manager = WitnessManager(min_quorum=self.min_quorum, witness_timeout=self.witness_timeout)

    def announce(self) -> Dict[str, Any]:
        """Announce the node on the network and return its metadata."""

        return {
            "name": self.name,
            "identity_hash": self.identity.hash,
            "status": "announced",
        }

    def trade(self, peer_hash: str, amount: int, description: str, witnesses: Optional[List[str]] = None) -> Dict[str, Any]:
        """Attempt a trade once all fail-closed checks succeed."""

        if amount <= 0:
            raise NodeValidationError("Amount must be positive.")

        if self.banlist.is_banned(peer_hash):
            raise NodeValidationError("Peer is banned; connection refused before any payload exchange.")

        try:
            quorum = self.witness_manager.choose_quorum(peer_hash)
        except WitnessValidationError as exc:
            raise NodeValidationError(f"Quorum not met: {exc}") from exc

        if len(quorum) < self.min_quorum:
            raise NodeValidationError("Witness quorum not reached within configured timeout.")

        tx = TransactionRecord(
            sender_hash=self.identity.hash,
            counterparty_hash=peer_hash,
            amount=amount,
            timestamp=0.0,
            counter=1,
            nonce=f"trade:{self.identity.hash}:{peer_hash}:{amount}",
            prev_state_hash="genesis",
            payload={"amount": amount, "description": description},
            signature="placeholder-signature",
        )

        try:
            self.ledger.validate_transaction(tx)
        except LedgerValidationError as exc:
            raise NodeValidationError(f"Ledger validation failed: {exc}") from exc

        if not self.reputation.can_accept_transaction(peer_hash):
            raise NodeValidationError("Transaction rejected due to insufficient reputation or local trust.")

        return {
            "status": "accepted",
            "peer_hash": peer_hash,
            "amount": amount,
            "quorum_size": len(quorum),
            "identity": self.identity.hash,
        }
