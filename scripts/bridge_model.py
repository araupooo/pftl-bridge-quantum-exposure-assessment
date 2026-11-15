#!/usr/bin/env python3
"""Logic model of a cross-chain bridge attestation scheme.

This module is a LOGIC MODEL, not a cryptographic implementation.

What it models (from the inherited XRPL XChainBridge design, postfiatd
``src/xrpld/app/tx/detail/XChainBridge.cpp``, and the whitepaper's stated
quorum of q=24 from 35 validators):

- A source-chain lock is observed by a set of witnesses.
- Each witness issues a signed attestation for a claim (lock transaction
  hash, destination, nonce, amount, domain separator).
- A claim is executed (minted on the destination chain) only when
  attestations from at least QUORUM distinct witnesses agree on the same
  claim fields.
- A claim identifier is consumed on execution, so the same claim cannot
  execute twice (mirrors ``finalizeClaimHelper`` erasing the claim-ID
  ledger entry; a second claim with the same ID fails in the real code
  with ``tecXCHAIN_NO_CLAIM_ID``).

What it does NOT model:

- Real cryptography. Attestation "signatures" here are HMAC-SHA256 tags
  computed with deterministically derived per-witness keys. They exist
  only so the harness can test ordering, duplication, quorum counting,
  and tamper rejection in the attestation *logic*. They say nothing about
  the security of ML-DSA, Ed25519, secp256k1, or any real signature
  scheme. A quantum adversary that breaks a real witness key is outside
  this model; that risk is assessed in ``threat-model.md`` instead.
- Real chains, real ledgers, real networks. There is no live chain here.

Determinism: every key, lock hash, nonce, and amount is fixed in code.
No randomness, no clock, no network, no environment input. Two runs of
the same check produce byte-identical output.
"""

import hashlib
import hmac
import json

# --- Pinned parameters -------------------------------------------------
# Quorum figure stated in the whitepaper, section 1.11: q=24 from 35
# validators. Used here as the witness quorum of the modelled bridge.
QUORUM = 24
WITNESS_COUNT = 35

# Domain separator for this bridge. Attestations carrying any other
# domain are cross-chain replays and must be rejected.
DOMAIN = "pftl-bridge/v1"
OTHER_DOMAIN = "other-bridge/v1"

# --- Deterministic witness keys (logic model only) ---------------------
# Fixed derivation, so a fresh clone reproduces identical attestations.


def witness_key(witness_id):
    """Deterministic per-witness HMAC key. NOT a real signing key."""
    return hashlib.sha256(
        ("witness-key-%02d" % witness_id).encode("utf-8")
    ).digest()


# --- Attestations -------------------------------------------------------


def canonical_fields(lock_tx_hash, destination, nonce, amount, domain):
    """Canonical serialisation of the fields a witness attests to."""
    return json.dumps(
        {
            "amount": amount,
            "destination": destination,
            "domain": domain,
            "lock_tx_hash": lock_tx_hash,
            "nonce": nonce,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def make_attestation(witness_id, lock_tx_hash, destination, nonce, amount,
                     domain=DOMAIN):
    """Build a signed attestation (HMAC tag = logic-model signature)."""
    tag = hmac.new(
        witness_key(witness_id),
        canonical_fields(lock_tx_hash, destination, nonce, amount,
                         domain).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "amount": amount,
        "destination": destination,
        "domain": domain,
        "lock_tx_hash": lock_tx_hash,
        "nonce": nonce,
        "signature": tag,
        "witness_id": witness_id,
    }


def verify_attestation(att):
    """Recompute the tag. Returns True only for an untampered attestation."""
    expected = hmac.new(
        witness_key(att["witness_id"]),
        canonical_fields(
            att["lock_tx_hash"], att["destination"], att["nonce"],
            att["amount"], att["domain"],
        ).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, att["signature"])


def claim_id(lock_tx_hash, nonce, domain):
    """Claim identifier: binds a lock transaction, its nonce, and the
    bridge domain. A claim ID is consumed on execution, so the same
    source lock cannot mint twice."""
    return hashlib.sha256(
        ("%s|%d|%s" % (lock_tx_hash, nonce, domain)).encode("utf-8")
    ).hexdigest()


def lock_hash(label):
    """Deterministic stand-in for a source-chain lock transaction hash."""
    return hashlib.sha256(("lock-tx-%s" % label).encode("utf-8")).hexdigest()


# --- Bridge state -------------------------------------------------------


class BridgeState:
    """Destination-chain state for the modelled bridge.

    ``claims`` maps a consumed claim ID to the executed mint.
    ``balances`` maps a destination address to total minted atoms.
    ``trace`` records executed mints in application order.
    """

    def __init__(self):
        self.claims = {}
        self.balances = {}
        self.trace = []

    def state_digest(self):
        """Deterministic digest of the full final state (order-free)."""
        canonical = json.dumps(
            {
                "balances": self.balances,
                "claims": {
                    cid: {
                        "amount": c["amount"],
                        "destination": c["destination"],
                    }
                    for cid, c in sorted(self.claims.items())
                },
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def process(self, attestations):
        """Validate an attestation set and execute the claim if it passes.

        Returns (status, detail) where status is "OK" or an error code:
          ERR_EMPTY            no attestations supplied
          ERR_BAD_SIGNATURE    a signature does not verify (tampered field
                               or forged signature)
          ERR_WRONG_DOMAIN     an attestation names another bridge/domain
          ERR_FIELD_MISMATCH   attestations disagree on lock, destination,
                               nonce, or amount
          ERR_NO_QUORUM        fewer than QUORUM distinct witnesses agree
          ERR_ALREADY_MINTED   the claim ID was already consumed
        """
        if not attestations:
            return ("ERR_EMPTY", "empty attestation set")

        first = attestations[0]
        for att in attestations:
            if not verify_attestation(att):
                return ("ERR_BAD_SIGNATURE",
                        "witness %d signature does not verify"
                        % att["witness_id"])
            if att["domain"] != DOMAIN:
                return ("ERR_WRONG_DOMAIN",
                        "domain %r is not this bridge" % att["domain"])
            for field in ("lock_tx_hash", "destination", "nonce", "amount"):
                if att[field] != first[field]:
                    return ("ERR_FIELD_MISMATCH",
                            "attestations disagree on %s" % field)

        distinct = sorted({a["witness_id"] for a in attestations})
        if len(distinct) < QUORUM:
            return ("ERR_NO_QUORUM",
                    "%d distinct witnesses, quorum is %d"
                    % (len(distinct), QUORUM))

        cid = claim_id(first["lock_tx_hash"], first["nonce"], DOMAIN)
        if cid in self.claims:
            return ("ERR_ALREADY_MINTED",
                    "claim %s already executed" % cid[:16])

        self.claims[cid] = {
            "amount": first["amount"],
            "destination": first["destination"],
            "witnesses": distinct,
        }
        self.balances[first["destination"]] = (
            self.balances.get(first["destination"], 0) + first["amount"]
        )
        self.trace.append({
            "amount": first["amount"],
            "claim_id": cid,
            "destination": first["destination"],
            "witnesses": len(distinct),
        })
        return ("OK", "minted %d atoms to %s (claim %s)"
                % (first["amount"], first["destination"], cid[:16]))


def attestation_set(witness_ids, lock_tx_hash, destination, nonce, amount,
                    domain=DOMAIN):
    """Build one attestation per listed witness for the same claim."""
    return [
        make_attestation(w, lock_tx_hash, destination, nonce, amount, domain)
        for w in witness_ids
    ]
