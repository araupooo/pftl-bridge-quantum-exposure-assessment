# Classical-to-hybrid ML-DSA / SLH-DSA migration plan

## 1. Goal and non-goals

**Goal.** Move bridge signing from classical-only (secp256k1 /
ed25519 witness keys, inherited from the XRPL design, S14) to
hybrid classical + post-quantum signing, and then to post-quantum
primary signing, without ever breaking the supply identity
(s_native + s_shielded + s_external + s_in-flight = s_authorized,
S10, section 1.3) and without a flag day that strands in-flight
claims.

**Non-goals.** This plan does not replace Groth16 bridge proofs
(see section 5 — an open research dependency), does not change the
destination chain's cryptography (see threat-model.md, T8), and
does not migrate ledger account keys, which are already ML-DSA-65
from genesis (S10, section 1.11).

## 2. Grounding: sizes, categories, and standards status

All figures below are from the cited primary sources (sources.md).
Nothing here is estimated.

### 2.1 Signature schemes

| Scheme | Parameter set | Category | Public key | Signature | Source |
|---|---|---|---|---|---|
| ML-DSA-44 | — | 2 (1 if RBG < 192-bit) | 1,312 B | 2,420 B | S1, Table 2, §4 |
| ML-DSA-65 | — | 3 | 1,952 B | 3,309 B | S1, Table 2, §4 |
| ML-DSA-87 | — | 5 | 2,592 B | 4,627 B | S1, Table 2, §4 |
| SLH-DSA-SHA2-128s | — | 1 | 32 B | 7,856 B | S2, Table 2 |
| SLH-DSA-SHA2-128f | — | 1* | 32 B | 17,088 B | S2, Table 2 |
| SLH-DSA-SHA2-192s | — | 3 | 48 B | 16,224 B | S2, Table 2 |
| SLH-DSA-SHA2-192f | — | 3 | 48 B | 35,664 B | S2, Table 2 |
| SLH-DSA-SHA2-256s | — | 5 | 64 B | 29,792 B | S2, Table 2 |
| SLH-DSA-SHA2-256f | — | 5 | 64 B | 49,856 B | S2, Table 2 |

\* S2, section 11: the two 128f sets do not meet their claimed
category for message-bound signatures. Avoid 128f for bridge
attestations.

**Recommendation.** ML-DSA-65 as the bridge signature scheme:
category 3, the same parameter set the ledger already uses for
accounts and validators (S10, section 1.11), so the ledger's
existing ML-DSA verification path is reused. ML-DSA-87 (category
5) is the choice if the bridge must match the highest CNSA 2.0
level (S21: ML-DSA-87 for signatures), at the cost of 4,627-byte
signatures; a 24-of-35 quorum then carries 24 x 4,627 = 111,048
signature bytes, against 79,416 for ML-DSA-65 (verified
arithmetic in t07_sizes). SLH-DSA is the fallback if lattice
assumptions are ever distrusted: its security rests only on hash
functions (S2), but its signatures are 2-15x larger and its
signing is slower (the "s" variants) or much larger (the "f"
variants); it is a poor fit for high-frequency attestation and is
reserved here for low-frequency release/firmware signing, where
its small public keys (32-64 bytes) and hash-only assumptions are
most valuable.

### 2.2 Hybrid signatures: the standards situation

- **There is no NIST FIPS hybrid-signature standard.** Hybrid
  guidance for *key establishment* exists in SP 800-227 §4.6 (S4);
  it does not cover signatures.
- **The live vehicle for hybrid signatures is the IETF LAMPS
  composite-ML-DSA draft** (S7): composite ML-DSA with RSA-PSS,
  ECDSA, Ed25519, or Ed448. Verification is AND-mode (both
  component signatures must validate). Component keys MUST NOT be
  reused standalone or in another composite. Status:
  Internet-Draft revision -19 (21 April 2026), **expired
  23 October 2026, not an RFC**. Whether a -20 revision exists is
  UNVERIFIED. The plan therefore treats composite signatures as a
  *transition mechanism*, not a permanent standard: use them while
  the draft is live or under a pinned revision, and design the
  exit to single ML-DSA from the start.
- **Single ML-DSA in X.509 is standardised:** RFC 9881 (October
  2025, S8) covers ML-DSA-44/65/87, pure variant only. This is the
  target end state for certificates and witness identity.
- SLH-DSA in X.509 (RFC 9909, December 2025) is cited in secondary
  sources only and was not re-verified (S9); do not rely on it
  without reading it first.

### 2.3 Transport

- ML-KEM-768 is the NIST-recommended default parameter set (S3,
  section 8): encapsulation key 1,184 bytes, decapsulation key
  2,400 bytes, ciphertext 1,088 bytes, 32-byte shared secret.
  ML-KEM-1024 is the CNSA 2.0 Level V choice (S21).
