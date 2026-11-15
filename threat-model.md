# Quantum-adversary threat model

## 1. Scope and method

This threat model covers the bridge architecture pinned in
`architecture.md`, against a quantum adversary — an attacker with a
cryptographically relevant quantum computer (CRQC), and, before one
exists, an attacker harvesting data today to decrypt later. Every
threat names the asset, the mechanism, the primary-source citation,
and the harness or migration control that addresses it. Where the
architecture is an assumption (see findings.md, assumptions
register), the threat is stated conditionally: "if the bridge is
built as assumed, then…".

## 2. Adversary and timeline

### 2.1 The adversary

- **CRQC adversary.** Runs Shor's algorithm (S19) against classical
  public keys. A CRQC breaks RSA, ECDSA, and EdDSA, and weakens
  symmetric cryptography. It does not break ML-DSA, ML-KEM, or
  SLH-DSA as standardised (S1, S2, S3).
- **Harvest-now-decrypt-later (HNDL) adversary.** Records encrypted
  traffic and public keys today; decrypts or forges when a CRQC
  arrives. Named explicitly by the joint CISA/NSA/NIST
  quantum-readiness factsheet (S22, unverified against the primary).
  Relevant because bridge attestations and public keys are
  long-lived, public, and permanent on a ledger: "years of public
  keys already sit on a permanent ledger" is exactly the exposure
  the whitepaper's from-genesis ML-DSA design is meant to avoid
  (S10, section 1.11).
- **Classical adversary.** Included for completeness: a classical
  attacker who compromises witness keys, replays attestations, or
  exploits ordering. The harness tests the logic defences against
  this adversary directly.

### 2.2 Timeline anchors (why the threat is current, not hypothetical)

- Mosca (2015): "I estimate a 1/2 chance of breaking RSA-2048 by
  2031" (S18, verbatim from the ePrint abstract).
- Global Risk Institute, Quantum Threat Timeline Report 2025
  (March 2026, 26 experts): a CRQC is "quite possible" (28-49%)
  within 10 years and "likely" (51-70%) within 15 years (S20).
  This is an expert survey, not a measurement.
- NIST IR 8547 (final, October 2026): quantum-vulnerable public-key
  algorithms are deprecated after 2030 and disallowed after 2035;
  federal high-value systems must adopt post-quantum key
  establishment by 31 December 2030 and post-quantum signatures by
  31 December 2031 (S6).
- NSA (CNSA 2.0 FAQ): "NSA does not know when there will be a CRQC.
  Expert assessments disagree significantly about timing" (S21).
  No CRQC exists in the public record as of 30 October 2026; that
  is a statement about the public record, not proof of absence.
- Mosca's inequality (S18): if X (years data must stay secret) + Y
  (years to migrate) > Z (years until a CRQC), the data is at risk.
  Bridge witness keys and locked value have long X; migration of a
  deployed bridge has long Y; Z is the uncertain 10-15 year band
  above. The inequality is the reason migration planning starts
  before a CRQC exists.

## 3. Assets

| Asset | Value at risk | Lifetime |
|---|---|---|
| Locked source-chain funds (door/lock custody) | Full locked value; a forged quorum releases it | As long as the bridge holds value |
| Mint authority on the destination chain | Unbounded wrapped supply if minting is forged; breaks the supply identity (S10, section 1.3) | Life of the bridge |
| Witness signing keys | Each key is one quorum vote; 24 compromised keys forge any claim | Key lifetime; public keys are permanent on the ledger once used |
| Attestation records | Replayed or reordered attestations can double-mint or misdirect value | Permanent (ledger history) |
| Bridge proofs (Groth16) | Soundness break forges reserve/bridge proofs | Life of the proof system |
| External-chain contracts | Their own classical cryptography (S10, section 1.11, scope limit) | Life of the deployment |

## 4. Threats

