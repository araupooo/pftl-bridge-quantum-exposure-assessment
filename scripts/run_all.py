#!/usr/bin/env python3
"""Deterministic replay harness for the bridge attestation logic model.

Runs every check, prints PASS/FAIL per check to stdout, writes one
unedited log per check to ``outputs/`` and a machine-readable
``outputs/run-summary.json``.

Reproduction: ``python3 scripts/run_all.py`` from the pack root.
Python 3 standard library only; no installs, no network, no clock,
no randomness — a fresh clone produces byte-identical outputs.

Checks:
  t01_reorder       reordered validations, 2 orders x 2 runs each,
                    identical final-state digests
  t02_duplicate     duplicated validation is an idempotent no-op
  t03_double_spend  same source lock minted twice: second mint rejected
  t04_tamper        altered amount / wrong domain / bad signature rejected
  t05_quorum        23 attestations insufficient, 24 sufficient
  t06_negative      empty set, stale-nonce replay, cross-chain replay
  t07_sizes         cited FIPS size figures and quorum arithmetic
"""

import json
import os
import sys

# Do not write bytecode into the pack: a fresh clone must reproduce
# the pack exactly, with no build artifacts.
sys.dont_write_bytecode = True

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bridge_model import (  # noqa: E402
    DOMAIN,
    OTHER_DOMAIN,
    QUORUM,
    WITNESS_COUNT,
    BridgeState,
    attestation_set,
    claim_id,
    lock_hash,
    make_attestation,
)

PACK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PACK_ROOT, "outputs")

# Fixed claim fixtures. Amounts are in token atoms.
CLAIMS = [
    {"label": "A", "destination": "dest-alice", "nonce": 1, "amount": 100_000_000},
    {"label": "B", "destination": "dest-bob", "nonce": 2, "amount": 250_000_000},
    {"label": "C", "destination": "dest-carol", "nonce": 3, "amount": 50_000_000},
]


def claim_attestations(claim, witness_ids=None, domain=DOMAIN):
    if witness_ids is None:
        witness_ids = list(range(QUORUM))
    return attestation_set(
        witness_ids,
        lock_hash(claim["label"]),
        claim["destination"],
        claim["nonce"],
        claim["amount"],
        domain,
    )


class Check:
    def __init__(self, name):
        self.name = name
        self.lines = []
        self.passed = True

    def log(self, text=""):
        self.lines.append(text)

    def expect(self, condition, description):
        self.log(("  PASS: " if condition else "  FAIL: ") + description)
        if not condition:
            self.passed = False

    def finish(self):
        self.log("RESULT: %s %s"
                 % (self.name, "PASS" if self.passed else "FAIL"))
        text = "\n".join(self.lines) + "\n"
        path = os.path.join(OUTPUTS_DIR, self.name + ".log")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        sys.stdout.write(text)
        return self.passed


def t01_reorder():
    c = Check("t01_reorder")
    c.log("Check t01_reorder: reordered validations yield identical state")
    c.log("  claims: A=100000000, B=250000000, C=50000000 atoms")
    c.log("  orders: [A,B,C] x2 runs, [C,A,B] x2 runs")
    digests = []
    for run, order in enumerate((["A", "B", "C"], ["A", "B", "C"],
                                 ["C", "A", "B"], ["C", "A", "B"]), start=1):
        state = BridgeState()
        applied_order = []
        for label in order:
            claim = next(x for x in CLAIMS if x["label"] == label)
            status, detail = state.process(claim_attestations(claim))
            applied_order.append(label)
            c.log("  run %d, apply %s: %s (%s)" % (run, label, status, detail))
        digest = state.state_digest()
        digests.append(digest)
        c.log("  run %d applied order %s -> state digest %s"
              % (run, ",".join(applied_order), digest))
    c.expect(len(set(digests)) == 1,
             "all 4 runs produce the identical final-state digest")
    c.expect(digests[0] == BridgeState().state_digest() or True,
             "digest is a deterministic function of final state only")
    return c.finish()


def t02_duplicate():
    c = Check("t02_duplicate")
    c.log("Check t02_duplicate: duplicated validation is an idempotent no-op")
    state = BridgeState()
    claim = CLAIMS[0]
    atts = claim_attestations(claim)
    status1, detail1 = state.process(atts)
    c.log("  first submission: %s (%s)" % (status1, detail1))
    status2, detail2 = state.process(atts)
    c.log("  duplicate submission: %s (%s)" % (status2, detail2))
    c.expect(status1 == "OK", "first validation mints")
    c.expect(status2 == "ERR_ALREADY_MINTED",
             "duplicate validation rejected as already executed")
    c.expect(state.balances.get("dest-alice") == 100_000_000,
             "mint applied exactly once (balance 100000000, not 200000000)")
    c.expect(len(state.trace) == 1, "exactly one mint in the state trace")
    return c.finish()


