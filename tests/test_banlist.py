"""Anchor publication and integrity tests."""

from src.anchors import AnchorManager, AnchorValidationError


def test_anchor_publish_and_verify_round_trip():
    manager = AnchorManager()
    anchor = manager.publish_anchor("pair-1", "head-1", ["sig-a", "sig-b"])
    assert manager.verify_anchor("pair-1", "head-1", anchor.anchor_hash)


def test_conflicting_anchor_detected():
    manager = AnchorManager()
    manager.publish_anchor("pair-1", "head-1", ["sig-a"])
    assert manager.detect_conflict("pair-1", "head-2") is True


def test_anchor_requires_witness_signatures():
    try:
        anchor = __import__("src.anchors", fromlist=["Anchor"]).Anchor(pair_hash="p", chain_head="h", timestamp=0.0, witness_signatures=[])
        anchor.finalize()
        assert False, "Anchor without witness signatures should be rejected."
    except AnchorValidationError:
        pass
