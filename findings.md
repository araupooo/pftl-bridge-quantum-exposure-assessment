# Bridge quantum-exposure and migration assessment

## 1. Summary

This assessment examines the proposed cross-chain bridge that would
move value between the native asset on the ledger and a wrapped
representation on an external chain, and asks one question: where is
the bridge quantum-exposed, and what migrates it?

**Headline findings.**

1. **The ledger side is quantum-safe by design.** Accounts and
   validators sign with ML-DSA-65 from genesis, with
   domain-separated contexts that explicitly include bridge
   witnesses (whitepaper section 1.11, S10).
2. **The quantum exposure is concentrated in exactly the places
   the whitepaper's own scope limit names:** bridge proofs wrap in
   Groth16 (pairing-based, classical), and external-chain contracts
   "use their own cryptography" (classical) (S10, section 1.11).
   A third exposure is inherited, not stated: bridge witness keys
   are secp256k1 or ed25519 (S14), both breakable by Shor's
   algorithm (S19).
3. **The logic defences are sound and measured.** The inherited
   attestation scheme — quorum counting, claim-ID consumption,
   domain separation, duplicate and reorder handling — is verified
   in the replay harness: 7 of 7 checks pass, 29 of 29 assertions
   pass, 0 fail (section 5). Reordered validations produce an
   identical final-state digest across 4 runs; duplicated
   validations are idempotent; a second mint of the same lock is
   rejected; tampered validations are rejected; the 24-of-35
   quorum boundary is exact.
4. **The bridge premise itself is unverified.** No primary source
   confirms an ERC-20 representation on Base, a Base bridge
   contract, or a genesis bridging procedure (section 2). The
   assessment treats the bridge as a stated premise and assesses
   the design that would follow from it; it does not assert the
   bridge exists.
5. **Migration is plannable now, but two exposures have no
   complete fix today:** Groth16 bridge proofs and destination-
   chain cryptography (migration.md, section 7).

## 2. Assumptions register

The assessment distinguishes confirmed implementation facts from
planned or unverified assumptions throughout. This register is the
authoritative list. Anything marked ASSUMPTION is not asserted as
fact anywhere in this pack.

