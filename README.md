# Reticulum Mutual Credit System

Reticulum Mutual Credit System is a decentralized, peer-to-peer mutual credit ledger built on top of the Reticulum Network Stack (RNS). It intentionally avoids blockchain-style global consensus and instead relies on bilateral accounting, signed state transitions, hash-chain continuity, and fail-closed witness verification.

## Overview

This repository provides a reference implementation scaffold for a trust-based mutual credit system where participants trade goods or services and record obligations as bilateral debits and credits. All communication between nodes is encrypted, infrastructure-less, and routed through Reticulum. Every transaction is verified before it can be accepted, and any failure path rejects the transaction immediately.

## Core principles

- Fail-closed by design: no partial acceptance, no best-effort approval.
- Bilateral credit lines: ledger state is local to each pair of participants.
- RNS-backed identities: `RNS.Identity()` and signed message formats are central.
- Witness verification: independent verification by quorum makes fraud harder to mask.
- Anchors: periodic anchor publication provides tamper-evident checkpoints.
- Ban propagation: signed blackhole notices allow bad actors to be refused at the network edge.
- Sybil resistance: witness registration and anchoring require costly, bootstrapped trust.

## Repository layout

- `docs/` — architecture, model, verification, threat model, and security guidance
- `src/` — core implementation modules
- `tests/` — unit, integration, and fail-closed verification tests
- `examples/` — working examples and configuration templates

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.cli init
python -m src.cli announce
python -m src.cli witness list
python -m src.cli status
```

## End-to-end flow

1. Initialize a node and create a persistent RNS identity.
2. Announce the node to the local Reticulum network.
3. Register at least two independent witnesses.
4. Open or settle a bilateral credit line.
5. Submit a transaction with `trade <peer_hash> <amount> <desc>`.
6. The node verifies signatures, counters, chain continuity, witness quorum, and anchor consistency before accepting the record.
7. If any verification step fails, the transaction is rejected and the failure is logged.

## Failure scenarios documented in this project

- tampered local JSON cache is rejected
- witness timeout results in rejection
- chain break or anchor mismatch is rejected
- nonce reuse or counter regression triggers rejection and ban candidate reporting
- quorum failure or independence rule violation blocks all acceptance

## Security posture

This project is intentionally strict and conservative. The fail-closed invariant is enforced in code, documentation, and tests. A transaction is accepted only when every required check can be demonstrated complete and valid.

## License

This project is licensed under the GNU General Public License v3.0.

## Contributing

Please read the repository guidance in `.github/copilot-instructions.md` before making changes. Any contribution must preserve the fail-closed invariants and must not weaken witness verification, anchor checks, or ban logic.