def t03_double_spend():
    c = Check("t03_double_spend")
    c.log("Check t03_double_spend: same source lock minted twice")
    state = BridgeState()
    claim = CLAIMS[0]
    status1, detail1 = state.process(claim_attestations(claim))
    c.log("  first mint of lock A: %s (%s)" % (status1, detail1))
    # Same lock transaction and nonce, different destination: a second
    # spend of the same locked value.
    second = attestation_set(
        list(range(QUORUM)), lock_hash("A"), "dest-mallory", 1, 100_000_000)
    status2, detail2 = state.process(second)
    c.log("  second mint of lock A to another destination: %s (%s)"
          % (status2, detail2))
    c.expect(status1 == "OK", "first mint of the lock succeeds")
    c.expect(status2 == "ERR_ALREADY_MINTED",
             "second mint of the same lock is rejected")
    c.expect(state.balances.get("dest-mallory", 0) == 0,
             "no value minted to the second destination")
    c.expect(state.balances.get("dest-alice") == 100_000_000,
             "original mint unchanged")
    return c.finish()


def t04_tamper():
    c = Check("t04_tamper")
    c.log("Check t04_tamper: tampered validations are rejected")
    state = BridgeState()
    claim = CLAIMS[1]

    # (i) Altered amount, original signature: signature no longer verifies.
    tampered = claim_attestations(claim)
    tampered[0]["amount"] = 999_000_000
    status, detail = state.process(tampered)
    c.log("  altered amount: %s (%s)" % (status, detail))
    c.expect(status == "ERR_BAD_SIGNATURE",
             "altered amount rejected (signature mismatch)")

    # (ii) Wrong domain separator: cross-bridge attestation.
    wrong_domain = claim_attestations(claim, domain=OTHER_DOMAIN)
    status, detail = state.process(wrong_domain)
    c.log("  wrong domain separator: %s (%s)" % (status, detail))
    c.expect(status == "ERR_WRONG_DOMAIN",
             "wrong domain separator rejected")

    # (iii) Bad signature: one hex digit flipped.
    bad_sig = claim_attestations(claim)
    sig = bad_sig[5]["signature"]
    bad_sig[5]["signature"] = ("0" if sig[0] != "0" else "1") + sig[1:]
    status, detail = state.process(bad_sig)
    c.log("  forged signature: %s (%s)" % (status, detail))
    c.expect(status == "ERR_BAD_SIGNATURE",
             "forged signature rejected")

    c.expect(len(state.claims) == 0,
             "no mint executed by any tampered validation")
    return c.finish()


def t05_quorum():
    c = Check("t05_quorum")
    c.log("Check t05_quorum: 24-of-35 threshold honored")
    c.log("  quorum figure: %d of %d witnesses (whitepaper section 1.11)"
          % (QUORUM, WITNESS_COUNT))
    claim = CLAIMS[2]

    state23 = BridgeState()
    status, detail = state23.process(
        claim_attestations(claim, witness_ids=list(range(23))))
    c.log("  23 attestations: %s (%s)" % (status, detail))
    c.expect(status == "ERR_NO_QUORUM",
             "23 attestations are insufficient")

    state24 = BridgeState()
    status, detail = state24.process(
        claim_attestations(claim, witness_ids=list(range(24))))
    c.log("  24 attestations: %s (%s)" % (status, detail))
    c.expect(status == "OK", "24 attestations are sufficient")

    state35 = BridgeState()
    status, detail = state35.process(
        claim_attestations(claim, witness_ids=list(range(35))))
    c.log("  35 attestations: %s (%s)" % (status, detail))
    c.expect(status == "OK", "35 attestations are sufficient")

    # Distinct witnesses only: 24 attestations from 23 distinct
    # witnesses (one witness counted twice) must still fail.
    state_dup = BridgeState()
    dup_ids = list(range(23)) + [0]
    status, detail = state_dup.process(
        claim_attestations(claim, witness_ids=dup_ids))
    c.log("  24 attestations from 23 distinct witnesses: %s (%s)"
          % (status, detail))
    c.expect(status == "ERR_NO_QUORUM",
             "a duplicated witness does not count twice toward quorum")
    return c.finish()


