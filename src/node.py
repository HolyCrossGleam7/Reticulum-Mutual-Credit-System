"""Message formats and protocol helpers for secure pairwise exchanges.

The protocol defines the JSON message envelope used across Reticulum transports,
including sender, monotonic counter, nonce, timestamp, and signature.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class ProtocolError(RuntimeError):
    """Raised when a message fails validation or message schema checks."""


@dataclass
class Message:
    """Base transport message."""

    type: str
    sender_hash: str
    counter: int
    nonce: str
    timestamp: float
    signature: str
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable dict for sending over RNS."""

        return {
            "type": self.type,
            "sender_hash": self.sender_hash,
            "counter": self.counter,
            "nonce": self.nonce,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Create a message from a serialized dict."""

        required = {"type", "sender_hash", "counter", "nonce", "timestamp", "signature", "payload"}
        missing = sorted(required - set(data.keys()))
        if missing:
            raise ProtocolError(f"Missing required fields: {missing}")
        return cls(**data)


def make_message(type_name: str, sender_hash: str, payload: Dict[str, Any], counter: int = 0, nonce: Optional[str] = None) -> Message:
    """Factory helper to construct a signed message wrapper."""

    return Message(
        type=type_name,
        sender_hash=sender_hash,
        counter=counter,
        nonce=nonce or f"{type_name}:{counter}:{sender_hash}",
        timestamp=0.0,
        signature="placeholder-signature",
        payload=payload,
    )


VALID_MESSAGE_TYPES = {
    "CREDIT_REQUEST",
    "CREDIT_APPROVAL",
    "CREDIT_REJECTION",
    "BALANCE_QUERY",
    "WITNESS_PULL",
    "WITNESS_RESPONSE",
    "ANCHOR_PUBLISH",
    "ANCHOR_QUERY",
    "BAN_NOTICE",
}
