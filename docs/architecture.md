# Architecture

This document gives the high-level architecture for the Reticulum Mutual Credit System. The system is intentionally small, modular, and fail-closed.

## Overview

Each participant runs a local node that maintains:

- a persistent RNS identity
- a local ledger of bilateral credit lines
- a witness registry and reputation tracker
- an anchor history for tamper-evident checkpoints
- optional banlist and signed blackhole list handling

No global ledger is shared. Instead, each pair maintains a hash chain that records its mutual credit state across time.

## Core components

- `src/crypto.py`: wrappers around RNS identity and signature operations, nonce/counter handling, hash chain logic, and anchor computation
- `src/ledger.py`: balance math, limit enforcement, validation of pair state, and local accounting
- `src/witness.py`: witness selection, quorum verification, independence checks, and timeout logic
- `src/anchors.py`: anchor publication and verification against historical history
- `src/protocol.py`: message schema definitions and JSON serialization helpers
- `src/node.py`: network adapter around `RNS.Link`, announcements, and fail-closed transaction gates
- `src/banlist.py`: signed ban propagation and local enforcement
- `src/reputation.py`: local viewer-relative trust metrics
- `src/cli.py`: command-line interface

## Sequence diagrams

### 1) Happy path with quorum = 2

```mermaid
sequenceDiagram
    participant A as Alice Node
    participant B as Bob Node
    participant W1 as Witness 1
    participant W2 as Witness 2

    A->>B: CREDIT_REQUEST signed + state hash
    B->>A: CREDIT_APPROVAL if within limit
    A->>W1: WITNESS_PULL previous proof + anchor
    A->>W2: WITNESS_PULL previous proof + anchor
    W1-->>A: WITNESS_RESPONSE valid
    W2-->>A: WITNESS_RESPONSE valid
    A->>B: Commit signed state update
    B-->>A: Acknowledge
```

### 2) Tampered JSON detection

```mermaid
sequenceDiagram
    participant A as Alice Node
    participant B as Bob Node
    participant L as Local Ledger File
    participant W as Witness

    A->>L: Read cached ledger JSON
    A->>A: Recompute signatures over object
    A->>W: Query historical proof
    W-->>A: Proof chain and anchor state
    A->>A: Compare signatures and hash chain
    A->>A: Detect mismatch
    A-->>B: REJECT transaction
```

### 3) Witness timeout -> rejection

```mermaid
sequenceDiagram
    participant A as Alice Node
    participant W1 as Witness 1
    participant W2 as Witness 2

    A->>W1: WITNESS_PULL
    A->>W2: WITNESS_PULL
    W1-->>A: No response before timeout
    W2-->>A: No response before timeout
    A->>A: Quorum not reached within timeout
    A-->>A: Reject transaction
```

### 4) Anchor conflict -> ban propagation

```mermaid
sequenceDiagram
    participant A as Alice Node
    participant B as Bob Node
    participant W as Witness
    participant G as Global/Trusted Network

    A->>B: Claim state with conflicting anchor
    B->>W: Verify anchor chain
    W-->>B: Conflict detected
    B->>G: BAN_NOTICE with offending proof hash
    G-->>B: Signed blackhole list or notice
    B-->>A: Reject + ban candidate
```

## Design constraints

- no blockchain
- no trusted central bank
- strict witness independence
- configurable quorum and timeouts
- fail-closed behavior required in every acceptance gate
