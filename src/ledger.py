"""Cryptographic helpers and state validation primitives.

All cryptographic operations intentionally use Reticulum's identity and signing
primitives instead of custom cryptographic code. This module provides wrappers
and validation helpers for signed transactions, hash chains, anchors, and nonce/counter checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Dict, Optional

try:
    import rns
except ImportError:  # pragma: no cover - runtime dependency
    rns = None


@dataclass
class SignedState:
    """Represents a signed bilateral state update."""

    sender_hash: str
    counterparty_hash: str
    amount: int
    timestamp: float
    counter: int
    nonce: str
    prev_state_hash: str
    payload: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None


def _require_rns() -> None:
    if rns is None:
        raise RuntimeError("Reticulum (rns) is required for cryptographic operations.")


def make_identity() -> Any:
    """Create a persistent RNS identity for a node.

    The real implementation should use `rns.Identity()` directly. This stub
    keeps the interface explicit and keeps the project ready for integration.
    """

    _require_rns()
    return rns.Identity()


def sign_payload(identity: Any, payload: Dict[str, Any]) -> str:
    """Sign a JSON-serializable payload using the provided RNS identity."""

    _require_rns()
    if not hasattr(identity, "sign"):
        raise AttributeError("Identity object does not expose a sign() method.")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return identity.sign(canonical)


def verify_signature(identity_hash: str, payload: Dict[str, Any], signature: str) -> bool:
    """Verify a signature against a known identity hash.

    The real implementation should check `RNS`-based signatures over the canonicalized payload.
    """

    _require_rns()
    if not hasattr(rns, "verify"):
        raise NotImplementedError("rns.verify is unavailable in the installed Reticulum library.")
    return bool(rns.verify(identity_hash, payload, signature))


def canonical_json(data: Dict[str, Any]) -> str:
    """Return a canonical JSON representation for hashing and signing."""

    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_payload(payload: Dict[str, Any]) -> str:
    """Return a stable SHA-256 hash of a signed payload."""

    return sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def compute_prev_state_hash(previous_hash: Optional[str], state: Dict[str, Any]) -> str:
    """Compute the next pair-state hash from the previous value and the current state."""

    combined = canonical_json({"previous": previous_hash or "", "state": state})
    return sha256(combined.encode("utf-8")).hexdigest()


def verify_counter_regression(current: int, previous: Optional[int]) -> bool:
    """Return True when the current counter is at least as high as the previous value."""

    if previous is None:
        return True
    return current >= previous


def verify_nonce_reuse(nonce: str, seen_nonces: set[str]) -> bool:
    """Reject repeated nonce usage for the same pair and direction."""

    if nonce in seen_nonces:
        return False
    return True


def derive_anchor_hash(pair_state_hash: str, witness_hashes: list[str]) -> str:
    """Create an anchor commitment tied to the current chain head and witness set."""

    payload = {"pair_state_hash": pair_state_hash, "witness_hashes": sorted(witness_hashes)}
    return sha256(canonical_json(payload).encode("utf-8")).hexdigest()
