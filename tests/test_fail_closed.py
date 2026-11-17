"""Ban propagation and blackhole consumption tests."""

from src.banlist import BanList


def test_ban_notice_propagates():
    bans = BanList()
    notice = bans.ban("malicious-peer", "proof-hash", "trusted-witness", "sig")
    assert bans.is_banned("malicious-peer") is True
    assert notice.offending_hash == "malicious-peer"


def test_blackhole_list_consumption_is_opt_in():
    bans = BanList()
    bans.consume_blackhole({
        "offending_hash": "banned",
        "proof_hash": "proof-hash",
        "signer_hash": "trusted-signer",
        "signature": "sig",
    })
    assert bans.is_banned("banned") is True