| ID | Assumption | Basis / what was checked | Impact if wrong |
|---|---|---|---|
| A1 | An ERC-20 representation of the native asset on Base exists or is planned before mainnet, with bridging to the native asset at genesis. | **UNVERIFIED.** The whitepaper contains zero occurrences of "ERC-20" and no mention of the Base chain. Web searches returned only the whitepaper/homepage and unrelated tokens. No founder post, document, or repository statement confirming it was located (S10). | If no such bridge is planned, sections 3-6 of this assessment describe a hypothetical design. The logic findings (section 5) and the migration plan (migration.md) still hold for any bridge built on the inherited XChainBridge design, but the Base/ERC-20 specifics do not apply. |
| A2 | The destination chain is Base. | **UNVERIFIED.** Same search as A1; no primary source names Base as a destination chain. | The destination-chain analysis (threat-model.md, T8) is generic to EVM chains; the chain name does not change the conclusions. |
| A3 | The bridge's deployment (witness count, quorum, operators, mint authority, contract) follows the inherited XRPL XChainBridge design. | **UNVERIFIED.** No deployment-specific document was found (S14). The inherited mechanism is confirmed in code (S12); its application to this bridge is assumed. | If the deployment differs (different quorum, different witness set, different mint authority), the quorum analysis and the harness's 24-of-35 figure must be re-pinned to the real deployment. The harness is parameterised for exactly this: QUORUM and WITNESS_COUNT in `scripts/bridge_model.py`. |
| A4 | The whitepaper's 24-of-35 quorum applies to bridge witnesses. | **ASSUMPTION.** The whitepaper states q=24 from 35 validators (S10, section 1.11) for validator quorum, and separately names domain-separated contexts for "bridge witnesses". It does not state that the bridge-witness quorum is 24-of-35. | The harness models 24-of-35 because it is the only quorum figure the project states. If the real witness quorum differs, t05_quorum must be re-run with the real figure. |
| A5 | The validator set is 35. | **CONFLICT, UNRESOLVED.** The whitepaper's arithmetic assumes 35; the homepage snapshot (21 September 2026) reports 53 validators (S11). | If the set is 53, 24 is 45.3% of it, not a supermajority. The quorum analysis in threat-model.md (T1, T2) flags this. |
| A6 | `fixAmendmentMajorityCalc` (67% threshold) is enabled on the live network. | **UNVERIFIED.** The code defines 67/100 post-fix and 204/256 pre-fix (S12); the amendment name was not located in `Feature.h`/`Feature.cpp`, so activation could not be determined from code. | The effective amendment threshold is 79.6875% or 67%, unknown. Any bridge change depending on an amendment inherits this uncertainty (threat-model.md, T9). |
| A7 | The "How the bridge stays post-quantum" page exists and supports the assessment. | **UNVERIFIED.** The homepage links that text; no matching page was located and the link target was not resolved (S11). | The pack relies on whitepaper section 1.11 instead, which was read directly. |
| A8 | The HMAC attestation model tests the real logic. | **LOGIC MODEL, labelled.** The harness uses HMAC-SHA256 tags with deterministically derived keys as a stand-in for signatures (scripts/bridge_model.py). It tests ordering, duplication, quorum counting, and tamper rejection in the attestation logic — not cryptographic primitives. | The harness says nothing about ML-DSA, Ed25519, or secp256k1 security. A logic PASS is not a cryptography PASS. See limitations.md. |
| A9 | CNSA 2.0 per-class deadlines (2027/2030/2033) are as reported. | **SECONDARY-SOURCED.** The NSA FAQ PDF was not retrievable from this environment; secondary summaries agree on the ladder, and the 2035 outer date is independently confirmed by IR 8547 (S21, S6). | The migration plan anchors on IR 8547 dates (2030/2031/2035), not the CNSA ladder. |
| A10 | A -20 revision of the LAMPS composite-signatures draft may exist. | **UNVERIFIED.** Draft -19 (21 April 2026) expired 23 October 2026; a later revision was not checked (S7). | If a newer revision or an RFC exists, migration.md should be re-pinned to it. The end state (single ML-DSA per RFC 9881) is unaffected. |
| A11 | RFC 9909 standardises SLH-DSA in X.509. | **SECONDARY-SOURCED.** Cited in secondary sources; the RFC text was not re-checked (S9). | Migration.md does not rely on it. |
| A12 | Axelar's 80% validator approval figure is current. | **CAVEAT.** The figure is from the Axelar whitepaper v1.0 (January 2021); current on-chain gateway thresholds are set by governance and were not re-verified (S16). | Used only as a reference point for quorum design, not as a current fact. |
| A13 | The joint CISA/NSA/NIST factsheet names harvest-now-decrypt-later. | **SECONDARY-SOURCED.** The factsheet (21 August 2023) was not fetched (S22). | Used only to name the HNDL adversary; the HNDL analysis does not depend on the factsheet's exact wording. |

## 3. Pinned architecture (summary)

Full detail: architecture.md. In brief:

