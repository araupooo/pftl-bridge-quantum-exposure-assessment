# Limitations

What was not verified, what failed or was inconclusive, and what
this pack cannot establish. Nothing in this file is a gap to be
filled silently later; each item is a disclosed limit on the
assessment.

## 1. The bridge premise is unverified

No primary source confirms an ERC-20 representation on Base, a Base
bridge contract, or a genesis bridging procedure (findings.md, A1,
A2). The whitepaper contains zero occurrences of "ERC-20" and no
mention of the Base chain. The assessment therefore evaluates a
stated premise, not a confirmed deployment. If the bridge is not
planned as premised, the Base- and ERC-20-specific analysis does
not apply, although the logic findings and the migration plan still
hold for any bridge built on the inherited XChainBridge design.

## 2. No deployed bridge was available to verify

No bridge contract address, witness list, operator list, signer
quorum, or mint-authority configuration is published for this
bridge (A3). The architecture is pinned from the inherited code
and the whitepaper only. The harness's 24-of-35 quorum is the
whitepaper's validator figure applied to bridge witnesses by
assumption (A4), and the validator count is conflicted — 35 in
the whitepaper's arithmetic, 53 in the homepage snapshot of
21 September 2026 (A5). All quorum conclusions must be re-pinned
to the real deployment before value moves.

## 3. The harness is a logic model, not a cryptographic test

Attestation "signatures" in the harness are HMAC-SHA256 tags with
deterministically derived keys (scripts/bridge_model.py). They
exist to test ordering, duplication, quorum counting, and tamper
rejection in the attestation logic. They say nothing about the
security of ML-DSA, Ed25519, secp256k1, or any real signature
scheme. A PASS here is a logic PASS, not a cryptography PASS.
The quantum threat to witness keys (threat-model.md, T1) is
assessed from the standards and the code, not measured by the
harness.

## 4. Residual double-spend paths not tested

The harness proves that a consumed claim ID cannot mint twice in
the model. It does not close these paths, which are outside the
model:

- **Source-chain double recording.** The claim-ID defence binds
  claims, not locks. If the source chain permits the same lock to
  be recorded under two different claim IDs, both can mint. The
  backstop is the source chain's lock accounting, which was not
  tested.
- **Destination re-mint without a processed-claim set.** The
  ledger-side claim-ID erasure does not protect a destination
  contract that keeps no already-processed set. If the destination
  contract accepts the same verified attestation set twice, it
  mints twice. The destination contract is unpublished (A3), so
  its processed-claim handling could not be inspected.
- **Source-chain reorganisation.** A reorganisation that un-locks
  value after the destination has minted is not modelled. The
  demonstrated A666 route used a 20 m 12 s mainnet round trip and
  the Arbitrum pfUSDC route used roughly 6.4-day trustless
  confirmations (S10, section 2.3); the assessed bridge's
  finality rule is unpublished.

## 5. Live-network state not checked

- Whether `fixAmendmentMajorityCalc` (67% threshold) is enabled
  on the live network is unverified (A6). The effective amendment
  threshold is 79.6875% or 67%, unknown.
- No live ledger queries were made; no current balances,
  validator set, or amendment status is claimed.
- The homepage network snapshot (53 validators, 39 verified
  domains, ledger ~6.5M) is dated 21 September 2026 and is not
  current.

## 6. Secondary-sourced items

The following are cited from secondary summaries, not from the
primary document, and are marked as such wherever used:

- CNSA 2.0 per-class deadline ladder (2027/2030/2033) — the NSA
  FAQ PDF was not retrievable from this environment (S21). The
  migration plan anchors on IR 8547 dates instead.
- RFC 9909 (SLH-DSA in X.509) — not re-verified; not relied on
  (S9).
- The joint CISA/NSA/NIST harvest-now-decrypt-later factsheet —
  not fetched (S22).
- CA/Browser Forum ML-DSA ballot status — not checked; not relied
  on (S23).
- Axelar's 80% figure is from the 2021 whitepaper; the current
  on-chain threshold was not re-verified (S16).
- Whether a -20 revision of the LAMPS composite-signatures draft
  exists after the -19 expiry — not checked (S7, A10).
- The Global Risk Institute figures are from the executive
  summary PDF, which was fetched and read; the full report PDF
  was not fetched. The figures are expert-survey estimates, not
  measurements.

## 7. Failed / inconclusive checks

- **No failed harness checks.** 7 of 7 checks pass, 29 of 29
  assertions pass, 0 fail. There is nothing failed to disclose
  from the harness run itself.
- **Inconclusive by design.** The two open dependencies in
  migration.md (section 7) are inconclusive, not failed:
  Groth16 replacement for bridge proofs has no specified
  post-quantum successor for this bridge, and destination-chain
  post-quantum authorisation has no specified path. Both are
  recorded as open, not resolved.
- **Primary-source fetch failures.** The NSA CNSA 2.0 FAQ PDF
  download returned an HTML page instead of a PDF from this
  environment; the CNSA algorithm table was verified from the
  NSA page crawl instead, and the deadline ladder is marked
  secondary-sourced (item 6 above). The XLS-38d spec landing
  page returned 301 when fetched directly; the transaction-type
  pages were used instead (S14).

## 8. Out of scope

- Ledger account-key migration: accounts already sign with
  ML-DSA-65 from genesis (S10), so there is nothing to migrate.
- Economic analysis of bridge fees, liquidity, or token price:
  not attempted.
- Legal, custodial, or insolvency analysis: the whitepaper
  states these lie outside what any proof establishes (S10,
  section 1.1).
- A security audit of any contract: no contract for this bridge
  is published to audit.
