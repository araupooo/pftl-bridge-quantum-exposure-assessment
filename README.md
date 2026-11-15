# Bridge quantum-exposure and migration assessment

An assessment of the proposed cross-chain bridge that would move
value between the native asset on the ledger and a wrapped
representation on an external chain: its quantum custody risks,
cross-chain replay exposure, and a migration path to hybrid
ML-DSA / SLH-DSA signing.

## Reproduction

One command, from the pack root:

```
python3 scripts/run_all.py
```

Intended repository name (for the public evidence repository, not
created here): `pftl-bridge-quantum-exposure-assessment`.

Python 3 standard library only. No installs, no network, no clock,
no randomness. A fresh clone produces byte-identical outputs.

The run writes one unedited log per check to `outputs/` and a
machine-readable `outputs/run-summary.json`, then prints
`OVERALL: PASS` (or `FAIL`).

**Measured result (this pack's run): 7 of 7 checks PASS, 29 of 29
assertions PASS, 0 FAIL.** Final-state digest for the reorder
check, identical across 4 runs:
`ea00ee470531c76d6e30f57eefcd97ee412cd1cfffef28d69c694962d5fee257`.

## File map

| File | Contents |
|---|---|
| `README.md` | This file: reproduction, file map, digest verification, limitations summary |
| `findings.md` | Full assessment: pinned architecture summary, assumptions register, threat-model summary, measured results, migration summary |
| `index.html` | Rendered findings page (static, self-contained, no external assets), mirroring findings.md |
| `architecture.md` | Pinned proposed bridge architecture: custody, mint/burn authority, signer quorum, wrapped representations; every element tagged CONFIRMED or ASSUMPTION |
| `threat-model.md` | Full threat model: signer compromise, quorum design, cross-chain replay, double-spend paths, trust boundaries, with specification citations |
| `migration.md` | Classical-to-hybrid ML-DSA/SLH-DSA migration plan: rollout phases, verification gates, rollback protection, key-compromise response |
| `scripts/bridge_model.py` | Attestation logic model (HMAC-SHA256 stand-in signatures, labelled as a logic model) |
| `scripts/run_all.py` | Deterministic replay harness: 7 checks, writes `outputs/` |
| `outputs/` | Unedited run logs (`t01_reorder.log` … `t07_sizes.log`) and `run-summary.json` |
| `sources.md` | Primary-source citations (URL + section/version/date) for every spec-derived claim |
| `claims.md` | Claim-to-evidence index: each testable claim → script(s) + output file(s) + result |
| `DIGESTS.txt` | SHA-256 of every file in the pack (excluding itself) |
| `limitations.md` | What was not verified, failed/inconclusive checks, open dependencies |

## How to verify digests

From the pack root:

```
sha256sum -c DIGESTS.txt
```

Every file should report `OK`. `DIGESTS.txt` itself is excluded
from the list by construction. If any file reports `FAILED`, the
pack has been modified since the digests were generated.

## What the harness models — and what it does not

The harness models bridge validations as signed attestation
records (witness id, source-chain lock transaction hash,
destination, nonce, amount, domain separator, signature). The
signatures are HMAC-SHA256 tags with deterministically derived
keys, explicitly labelled a **LOGIC MODEL**: they test ordering,
duplication, quorum logic, and tamper rejection — not
cryptographic primitives. See `scripts/bridge_model.py` and
`limitations.md`.

Checks: reordered validations (2 orders x 2 runs, identical state
traces); duplicated validation (idempotent no-op); double-spend
(same source lock minted twice, second rejected); tampered
validation (altered amount, wrong domain separator, bad signature
— all rejected); quorum (23 insufficient, 24 sufficient, 24-of-35
per the whitepaper's stated quorum); negative controls (empty
attestation set, stale-nonce replay, cross-chain replay — all
rejected).

## Limitations summary

- **The bridge premise is unverified.** No primary source confirms
  an ERC-20 representation on Base, a Base bridge contract, or a
  genesis bridging procedure. The pack presents the premise as a
  stated assumption (ASSUMPTION / UNVERIFIED), never as a
  confirmed fact. See the assumptions register in findings.md,
  section 2.
- **No deployed bridge was available to verify.** No contract,
  witness set, or operator list is published. The harness's
  24-of-35 quorum is the whitepaper's validator figure applied to
  bridge witnesses by assumption.
- **Two exposures have no complete fix today:** Groth16 bridge
  proofs and destination-chain cryptography (migration.md,
  section 7).
- **Residual double-spend paths** (source-chain double recording,
  destination re-mint without a processed-claim set, source-chain
  reorganisation) are outside the model and listed as open in
  limitations.md.
- Full limitations: `limitations.md`.

## Sources

Every specification-derived claim cites a primary source in
`sources.md` — NIST FIPS 203/204/205, SP 800-227 §4.6, SP 800-208,
IR 8547, RFC 9881, the LAMPS composite-signatures draft, the
whitepaper, postfiatd and upstream XRPL source code, XRPL
witness-server documentation, Wormhole/Axelar/LayerZero official
docs, Mosca ePrint 2015/1075, the Global Risk Institute 2025
timeline report, and the NSA CNSA 2.0 FAQ. Items that could not
be verified against a primary source are marked UNVERIFIED or
secondary-sourced in `sources.md` and in the assumptions register.