- **Custody.** Source-chain lock held by a door account or lock
  contract (mechanism confirmed from the inherited design, S14;
  this bridge's custodian unverified, A3).
- **Mint/burn authority.** The destination contract mints only on
  a verified quorum of witness attestations; redemption burns the
  wrapped representation and releases the lock (assumed, A3).
- **Quorum.** 24 of 35 as stated in the whitepaper (S10); the
  bridge-witness application of that figure is assumed (A4), and
  the validator count is conflicted (A5).
- **Supply accounting.** s_native + s_shielded + s_external +
  s_in-flight = s_authorized; a claim occupies exactly one
  category at each stage (S10, section 1.3). A double-mint breaks
  this identity by counting one claim twice.
- **Attestations.** Witness servers sign attestations confirming a
  transaction occurred; keys are secp256k1 or ed25519 (S14);
  contexts are domain-separated, including for bridge witnesses
  (S10, section 1.11); claim IDs are consumed on execution (S12).
- **Scope limit.** Bridge proofs wrap in Groth16; external-chain
  contracts use their own cryptography (S10, section 1.11). The
  post-quantum claim covers account and validator authorisation
  "and nothing broader" (paraphrased from S10, section 1.11).

## 4. Threat model (summary)

Full detail: threat-model.md. Ten threats, T1-T10:

| ID | Threat | Severity | Status |
|---|---|---|---|
| T1 | Signer compromise by a quantum adversary (classical witness keys) | High | Open; migration phases 1-2 |
| T2 | Quorum design weakness (set size, operator correlation) | Medium | Open; deployment data needed (A3, A5) |
| T3 | Cross-chain replay (domain separation) | High if missing | Controlled in code; destination contract unverified |
| T4 | Double-spend paths (claim-ID reuse, destination re-mint, reorg) | High | Logic defences measured (section 5); residual paths listed in limitations.md |
| T5 | Reordered / duplicated validations | Medium | Measured: identical state digest, idempotent no-op |
| T6 | Tampered attestations | High if keys fall | Measured: all tamper cases rejected |
| T7 | Bridge-proof soundness (Groth16, pairing-based) | High | Open research dependency; no fix in this plan |
| T8 | External-chain contract cryptography (classical EVM) | High | Open; minimise external value at risk |
| T9 | Governance / amendment risk (67% vs 79.6875%, activation unknown) | Medium | Open; needs a live ledger check (A6) |
| T10 | Key-compromise response failure (revocation window) | Medium-high | Procedure in migration.md section 6 |

**Timeline anchors.** Mosca (2015): "a 1/2 chance of breaking
RSA-2048 by 2031" (S18). Global Risk Institute (March 2026, 26
experts): CRQC "quite possible" (28-49%) within 10 years,
"likely" (51-70%) within 15 years (S20). NIST IR 8547 (final,
October 2026): quantum-vulnerable algorithms deprecated after
2030, disallowed after 2035; post-quantum signatures by
31 December 2031 (S6). NSA: "does not know when there will be a
CRQC" (S21).

## 5. Measured results

The replay harness (`scripts/run_all.py`, Python 3 standard
library only) models the attestation scheme as signed attestation
records — witness id, source-chain lock transaction hash,
destination, nonce, amount, domain separator, signature — and
tests ordering, duplication, quorum, and tamper handling.
Signatures in the model are HMAC-SHA256 tags with deterministically
derived keys, explicitly labelled a LOGIC MODEL: they test the
attestation logic, not cryptographic primitives
(see `scripts/bridge_model.py` and limitations.md).

**Overall: 7 of 7 checks PASS, 29 of 29 assertions PASS, 0 FAIL.**
Unedited logs: `outputs/`. Machine-readable summary:
`outputs/run-summary.json`.

