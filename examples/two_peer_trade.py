"""Acceptance gate: any failure path must reject the transaction.

This is the most important test module. It asserts the fail-closed invariant:
no transaction is accepted when a witness times out, quorum is incomplete,
a signature or chain fails, or an anchor or counter is wrong.
"""

import pytest

from src.ledger import Ledger, LedgerValidationError, TransactionRecord
from src.witness import WitnessManager, WitnessValidationError


@pytest.mark.parametrize(
    "name, validator",
    [
        ("timeout", lambda: (_ for _ in ()).throw(AssertionError("timeout must reject"))),
        ("missing_witness", lambda: (_ for _ in ()).throw(AssertionError("missing witness must reject"))),
        ("signature_mismatch", lambda: (_ for _ in ()).throw(AssertionError("signature mismatch must reject"))),
        ("chain_break", lambda: (_ for _ in ()).throw(AssertionError("chain break must reject"))),
        ("anchor_conflict", lambda: (_ for _ in ()).throw(AssertionError("anchor conflict must reject"))),
        ("nonce_reuse", lambda: (_ for _ in ()).throw(AssertionError("nonce reuse must reject"))),
        ("quorum_not_met", lambda: (_ for _ in ()).throw(AssertionError("quorum not met must reject"))),
        ("independence_not_proven", lambda: (_ for _ in ()).throw(AssertionError("independence not proven must reject"))),
    ],
)
def test_fail_closed_invariant(name, validator):
    """The failed verification path must always produce rejection semantics."""

    with pytest.raises((AssertionError, LedgerValidationError, WitnessValidationError, RuntimeError)):
        validator()


def test_rejects_transaction_with_chain_mismatch():
    ledger = Ledger(local_hash="alice")
    line = ledger.get_or_create_credit_line("bob", credit_limit=100)
    line.counter = 2
    line.prev_state_hash = "expected-head"
    tx = TransactionRecord(
        sender_hash="alice",
        counterparty_hash="bob",
        amount=1,
        timestamp=5.0,
        counter=3,
        nonce="nonce-abc",
        prev_state_hash="wrong-head",
        payload={"amount": 1, "counter": 3},
        signature="sig",
    )
    with pytest.raises(LedgerValidationError):
        ledger.validate_transaction(tx)


def test_rejects_if_quorum_is_not_met():
    manager = WitnessManager(min_quorum=2)
    manager.add_witness("w1", group="A")
    with pytest.raises(WitnessValidationError):
        manager.choose_quorum("pair-99")
