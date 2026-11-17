# Security Considerations

This project assumes Reticulum nodes may operate in privacy-sensitive, low-power, or intermittently connected environments. The default assumptions are not trust-based or anonymous by default.

## Metadata leakage

Reticulum traffic can reveal communication patterns, destination hashes, and timing. In an adversarial environment, this can enable correlation or service profiling.

Recommended mitigations:

- keep node announcements minimal
- avoid broadcasting unnecessary metadata
- use encrypted transport and private destination paths where possible
- reduce high-frequency anchor publication in sensitive communities

## Tor and I2P recommendations

For users who need stronger anonymity or wiring resistance to traffic analysis, run traffic through a SOCKS proxy or a dedicated I2P transport. The system should be able to pass through Tor or I2P without changing application logic.

Operational guidance:

- configure outbound RNS flows through Tor for privacy-sensitive deployments
- use I2P when path or timing obfuscation is more important than latency
- keep the witness set diverse and avoid grouping all witnesses behind a single operator or infrastructure

## Stamp costs

The system design requires stamp costs for the following actions:

- creating a new credit line
- registering as a witness
- publishing an anchor
- ban recovery

The default values should be high enough to make mass witness Sybil flooding unattractive. The exact values are configurable and should account for the hardware and network environment.

## Operational hardening checklist

- run independent witnesses with distinct network identities and separate operational groups
- segregate witness traffic from user traffic where feasible
- maintain local logs of failed witness checks and security events
- review anchor publication cadence in slow or remote deployments
- enforce persistent bans for confirmed malicious acts
- require witness endorsement before new witnesses are allowed to participate in quorum
- reboot or rotate stale witness endpoints when they fail silently