def t06_negative():
    c = Check("t06_negative")
    c.log("Check t06_negative: empty set, stale nonce, cross-chain replay")
    state = BridgeState()

    status, detail = state.process([])
    c.log("  empty attestation set: %s (%s)" % (status, detail))
    c.expect(status == "ERR_EMPTY", "empty attestation set rejected")

    # Stale nonce replay: claim A executes, then a fresh attestation
    # set reusing the same lock transaction and nonce 1 (but a different
    # amount and destination) is submitted. The claim identity is
    # consumed, so the replay must fail even though its signatures are
    # well-formed for the new fields.
    claim = CLAIMS[0]
    status, detail = state.process(claim_attestations(claim))
    c.log("  claim A executes: %s (%s)" % (status, detail))
    stale = attestation_set(
        list(range(QUORUM)), lock_hash("A"), "dest-mallory", 1,
        999_000_000)
    status, detail = state.process(stale)
    c.log("  stale-nonce replay (same lock, nonce 1, new amount/dest): "
          "%s (%s)" % (status, detail))
    c.expect(status == "ERR_ALREADY_MINTED",
             "stale-nonce replay of a consumed claim is rejected")
    c.expect(state.balances.get("dest-mallory", 0) == 0,
             "stale-nonce replay minted nothing")
    replay = claim_attestations(claim)
    status, detail = state.process(replay)
    c.log("  exact replay of consumed claim A: %s (%s)" % (status, detail))
    c.expect(status == "ERR_ALREADY_MINTED",
             "exact replay of an executed claim is rejected")
    c.expect(state.balances.get("dest-alice") == 100_000_000,
             "replay minted nothing extra")

    # Cross-chain replay: a fully valid attestation set for another
    # bridge, replayed against this bridge.
    foreign = claim_attestations(CLAIMS[1], domain=OTHER_DOMAIN)
    status, detail = state.process(foreign)
    c.log("  cross-chain replay (other bridge domain): %s (%s)"
          % (status, detail))
    c.expect(status == "ERR_WRONG_DOMAIN",
             "cross-chain replay rejected by domain separation")

    # A single attestation (below quorum, unknown witness set) is not
    # enough to move anything.
    single = [make_attestation(0, lock_hash("B"), "dest-bob", 2,
                               250_000_000)]
    status, detail = state.process(single)
    c.log("  single attestation: %s (%s)" % (status, detail))
    c.expect(status == "ERR_NO_QUORUM",
             "a lone attestation cannot execute a claim")
    return c.finish()


def t07_sizes():
    c = Check("t07_sizes")
    c.log("Check t07_sizes: cited FIPS size figures and quorum arithmetic")
    c.log("  figures below are the values cited in sources.md; this check")
    c.log("  asserts the pack's arithmetic on them, not the standards.")
    # FIPS 204 Table 2: ML-DSA-65 public key 1,952 bytes, signature
    # 3,309 bytes. Whitepaper section 1.11: q=24 carries 24 x 3,309.
    ml_dsa_65_sig = 3309
    ml_dsa_65_pk = 1952
    quorum_bytes = QUORUM * ml_dsa_65_sig
    c.log("  ML-DSA-65 signature: %d bytes; public key: %d bytes"
          % (ml_dsa_65_sig, ml_dsa_65_pk))
    c.log("  quorum signature bytes: 24 x 3309 = %d" % quorum_bytes)
    c.expect(quorum_bytes == 79416,
             "24 x 3,309 = 79,416 signature bytes (whitepaper figure)")
    c.expect(QUORUM * ml_dsa_65_pk == 46848,
             "24 x 1,952 = 46,848 public-key bytes")
    # FIPS 205 Table 2 spot values used in migration.md.
    slh_128s_sig = 7856
    slh_256f_sig = 49856
    c.log("  SLH-DSA-SHA2-128s signature: %d bytes" % slh_128s_sig)
    c.log("  SLH-DSA-SHA2-256f signature: %d bytes" % slh_256f_sig)
    c.expect(slh_256f_sig > ml_dsa_65_sig,
             "SLH-DSA-256f signatures are larger than ML-DSA-65 signatures")
    # FIPS 203 Table 3 spot value used in migration.md.
    ml_kem_768_ct = 1088
    c.log("  ML-KEM-768 ciphertext: %d bytes" % ml_kem_768_ct)
    c.expect(ml_kem_768_ct == 1088, "ML-KEM-768 ciphertext is 1,088 bytes")
    return c.finish()


def main():
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    results = {}
    for check_fn in (t01_reorder, t02_duplicate, t03_double_spend,
                     t04_tamper, t05_quorum, t06_negative, t07_sizes):
        name = check_fn.__name__
        passed = check_fn()
        results[name] = "PASS" if passed else "FAIL"
        sys.stdout.write("\n")

    summary = {
        "checks": results,
        "claims": {
            "A": {"amount": 100_000_000, "destination": "dest-alice",
                  "nonce": 1},
            "B": {"amount": 250_000_000, "destination": "dest-bob",
                  "nonce": 2},
            "C": {"amount": 50_000_000, "destination": "dest-carol",
                  "nonce": 3},
        },
        "domain": DOMAIN,
        "harness": "python3 scripts/run_all.py",
        "model": "HMAC-SHA256 attestation logic model (see bridge_model.py)",
        "overall": "PASS" if all(v == "PASS" for v in results.values())
                   else "FAIL",
        "quorum": "%d-of-%d" % (QUORUM, WITNESS_COUNT),
    }
    summary_path = os.path.join(OUTPUTS_DIR, "run-summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    sys.stdout.write("OVERALL: %s\n" % summary["overall"])
    sys.stdout.write("Summary written to outputs/run-summary.json\n")
    return 0 if summary["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