- Hybrid key establishment follows SP 800-227 §4.6 (S4):
  multi-algorithm KEMs, approved key combiners (§4.6.2), X-Wing
  (ML-KEM + X25519) as the worked example. Transport hardening is
  separate from signing: ML-KEM protects witness and relayer
  channels; it does not make bridge signatures quantum-safe.
- Firmware and release signing: LMS/XMSS under SP 800-208 (S5),
  with key generation and signing inside a hardware module that
  does not export the private key; CNSA 2.0 requires LMS/XMSS for
  firmware/software signing (S21).

### 2.4 Timeline anchors

- NIST IR 8547 (S6): quantum-vulnerable algorithms deprecated
  after 2030, disallowed after 2035; post-quantum key
  establishment by 31 December 2030, post-quantum signatures by
  31 December 2031 (federal high-value systems).
- NSM-10: 2035 as the target for completing the transition (S6).
- CNSA 2.0 algorithms: ML-KEM-1024, ML-DSA-87 (S21). The
  per-class deadline ladder (2027/2030/2033) is NOT re-verified
  against the NSA primary; the plan uses the IR 8547 dates as its
  anchors and treats the CNSA ladder as secondary-sourced.

## 3. Rollout phases

### Phase 0 — Inventory and crypto-agility (before any signing change)
- Inventory every classical key in the bridge path: witness keys,
  relayer keys, contract admin keys, TLS endpoints, release
  signing keys.
- Record the amendment activation state (threat-model.md, T9):
  resolve whether `fixAmendmentMajorityCalc` is enabled on the
  live network.
- Build crypto-agility into the attestation format now: a version
  field, a scheme identifier per signature, and a domain
  separator that includes the scheme version. Attestations that
  cannot express "signed with scheme X, version Y" cannot be
  migrated without a flag day.
- **Gate 0.** Inventory complete and signed off; attestation
  format carries scheme + version; no value has moved under the
  new format yet.

### Phase 1 — Hybrid composite witness signatures (transition)
- Each witness signs every attestation twice: once classically
  (Ed25519, the inherited scheme) and once with ML-DSA-65.
  Verification is AND-mode (S7): both must validate.
- Composite profiles follow the LAMPS draft (S7), pinned to
  revision -19, with the key non-reuse rule enforced: composite
  keys are never used standalone or in another composite.
- Quorum counting is unchanged (24 of 35) but counts only
  attestations that pass AND-mode verification. The harness's
  quorum test (t05_quorum) is re-run against the composite
  verifier before deployment.
- Transport moves to hybrid ML-KEM in the same phase: ML-KEM-768
  + X25519 (X-Wing pattern, S4) for witness and relayer channels,
  with NIST-approved key combiners (S4, §4.6.2).
- **Gate 1.** Composite attestations verify end-to-end on a
  test deployment; a classical-only attestation is rejected;
  an ML-DSA-only attestation is rejected (the hybrid is
  mandatory in this phase); the supply identity reconciles
  exactly after every test transfer.

### Phase 2 — Quorum migration with dual-signature window
- The witness set migrates key by key. During the window, the
  signer list accepts both classical-only keys (legacy witnesses
  not yet migrated) and composite keys, but a claim executes only
  when the composite-key witnesses alone reach quorum — i.e. the
  effective quorum is 24 composite attestations, so the bridge is
  quantum-safe as soon as the window opens, not when it closes.
- New witnesses are onboarded composite-only. Legacy keys are
  retired as their operators migrate; no new classical-only key
  is ever added.
- **Gate 2.** 24 witnesses hold composite keys and have signed
  live test claims; zero claims in the window executed on
  classical-only attestations; the signer list contains no
  classical-only key added after the window opened.

### Phase 3 — Classical deprecation
- Classical component signatures stop being verified. Witness
  attestations are ML-DSA-65 only, identified per RFC 9881 (S8).
- The domain separator is versioned forward
  (e.g. `pftl-bridge/v2`): attestations under the old domain are
  rejected, so a classical attestation cannot be replayed into
  the post-quantum bridge (threat-model.md, T3).
- Release and firmware signing moves to LMS/XMSS under SP 800-208
  (S5), with hardware-module key custody.
- **Gate 3.** Zero classical signatures accepted in a full audit
  window; a classical attestation submitted to the new verifier
  is rejected; the supply identity reconciles exactly.

### Phase 4 — Full ML-DSA operation and review
- Bridge signing is ML-DSA-65 (or ML-DSA-87 if the category-5
  decision is taken — see section 2.1). SLH-DSA remains the
  documented lattice-failure fallback, not the deployed scheme.
- Annual review: re-check the LAMPS draft status (whether a
  composite standard has become an RFC), re-check the GRI threat
  timeline, and re-run the harness against the deployed verifier.
