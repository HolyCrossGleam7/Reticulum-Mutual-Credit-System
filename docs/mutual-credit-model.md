# Mutual Credit Model

This document describes the pairwise credit design for the Reticulum Mutual Credit System.

## Bilateral credit lines

Each pair of participants maintains a local credit line. It is not a global account and not a ledger across all users. The model is bilateral and pair-specific.

A credit line contains:

- creditor identity hash
- debtor identity hash
- `credit_limit` maximum allowed debt
- current `balance` (positive or negative depending on viewpoint)
- chain head hash of the latest signed state
- last acknowledged anchor
- monotonic counters per direction

## State transition semantics

A transaction between Alice and Bob is a signed obligation update. It does not create money ex nihilo; it updates the pairwise state. A positive balance for Alice means Bob owes Alice; a negative balance means Alice owes Bob.

## Credit/debit rules

Each acceptance gate ensures:

- the debtor's effective balance remains within the configured credit limit
- both parties signed the transaction
- the previous hash matches the pair's latest chain head
- the direction-specific counter is monotonic
- no nonce is reused for the same `(pair, direction)`

## Example

If Alice buys a service worth 50 units from Bob:

- Bob is the creditor
- Alice's balance against Bob decreases by 50 if we read from Alice's perspective
- Bob's balance against Alice increases by 50

The system records both directions as separate signed entries on the shared pair state.

## Limits and debt caps

The pairwise credit line must include a configured maximum net debt. If the next transaction would exceed that maximum, the node rejects the credit request. The fail-closed behavior means there is no soft overrun or temporary allowance.

## Settlement policy

Settlement is eventual and bilateral. The system may prefer a direct balance reconciliation or a witness-attested settlement record, but the default behavior is to remain conservative and require valid proofs before settlement is accepted.
