# Witness Verification

This document describes the strict witness verification model and the rationale behind providing quorum-based, fail-closed security for all accepted transactions.

## Quorum rules

The default minimum witness quorum is 2. The minimum quorum is configurable but never lower than 2.

A verification quorum is valid only when the selected witnesses are independent. Independence may be determined by:

- different transport identities
- distinct announced subnet tags
- operator-declared independence groups

If two witnesses share the same independence group, they count as one witness toward the quorum. If witness independence cannot be proven, the transaction is rejected.

## Verification pipeline

Before a transaction is accepted, the receiver performs the following checks:

1. Select independent witnesses based on reputation and availability.
2. Pull pair proofs and latest anchor from each witness.
3. Validate both signatures.
4. Validate the pair hash chain.
5. Validate anchor continuity.
6. Check monotonic counters and nonces.
7. Reconstruct the claimed balance from the chain.
8. Confirm quorum is reached.
9. Confirm no witness reports a mismatch or timeout.
10. Accept only when every requirement has passed.

## Timeouts and retries

The default witness timeout is 15 seconds. If quorum is not reached within that time, the transaction is rejected. There is no fallback to partial acceptance and no silent downgrade. If configured minimum quorum cannot be met, the node blocks the transaction until quorum becomes available again.

## Anchor cadence

Anchors are published periodically after `N` transactions or `T` hours, with the default `N` = 10. Anchors are only acknowledged by quorum. Once acknowledged, the anchor becomes the historical reference point. Any claim that conflicts with an accepted anchor is hard-rejected and may trigger ban propagation.

## Recovery flow

A bad actor or adversarial claim may require a formal recovery path. Recovery must not be automatic. It requires:

- a non-trivial appeal process
- witness sign-off from quorum participants
- an explicit stamp cost
- review against the historical proof and anchor record

## Fail-closed rationale

The system assumes network failures, witness compromise, and local tampering are normal adversarial conditions. Because the system must never accept invalid obligations, every witness check is treated as a gate, not as advice. This makes the system conservative but operationally safer for low-power, slow, or untrusted networks.