### T1 — Signer compromise by a quantum adversary
- **Mechanism.** Witness signing keys are secp256k1 or ed25519
  (S14), both classical. Shor's algorithm (S19) recovers the
  private key from the public key. Witness public keys are on the
  ledger and therefore harvestable today (HNDL). A quantum
  adversary that recovers 24 witness private keys can forge a
  quorum of attestations for any claim and drain the lock.
- **Threshold analysis.** The whitepaper's quorum is 24 of 35
  (S10). Compromising 12 witnesses is insufficient; 24 is
  sufficient. The harness confirms the boundary exactly: 23
  attestations fail, 24 succeed (t05_quorum). The same arithmetic
  applies to key compromise: the attacker needs 24 of 35 keys, not
  one. But note the validator-count conflict (architecture.md,
  section 4): if the set is 53, 24 is only 45.3% of it.
- **Severity.** High impact, medium likelihood on the 10-15 year
  horizon (S20). The exposure is structural, not a bug: the
  inherited witness design is classical by construction.
- **Controls.** Migration to ML-DSA witness signatures
  (migration.md, phases 1-2). Until then: witness key hygiene,
  hardware-backed keys, and the key-compromise response procedure
  (migration.md, section 6). The harness does not test this threat
  — it is a cryptographic property, not a logic property — and the
  pack says so in limitations.md.

### T2 — Quorum design weakness
- **Mechanism.** A quorum that is too low, or a signer set that is
  too small, too centralised, or too correlated, lets a minority
  of compromised or colluding witnesses forge claims. The inherited
  design authorises through the door account's `SignerListSet`
  quorum (S14), and the code enforces `weight >= quorum` (S12).
  Nothing in the code checks signer independence.
- **Reference points.** Wormhole: 13-of-19 guardians (68.4%, S15).
  Axelar whitepaper: 80% of validators must co-sign (S16, 2021
  figure; current threshold not re-verified). LayerZero: the
  application sets its own DVN quorum; there is no protocol-wide
  figure (S17). The whitepaper's 24-of-35 is 68.6% — in line with
  Wormhole's supermajority, below Axelar's stated 80%.
- **Severity.** Medium. The stated threshold is a supermajority,
  but the actual witness set, its size, and its operator diversity
  are all unverified (A3). A 24-of-35 quorum over 35 keys held by
  few operators is weaker than the same quorum over 35 independent
  operators.
- **Controls.** Publish the witness set and operator diversity;
  weight quorum by independent operators, not raw key count;
  monitor attestation patterns for correlated signing. Harness
  t05_quorum verifies the threshold boundary in the logic model.

### T3 — Cross-chain replay
- **Mechanism.** An attestation valid on one bridge or chain is
  replayed on another, minting value that was never locked there.
  The defence is domain separation: attestations must bind the
  bridge identity, the source and destination chains, and the
  claim, and the destination must verify all of them.
- **Confirmed defences.** The whitepaper requires "domain-separated
  contexts for … bridge witnesses" (S10, section 1.11). The code
  rejects a wrong destination chain (`tecXCHAIN_WRONG_CHAIN`) and
  a sending-account mismatch (`tecXCHAIN_SENDING_ACCOUNT_MISMATCH`)
  (S12). Wormhole binds replay protection to the VAA's unique
  (emitter_chain, emitter_address, sequence) index plus the
  destination's already-processed check (S15).
- **Severity.** High impact if domain separation is missing or
  misconfigured; low likelihood if the confirmed defences are
  implemented as specified. The risk concentrates in the
  *unverified* part: the destination contract for this bridge is
  not published, so its domain checks cannot be inspected (A3).
- **Controls.** Harness t04_tamper (wrong domain rejected) and
  t06_negative (cross-chain replay rejected). Migration phase
  gates require a domain-separation audit of the destination
  contract before any value moves (migration.md, section 4).

### T4 — Double-spend paths
- **Mechanism.** The same source lock mints twice on the
  destination chain, creating wrapped supply with no backing and
  breaking the supply identity s_native + s_shielded + s_external
  + s_in-flight = s_authorized (S10, section 1.3).
