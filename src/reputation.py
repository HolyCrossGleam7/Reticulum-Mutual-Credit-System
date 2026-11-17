"""Local ban list and signed blackhole list handling.

The fail-closed design uses ban propagation to refuse misbehaving identities at
network entry and to minimize accepted fraud.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class BanNotice:
    """Signed notice identifying an offending peer or witness."""

    offending_hash: str
    proof_hash: str
    signer_hash: str
    signature: str
    persistent: bool = True


class BanList:
    """Local ban list for persistent rejection of known bad actors."""

    def __init__(self) -> None:
        self.banned: Dict[str, BanNotice] = {}

    def ban(self, offending_hash: str, proof_hash: str, signer_hash: str, signature: str) -> BanNotice:
        """Ban an offending hash permanently by default."""

        notice = BanNotice(
            offending_hash=offending_hash,
            proof_hash=proof_hash,
            signer_hash=signer_hash,
            signature=signature,
            persistent=True,
        )
        self.banned[offending_hash] = notice
        return notice

    def is_banned(self, peer_hash: str) -> bool:
        """Return True if the peer must be refused before any application data exchange."""

        return peer_hash in self.banned

    def consume_blackhole(self, blackhole: Dict[str, str]) -> None:
        """Consume a signed blackhole list by opt-in policy."""

        offending = blackhole.get("offending_hash")
        if offending:
            self.banned[offending] = BanNotice(
                offending_hash=offending,
                proof_hash=blackhole.get("proof_hash", ""),
                signer_hash=blackhole.get("signer_hash", ""),
                signature=blackhole.get("signature", ""),
                persistent=True,
            )
