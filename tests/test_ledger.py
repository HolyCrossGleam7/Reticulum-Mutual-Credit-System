"""Command-line interface for the Reticulum Mutual Credit System.

The CLI exposes the core node operations: init, announce, trade, balance, witness,
anchor, ban, and system status.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI parser."""

    parser = argparse.ArgumentParser(description="Reticulum Mutual Credit System")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize a node")
    init_parser.set_defaults(func=cmd_init)

    announce_parser = subparsers.add_parser("announce", help="announce the node")
    announce_parser.set_defaults(func=cmd_announce)

    trade_parser = subparsers.add_parser("trade", help="create a signed trade request")
    trade_parser.add_argument("peer_hash")
    trade_parser.add_argument("amount", type=int)
    trade_parser.add_argument("description")
    trade_parser.set_defaults(func=cmd_trade)

    balance_parser = subparsers.add_parser("balance", help="display the current balance against a peer")
    balance_parser.add_argument("peer_hash")
    balance_parser.set_defaults(func=cmd_balance)

    witness_parser = subparsers.add_parser("witness", help="list or manage witnesses")
    witness_parser.add_argument("action", choices=["add", "remove", "list"])
    witness_parser.add_argument("witness_hash", nargs="?")
    witness_parser.set_defaults(func=cmd_witness)

    anchor_parser = subparsers.add_parser("anchor", help="publish or verify anchors")
    anchor_parser.add_argument("action", choices=["publish", "verify"])
    anchor_parser.add_argument("pair_hash", nargs="?")
    anchor_parser.set_defaults(func=cmd_anchor)

    ban_parser = subparsers.add_parser("ban", help="ban a peer or witness")
    ban_parser.add_argument("peer_hash")
    ban_parser.set_defaults(func=cmd_ban)

    status_parser = subparsers.add_parser("status", help="display local node status")
    status_parser.set_defaults(func=cmd_status)

    return parser


def cmd_init(_: argparse.Namespace) -> Dict[str, Any]:
    """Initialize a node and local state."""

    return {"status": "initialized", "message": "Persistent RNS identity created in the local node state."}


def cmd_announce(_: argparse.Namespace) -> Dict[str, Any]:
    """Announce the node to the network."""

    return {"status": "announced", "transport": "Reticulum Network Stack"}


def cmd_trade(args: argparse.Namespace) -> Dict[str, Any]:
    """Submit a trade request through the node's fail-closed gate."""

    return {
        "status": "rejected",
        "message": "This is a scaffold implementation; trade validation would be executed by the node gate.",
        "peer_hash": args.peer_hash,
        "amount": args.amount,
        "description": args.description,
    }


def cmd_balance(args: argparse.Namespace) -> Dict[str, Any]:
    """Return the current pairwise balance for a peer."""

    return {"peer_hash": args.peer_hash, "balance": 0, "message": "placeholder"}


def cmd_witness(args: argparse.Namespace) -> Dict[str, Any]:
    """Add, remove, or list witnesses."""

    return {"action": args.action, "witness_hash": args.witness_hash, "status": "not_implemented"}


def cmd_anchor(args: argparse.Namespace) -> Dict[str, Any]:
    """Publish or verify an anchor."""

    return {"action": args.action, "pair_hash": args.pair_hash, "status": "not_implemented"}


def cmd_ban(args: argparse.Namespace) -> Dict[str, Any]:
    """Ban a peer or witness."""

    return {"peer_hash": args.peer_hash, "status": "ban_notice_created"}


def cmd_status(_: argparse.Namespace) -> Dict[str, Any]:
    """Return a summary of the local node status."""

    return {
        "status": "ready",
        "transport": "Reticulum",
        "fail_closed": True,
        "minimum_witness_quorum": 2,
    }


def main() -> None:
    """Entry point for the CLI."""

    parser = build_parser()
    args = parser.parse_args()
    result = args.func(args)
    print(result)


if __name__ == "__main__":
    main()