- **Gate 4.** Independent re-run of this pack's harness against
  the deployed attestation verifier passes; the assumptions
  register is updated with the deployment's real witness set,
  quorum, and contract addresses.

## 4. Verification gates (summary)

| Gate | Criterion | Evidence |
|---|---|---|
| Gate 0 | Inventory complete; format carries scheme + version | Inventory document; format specification |
| Gate 1 | Composite AND-mode verifies; classical-only and ML-DSA-only rejected; supply identity reconciles | Test deployment logs; harness re-run (t04_tamper, t05_quorum) |
| Gate 2 | 24 composite witnesses; no claim on classical-only attestations | Signer-list snapshot; claim audit |
| Gate 3 | Zero classical signatures accepted; old domain rejected | Audit-window log; negative test |
| Gate 4 | Harness passes against deployed verifier; assumptions register updated | Harness output; updated register |

## 5. Rollback protection

- **Versioned domains.** Every attestation domain includes the
  scheme version. A verifier accepts exactly the current version
  (and, during a window, the immediately previous one). Old
  versions are rejected, never downgraded to.
- **No downgrade after cutover.** Once Gate 3 passes, the
  classical verification path is removed from the verifier, not
  merely disabled. A rollback to classical verification requires
  a governance action with the same quorum as a bridge upgrade,
  and is itself recorded as an incident (section 6).
- **In-flight claims.** A claim that is in-flight (s_in-flight,
  S10, section 1.3) at a phase boundary completes under the rules
  in force when it was created; no in-flight claim is re-validated
  under new rules, and no in-flight claim is cancelled by a phase
  change. The supply identity is reconciled at every boundary.
- **Claim-ID continuity.** Claim IDs are never reused across a
  phase boundary. A new phase starts a new claim-ID epoch, and
  the verifier rejects claim IDs from a closed epoch.
- **Emergency halt.** A pre-agreed halt switch freezes minting
  (not the ledger) when the compromise threshold in section 6 is
  met. The halt is itself a quorum action, and un-halting requires
  the same quorum plus a post-incident review.

## 6. Key-compromise response procedures

### 6.1 Detection
- Continuous monitoring: attestation patterns per witness
  (unexpected signing times, duplicate claims, amounts outside
  the witness's history), signer-list changes, and public
  reporting of quantum progress against the timeline in
  threat-model.md, section 2.2.
- Any witness operator reports a suspected compromise within 24
  hours of discovery; the report goes to all other operators and
  to the bridge's public incident channel.

### 6.2 Containment (first 24 hours)
- The compromised key is removed from the signer list by
  governance action. The inherited code already drops
  attestations from signers no longer in the list (`claimHelper`,
  S12); removal is therefore effective as soon as the list
  updates.
- If compromised keys reach 12 (half the quorum margin: 24 - 12),
  minting halts under the emergency switch (section 5). The
  threshold is deliberately set at half the quorum margin so the
  bridge halts before a quorum can be assembled from compromised
  keys.
- All in-flight claims are frozen and reconciled against the
  supply identity before any resume.

### 6.3 Recovery
- The compromised witness generates a fresh key pair (ML-DSA-65
  if Phase 1 or later, otherwise classical with a dated migration
  commitment) inside a hardware module that does not export the
  private key (S5 practice, applied to witness keys).
- The new key is onboarded through the normal signer-list
  governance path; the old key is never re-added.
- A post-incident review establishes what the compromised key
  signed, whether any claim it voted for was anomalous, and
  whether any value moved. The review is published with the
  incident record.

### 6.4 Quantum-compromise (CRQC) response
- If a CRQC is credibly demonstrated against ECDSA/Ed25519, the
  bridge halts minting immediately — before waiting for a quorum
  vote — under the pre-agreed emergency authority, and Phase 1
  (hybrid composite) is executed on an emergency timetable.
  Classical witness keys are assumed compromised as a class, not
  individually: the response is migration, not per-key revocation.
- The Groth16 bridge-proof exposure (threat-model.md, T7) has no
  equivalent emergency fix: if pairing assumptions fall, bridge
  proofs are suspended and the bridge operates on quorum
  attestation plus supply reconciliation alone until a
  post-quantum proof system is deployed. This is recorded here as
  an accepted residual risk, not as a solved problem.

## 7. Open dependencies

- Groth16 replacement for bridge proofs: no post-quantum proof
  system is specified for this bridge. Until one is, T7 stands.
- Destination-chain post-quantum authorisation: the EVM side has
  no ML-DSA path in this plan (T8). Minimise external value at
  risk until the destination chain offers one.
- LAMPS composite standardisation: the hybrid vehicle is an
  expired Internet-Draft (S7). If it becomes an RFC, re-pin to
  the RFC; if it is abandoned, the exit is single ML-DSA per
  RFC 9881 (S8), which this plan already targets as the end state.
