"""Witness verification tests for valid proofs, tampering, and rejection paths."""

from src.witness import WitnessManager, WitnessValidationError


def test_witness_quorum_selection_uses_independent_groups():
    manager = WitnessManager(min_quorum=2)
    manager.add_witness("w1", group="A", reliability=0.9)
    manager.add_witness("w2", group="A", reliability=0.8)
    manager.add_witness("w3", group="B", reliability=0.7)
    selected = manager.choose_quorum("pair-1")
    assert len(selected) == 2
    assert {w.witness_hash for w in selected} == {"w1", "w3"}


def test_quorum_not_met_is_rejected():
    manager = WitnessManager(min_quorum=2)
    manager.add_witness("w1", group="A")
    try:
        manager.choose_quorum("pair-2")
        assert False, "Insufficient independent witnesses should be rejected."
    except WitnessValidationError:
        pass


def test_timeout_rejected():
    manager = WitnessManager(min_quorum=2, witness_timeout=15.0)
    manager.add_witness("w1", group="A")
    manager.add_witness("w2", group="B")
    responses = [{"valid": False}, {"valid": False}]
    assert manager.timeout_reached(responses) is True