| Check | Result | What was measured |
|---|---|---|
| t01_reorder | PASS (2 assertions) | Claims A (100,000,000 atoms), B (250,000,000), C (50,000,000) applied in orders [A,B,C] x2 runs and [C,A,B] x2 runs. All 4 runs produce the identical final-state digest `ea00ee470531c76d6e30f57eefcd97ee412cd1cfffef28d69c694962d5fee257`. Application order differs; final state does not. |
| t02_duplicate | PASS (4 assertions) | First validation mints 100,000,000 atoms; the identical duplicate is rejected (`ERR_ALREADY_MINTED`); balance stays 100,000,000 (not 200,000,000); exactly one mint in the trace. |
| t03_double_spend | PASS (4 assertions) | Same source lock minted to a second destination is rejected (`ERR_ALREADY_MINTED`); no value reaches the second destination; the original mint is unchanged. |
| t04_tamper | PASS (4 assertions) | Altered amount rejected (signature mismatch); wrong domain separator rejected (`ERR_WRONG_DOMAIN`); forged signature rejected; no mint executed by any tampered validation. |
| t05_quorum | PASS (4 assertions) | 23 attestations insufficient (`ERR_NO_QUORUM`); 24 sufficient; 35 sufficient; 24 attestations from only 23 distinct witnesses insufficient — a duplicated witness does not count twice. |
| t06_negative | PASS (7 assertions) | Empty attestation set rejected; stale-nonce replay (same lock, nonce 1, new amount/destination) rejected; exact replay of an executed claim rejected; cross-chain replay (other bridge domain) rejected; a lone attestation cannot execute a claim. |
| t07_sizes | PASS (4 assertions) | 24 x 3,309 = 79,416 signature bytes (whitepaper figure, verified); 24 x 1,952 = 46,848 public-key bytes; SLH-DSA-256f signatures (49,856 B) larger than ML-DSA-65 (3,309 B); ML-KEM-768 ciphertext 1,088 bytes. |

**What the measurements establish.** In the modelled attestation
logic, validation order does not affect the outcome, duplication
cannot double-mint, a consumed claim cannot mint again, tampered
or foreign-domain attestations cannot execute, and the quorum
boundary is exact at 24 of 35. These properties mirror the
inherited code: `claimHelper` enforces `weight >= quorum`,
`onNewAttestations` replaces rather than double-counts duplicates,
`finalizeClaimHelper` erases the claim ID after execution, and
`applyClaimAttestations` rejects wrong-chain and
sending-account-mismatch attestations (S12).

**What the measurements do not establish.** They do not test real
cryptography (A8), a live chain, a real destination contract, or
the residual double-spend paths in T4 (source-chain double
recording, destination re-mint without a processed-claim set,
source-chain reorganisation). See limitations.md.

## 6. Migration plan (summary)

Full detail: migration.md. ML-DSA-65 is the recommended bridge
signature scheme (category 3, 1,952-byte public keys, 3,309-byte
signatures, S1) — the same parameter set the ledger already uses
(S10). ML-DSA-87 (category 5) is the higher-assurance option at
4,627-byte signatures. SLH-DSA is the lattice-failure fallback
(hash-only security, S2) but a poor fit for high-frequency
attestation at 7,856-49,856-byte signatures.

There is **no NIST hybrid-signature standard**. The transition
vehicle is the IETF LAMPS composite-ML-DSA draft (S7): AND-mode
verification, component keys never reused standalone — but
revision -19 expired 23 October 2026 and is not an RFC (A10).
Single ML-DSA in X.509 is standardised in RFC 9881 (S8) and is
the end state. Transport hardens with ML-KEM-768 (NIST default,
S3, section 8) in a hybrid PQ/T construction per SP 800-227
section 4.6 (S4). Firmware/release signing uses LMS/XMSS under
SP 800-208 (S5).

Phases: 0 inventory and crypto-agility; 1 hybrid composite
witness signatures with AND-mode verification; 2 quorum migration
with a dual-signature window in which only composite attestations
count toward quorum; 3 classical deprecation with a versioned
domain separator; 4 full ML-DSA operation and annual review. Each
phase has a verification gate; rollback protection is by versioned
domains, no downgrade after cutover, claim-ID epoch continuity,
and an emergency mint halt at 12 compromised keys (half the
quorum margin). Key-compromise response covers detection,
containment within 24 hours, recovery with hardware-backed
re-keying, and a CRQC emergency procedure that assumes classical
keys compromised as a class.

## 7. Limitations

See limitations.md for the full list, including what was not
verified, the residual double-spend paths, and the open
dependencies (Groth16 replacement, destination-chain
post-quantum authorisation, LAMPS standardisation). The
short version: this pack verifies attestation *logic* against
pinned primary sources; it does not verify a deployed bridge,
because no deployed bridge is published to verify.
