"""Witness selection, validation, and quorum enforcement.

Witnesses are critical for fail-closed acceptance. No valid transaction can be
accepted without independent witness verification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set


class WitnessValidationError(RuntimeError):
    """Raised when witness verification fails."""


@dataclass
class WitnessRecord:
    """Represents a witness and its independence group."""

    witness_hash: str
    group: str
    reliability: float = 1.0
    available: bool = True
    last_response: Optional[float] = None


class WitnessManager:
    """Coordinate witness selection and quorum verification."""

    def __init__(self, min_quorum: int = 2, witness_timeout: float = 15.0) -> None:
        self.min_quorum = max(2, min_quorum)
        self.witness_timeout = witness_timeout
        self.witnesses: Dict[str, WitnessRecord] = {}

    def add_witness(self, witness_hash: str, group: str, reliability: float = 1.0) -> WitnessRecord:
        """Add a witness to the registry."""

        record = WitnessRecord(witness_hash=witness_hash, group=group, reliability=reliability)
        self.witnesses[witness_hash] = record
        return record

    def remove_witness(self, witness_hash: str) -> None:
        """Remove a witness from the registry."""

        self.witnesses.pop(witness_hash, None)

    def list_witnesses(self) -> List[WitnessRecord]:
        """Return all known witness records."""

        return list(self.witnesses.values())

    def choose_quorum(self, pair_hash: str) -> List[WitnessRecord]:
        """Select independent witnesses for a verification quorum.

        In a production implementation this method should use local reputation,
        availability, and independence checks. The stub keeps the logic explicit and
        fail-closed: there is no fallback to less-than-minimum quorum.
        """

        candidates = [w for w in self.witnesses.values() if w.available and w.reliability > 0.0]
        selected: List[WitnessRecord] = []
        seen_groups: Set[str] = set()

        for witness in sorted(candidates, key=lambda item: item.reliability, reverse=True):
            if witness.group in seen_groups:
                continue
            seen_groups.add(witness.group)
            selected.append(witness)
            if len(selected) >= self.min_quorum:
                return selected

        raise WitnessValidationError("Insufficient independent witnesses for quorum.")

    def verify_quorum(self, responses: List[Dict[str, Any]], required_quorum: Optional[int] = None) -> bool:
        """Verify the available witness responses meet the minimum quorum."""

        quorum = required_quorum or self.min_quorum
        valid = 0
        for response in responses:
            if response.get("valid") is True:
                valid += 1
        return valid >= quorum

    def timeout_reached(self, responses: List[Dict[str, Any]]) -> bool:
        """Return True when the witness set cannot complete within the configured timeout."""

        if len(responses) < self.min_quorum:
            return True
        return False
