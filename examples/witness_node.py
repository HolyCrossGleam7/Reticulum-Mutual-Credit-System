"""Minimal example: two peers trading with a quorum of two witnesses.

This script demonstrates the intended workflow for two nodes and an independent
witness quorum. It is intentionally scaffolded and safe to read without a full
Reticulum runtime.
"""

from __future__ import annotations


def main() -> None:
    """Show a minimal two-peer trade configuration."""

    quorum = 2
    peers = ["peer-alice", "peer-bob"]
    witnesses = ["witness-1", "witness-2"]
    print({
        "quorum": quorum,
        "peers": peers,
        "witnesses": witnesses,
        "status": "simulated trade request prepared",
    })


if __name__ == "__main__":
    main()
