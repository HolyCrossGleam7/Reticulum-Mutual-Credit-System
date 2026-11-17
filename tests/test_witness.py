"""Protocol-level integration tests for JSON transport and message validation."""

from src.protocol import Message, ProtocolError, VALID_MESSAGE_TYPES, make_message


def test_valid_message_types_are_registered():
    assert "CREDIT_REQUEST" in VALID_MESSAGE_TYPES
    assert "WITNESS_RESPONSE" in VALID_MESSAGE_TYPES
    assert "BAN_NOTICE" in VALID_MESSAGE_TYPES


def test_make_message_factory_sets_core_fields():
    message = make_message("CREDIT_REQUEST", "alice", {"amount": 10}, counter=1, nonce="n-1")
    assert message.type == "CREDIT_REQUEST"
    assert message.sender_hash == "alice"
    assert message.counter == 1
    assert message.nonce == "n-1"


def test_from_dict_round_trip():
    raw = {
        "type": "BALANCE_QUERY",
        "sender_hash": "alice",
        "counter": 2,
        "nonce": "n-2",
        "timestamp": 123.0,
        "signature": "sig",
        "payload": {"peer_hash": "bob"},
    }
    message = Message.from_dict(raw)
    assert message.to_dict() == raw


def test_missing_field_rejected():
    raw = {"type": "BALANCE_QUERY", "sender_hash": "alice"}
    try:
        Message.from_dict(raw)
        assert False, "Missing fields should be rejected."
    except ProtocolError:
        pass
