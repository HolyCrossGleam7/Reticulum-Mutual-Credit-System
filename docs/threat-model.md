# Threat Model

This document enumerates key threats and the mitigations applied to the Reticulum Mutual Credit System.

## 1. JSON tampering

Threat: A local or remote JSON ledger cache is modified by a malicious actor or a buggy process.

Mitigation: Treat all ledger JSON as untrusted cache. Validate signatures, chain continuity, and anchors before accepting any state. Tampered cache invalidates the chain and results in rejection.

Residual risk: Local tampering may still affect the original node's local operations if the node fails to verify the file before processing. The fail-closed design reduces this risk by insisting on cryptographic validation prior to acceptance.

## 2. Sybil witness flooding

Threat: An attacker creates many fake identities to dominate witness selection or push the system into a compromised quorum.

Mitigation: Required stamp cost for witness registration, witness endorsement from a trusted identity, and local reputation scoring that deprioritizes weak or unknown witnesses.

Residual risk: If the attacker controls sufficiently many trusted identities and can pay the cost, they may still attempt to game the system. The design minimizes this by requiring independence checks and bootstrapping trust.

## 3. Colluding witnesses

Threat: Multiple witnesses collude to falsely confirm invalid state.

Mitigation: Require independent witness groups, local reputation scoring, and strict anchor verification. Two witnesses from the same group count as one witness.

Residual risk: A credible coalition of independent operators could still deceive the network if they attack the same pair state. The combination of independence and fail-closed verification reduces, but does not eliminate, this risk.

## 4. Eclipse via witness monopoly

Threat: A node is isolated from independent witnesses and is forced to rely on a single or captured witness set.

Mitigation: Reject if quorum is not reached. Do not silently degrade to partial acceptance. If witness connectivity or independence cannot be proven, the transaction is blocked.

Residual risk: A sustained network partition may cause all transactions to fail until connectivity or witness independence returns.

## 5. Replay attacks

Threat: An attacker replays old signed messages or reuses an old nonce to cause a state contradiction.

Mitigation: Counter monotonicity, per-pair directional nonce management, and ban candidate handling for suspect replay patterns.

Residual risk: A replay attack across long network outages may still be possible if local state is not consistently synchronized. The design keeps counters and nonces strict and local to each pair.

## 6. Metadata correlation and traffic analysis

Threat: Reticulum network traffic and announced identities reveal who is transacting with whom.

Mitigation: Prefer transport privacy guidance, use Tor or I2P tunnels for anonymity-sensitive deployments, and minimize metadata leaks through path discovery and announcements.

Residual risk: Metadata leakage is reduced but not eliminated. The system is not anonymous by default and should be adapted for privacy-sensitive environments.
