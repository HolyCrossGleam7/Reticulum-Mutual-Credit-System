# Copilot instructions

This repository implements a fail-closed Reticulum-based mutual credit ledger. The aim is not to maximize throughput at the expense of safety; the aim is to reject any transaction that cannot be proven valid.

## Mandatory invariants

1. Never accept a transaction when any verification step is incomplete.
2. Never fall back to partial acceptance when witnesses time out, disagree, or disappear.
3. Treat raw ledger JSON as untrusted cache only; never as the source of truth.
4. Every signed transaction must include both parties' signatures, monotonic counters, nonce, timestamp, and the prior pair-state hash.
5. Any counter regression, nonce reuse, signature mismatch, witness quorum failure, or anchor conflict must reject the transaction.
6. If independence of witnesses cannot be proven, the transaction must be rejected.
7. Ban notices and blackhole list consumption should be opt-in when enabled, but they must be enforced at the network boundary without bypass.
8. Preserve the no-blockchain, no-global-consensus philosophy.

## Architecture expectations

- Prefer explicit validation gates and small isolated modules.
- Keep cryptographic primitives in `src/crypto.py` and never implement custom cryptography.
- Require type hints and clear docstrings.
- Use `pytest` for fail-closed checks and reject acceptance on every failure path.
- Document risk, witness behavior, and assumptions in `docs/`.

## Review checklist

Before merging, ensure:

- witness quorum is enforced before new acceptance
- independence groups are checked for each verification event
- transaction rejection paths are explicit and tested
- anchor checks and counter checks are not bypassed
- repeated invalid proofs can be banned or escalated
- defaults reflect cautious fail-closed behavior for low-power or slow-link environments
