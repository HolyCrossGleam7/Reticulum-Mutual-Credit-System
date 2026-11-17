"""Ledger unit tests."""

from src.ledger import Ledger, LedgerValidationError, TransactionRecord


def test_credit_line_created():
    ledger = Ledger(local_hash="alice")
    line = ledger.get_or_create_credit_line("bob", credit_limit=100)
    assert line.peer_hash == "bob"
    assert line.credit_limit == 100


def test_rejects_counter_regression():
    ledger = Ledger(local_hash="alice")
    line = ledger.get_or_create_credit_line("bob", credit_limit=100)
    line.counter = 5
    tx = TransactionRecord(
        sender_hash="alice",
        counterparty_hash="bob",
        amount=10,
        timestamp=1.0,
        counter=4,
        nonce="nonce-1",
        prev_state_hash=line.prev_state_hash,
        payload={"amount": 10, "counter": 4},
        signature="sig",
    )
    try:
        ledger.validate_transaction(tx)
        assert False, "Counter regression should be rejected."
    except LedgerValidationError:
        pass


def test_rejects_amount_over_limit():
    ledger = Ledger(local_hash="alice")
    line = ledger.get_or_create_credit_line("bob", credit_limit=10)
    tx = TransactionRecord(
        sender_hash="alice",
        counterparty_hash="bob",
        amount=11,
        timestamp=1.0,
        counter=1,
        nonce="nonce-2",
        prev_state_hash=line.prev_state_hash,
        payload={"amount": 11, "counter": 1},
        signature="sig",
    )
    try:
        ledger.validate_transaction(tx)
        assert False, "Over-limit amount should be rejected."
    except LedgerValidationError:
        pass