- **Confirmed defences.** The claim-ID counter increments per
  commit, and `finalizeClaimHelper` erases the claim-ID ledger
  entry after a successful claim; a second claim with the same ID
  fails (`tecXCHAIN_NO_CLAIM_ID`) (S12). Duplicate attestations
  from the same signer replace rather than accumulate
  (`onNewAttestations`, S12).
- **Residual paths.** (a) Two different claim IDs for the same
  lock, if the source chain permits the lock to be recorded twice
  — the claim-ID defence binds claims, not locks; the source
  chain's lock accounting is the backstop. (b) A destination
  contract that does not track processed claims can be fed the
  same verified attestation set twice — the ledger-side defence
  does not protect a destination contract that keeps no
  already-processed set. (c) A chain reorganisation on the source
  chain that un-locks value after the destination has minted.
  None of these is tested by the harness; all are listed in
  limitations.md.
- **Severity.** High impact; likelihood depends on the
  destination contract, which is unpublished (A3).
- **Controls.** Harness t02_duplicate (idempotent no-op),
  t03_double_spend (second mint rejected), t06_negative
  (stale-nonce and exact replay rejected). The migration plan
  requires the destination contract to maintain a processed-claim
  set and to reconcile against the supply identity continuously
  (migration.md, section 4).

### T5 — Reordered and duplicated validations
- **Mechanism.** Validations arriving out of order, or delivered
  twice (network retries, relayer duplication), must not change
  the resulting state or mint twice. This is a logic property of
  the attestation scheme, independent of cryptography.
- **Confirmed behaviour.** The code's claim handling is
  order-independent in effect: attestations accumulate per claim
  ID and the claim executes once, when quorum is reached
  (`claimHelper`, `onNewAttestations`, S12).
- **Severity.** Medium impact (double-mint or inconsistent state),
  high likelihood of occurrence in normal operation (retries are
  routine) — which is why the defence must be in the logic, not
  in operator discipline.
- **Controls.** Harness t01_reorder (2 orders x 2 runs, identical
  final-state digest ea00ee470531c76d6e30f57eefcd97ee412cd1cfffef28d69c694962d5fee257)
  and t02_duplicate (duplicate is an idempotent no-op).

### T6 — Tampered attestations
- **Mechanism.** An attacker alters the amount, destination, or
  nonce in an attestation, or forges a witness signature, to
  redirect or inflate a mint. The defence is signature binding:
  the signature covers every field, so any alteration invalidates
  it, and the quorum counts only valid signatures.
- **Severity.** High impact, low likelihood against a sound
  signature scheme; the likelihood rises sharply once witness
  keys are quantum-recoverable (T1). Tamper resistance is only as
  strong as the signature scheme.
- **Controls.** Harness t04_tamper (altered amount, wrong domain,
  forged signature all rejected; no mint executed). Note the
  model's signatures are HMAC tags for logic testing only
  (bridge_model.py); real tamper resistance depends on the real
  scheme, which is classical today (T1).

### T7 — Bridge-proof soundness (Groth16)
- **Mechanism.** "SP1 reserve and bridge proofs wrap in Groth16"
  (S10, section 1.11). Groth16 is a pairing-based zk-SNARK: its
  soundness rests on classical assumptions (discrete logarithms
  in pairing groups), which Shor's algorithm breaks. A quantum
  adversary that breaks the pairing assumption can forge a bridge
  proof. This is explicitly outside the whitepaper's post-quantum
  claim: "The scope ends there" (S10, section 1.11).
- **Severity.** High impact, low-to-medium likelihood on the
  timeline in S20; the proof system is a single point of trust
  for reserve and bridge verification, and its replacement is a
  research problem, not a configuration change.
- **Controls.** None in this pack beyond disclosure: the migration
  plan (migration.md, section 5) records Groth16 replacement as
  an open research dependency and requires that bridge proofs
  never be the sole control — quorum attestation and supply
  reconciliation must independently bound what a forged proof
  can withdraw.

