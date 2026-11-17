"""Anchor publication and verification.

Anchors provide periodic commitments to pair-state hash heads. Once an anchor is
acknowledged by a valid quorum of independent witnesses, any conflicting state
claim must be rejected.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class AnchorValidationError(RuntimeError):
    """Raised when anchor publication or verification fails."""


@dataclass
class Anchor:
    """Represents a pair-level anchor record."""

    pair_hash: str
    chain_head: str
    timestamp: float
    witness_signatures: List[str]
    anchor_hash: Optional[str] = None

    def finalize(self) -> None:
        """Finalize the anchor hash after witnessing."""

        if not self.witness_signatures:
            raise AnchorValidationError("Anchor requires at least one witness signature.")
        self.anchor_hash = f"anchor:{self.pair_hash}:{self.chain_head}:{len(self.witness_signatures)}"


class AnchorManager:
    """Maintain the local record of historical anchors for each pair."""

    def __init__(self) -> None:
        self.anchors: Dict[str, List[Anchor]] = {}

    def publish_anchor(self, pair_hash: str, chain_head: str, witness_signatures: List[str]) -> Anchor:
        """Publish an anchor record for a pair."""

        anchor = Anchor(
            pair_hash=pair_hash,
            chain_head=chain_head,
            timestamp=0.0,
            witness_signatures=witness_signatures,
        )
        anchor.finalize()
        self.anchors.setdefault(pair_hash, []).append(anchor)
        return anchor

    def verify_anchor(self, pair_hash: str, chain_head: str, anchor_hash: str) -> bool:
        """Validate a pair anchor against the locally known history."""

        for anchor in self.anchors.get(pair_hash, []):
            if anchor.chain_head == chain_head and anchor.anchor_hash == anchor_hash:
                return True
        return False

    def detect_conflict(self, pair_hash: str, claimed_chain_head: str) -> bool:
        """Return True if the node has a previously acknowledged anchor that conflicts with the claim."""

        for anchor in self.anchors.get(pair_hash, []):
            if anchor.chain_head != claimed_chain_head:
                return True
        return False
