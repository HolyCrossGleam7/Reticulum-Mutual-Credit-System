"""Local viewer-relative reputation tracking.

Reputation is local, pair-specific, and viewer relative. It is never shared as a
global truth source and is used only to prune weak or unreliable witnesses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Reputation:
    """Local trust score for a peer or witness."""

    score: float = 0.0
    successful_settlements: int = 0
    disputed_transactions: int = 0
    witness_accuracy: float = 1.0
    witness_reliability: float = 1.0


class ReputationTracker:
    """Track local trust relationships without global consensus."""

    def __init__(self) -> None:
        self.peer_scores: Dict[str, Reputation] = {}
        self.witness_scores: Dict[str, Reputation] = {}

    def get_peer_reputation(self, peer_hash: str) -> Reputation:
        """Return or initialize the local reputation for a peer."""

        return self.peer_scores.setdefault(peer_hash, Reputation())

    def get_witness_reputation(self, witness_hash: str) -> Reputation:
        """Return or initialize the local reputation for a witness."""

        return self.witness_scores.setdefault(witness_hash, Reputation())

    def update_peer_success(self, peer_hash: str, amount: float = 1.0) -> None:
        """Update the local reputation after a successful settlement or trade."""

        rep = self.get_peer_reputation(peer_hash)
        rep.score += amount
        rep.successful_settlements += 1

    def update_dispute(self, peer_hash: str, amount: float = 1.0) -> None:
        """Reduce peer reputation after a dispute or invalid action."""

        rep = self.get_peer_reputation(peer_hash)
        rep.score -= amount
        rep.disputed_transactions += 1

    def can_accept_transaction(self, peer_hash: str, minimum_score: float = 0.0) -> bool:
        """Accept transactions only when local trust remains above the threshold."""

        rep = self.get_peer_reputation(peer_hash)
        return rep.score >= minimum_score

    def update_witness_response(self, witness_hash: str, valid: bool) -> None:
        """Record witness performance for future quorum selection."""

        rep = self.get_witness_reputation(witness_hash)
        rep.score += 1.0 if valid else -1.0
        rep.witness_accuracy = rep.witness_accuracy if valid else max(0.0, rep.witness_accuracy - 0.1)
        rep.witness_reliability = rep.witness_accuracy