### T8 — External-chain contract cryptography
- **Mechanism.** "External-chain contracts use their own
  cryptography" (S10, section 1.11). The destination contract on
  Base is an EVM contract: ECDSA signatures, keccak256, classical
  assumptions. A quantum adversary can forge EOA signatures and
  compromise the contract's admin keys. The ledger's ML-DSA claim
  does not extend to the destination chain.
- **Severity.** High impact, medium likelihood on the S20 horizon.
  This is the largest quantum exposure in the assessed bridge
  that the ledger's own design cannot fix: the quantum-safe side
  ends at the ledger boundary.
- **Controls.** Migration plan (migration.md, section 5): the
  destination contract needs its own post-quantum roadmap
  (account-abstraction / ML-DSA-based authorisation on the EVM
  side, or migration of custody off classical EOAs). Until then,
  minimise value at risk on the external side and keep the
  in-flight and external categories small relative to authorised
  supply.

### T9 — Governance and amendment risk
- **Mechanism.** Bridge behaviour that depends on ledger
  amendments inherits amendment risk. postfiatd diverges from
  upstream XRPL: 67/100 after `fixAmendmentMajorityCalc` versus
  80/100 upstream (S12, S13), with a 2-week majority hold. Whether
  the fix is enabled on the live network is unverified (S12).
  An amendment that changes bridge validation, quorum rules, or
  the claim flow could weaken the bridge; an amendment that never
  activates leaves the bridge on the pre-fix threshold.
- **Severity.** Medium. The uncertainty itself is the risk: the
  effective threshold is 79.6875% or 67%, unknown.
- **Controls.** Resolve the activation status with a live ledger
  feature check before the bridge carries value; pin the
  amendment state in the bridge's deployment record.

### T10 — Key-compromise response failure
- **Mechanism.** A compromised witness key that is not revoked
  promptly continues to vote. The inherited design removes
  attestations from signers no longer in the signer list
  (`claimHelper` erases attestations whose key check fails, S12),
  but removal depends on the signer list being updated, which is
  a governance action.
- **Severity.** Medium-high: the window between compromise and
  revocation is the attacker's window.
- **Controls.** Key-compromise response procedure (migration.md,
  section 6): detection, signer-list update, quorum re-keying,
  and a pre-agreed compromise threshold that halts minting.

## 5. Trust boundaries

| Boundary | Trusted side | Untrusted / partially trusted side | What crosses it |
|---|---|---|---|
| Ledger <-> witness servers | Ledger consensus, ML-DSA validator signatures (S10) | Witness operators and their classical keys (S14) | Attestations |
| Source chain <-> destination chain | Source lock state, claim-ID consumption (S12) | Destination contract and its classical cryptography (S10 scope limit) | Mint/burn instructions |
| Bridge proofs <-> ledger | Ledger verification of Groth16 proofs (S10) | Proof generation, pairing assumptions (T7) | Reserve/bridge proofs |
| Custody perimeter <-> market | Reserve arithmetic, supply identity (S10) | Custodian honesty, undisclosed liabilities (S10, section 1.1) | Value |
| Governance <-> bridge code | Amendment process (S12, S13) | Amendment activation state (UNVERIFIED) | Rule changes |

## 6. Residual risk summary

The ledger side of the bridge is quantum-safe by design (ML-DSA-65
from genesis, S10). The quantum exposure concentrates in exactly
the places the whitepaper's scope limit names: bridge proofs
(Groth16, T7), external-chain contracts (classical, T8), and the
inherited witness keys (secp256k1/ed25519, T1). The logic defences
— quorum, claim-ID consumption, domain separation, duplicate and
reorder handling — are sound in the inherited code and verified in
the harness, but they are classical-logic defences: they stop
replay and duplication, not a quantum adversary holding 24 witness
keys. The migration plan (migration.md) addresses the key and
transport exposure; T7 and T8 have no complete fix today and are
recorded as open dependencies.
