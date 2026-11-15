# Primary-source citations

Every specification-derived claim in this pack traces to one of the
sources below. Each entry gives the document, the section or table, the
version or publication date, and the URL as fetched on 2026-11-15.
Entries marked **UNVERIFIED** are claims that could not be confirmed
against a primary source; the pack never asserts them as fact.

## Post-quantum signature and KEM standards

### S1 — NIST FIPS 204, ML-DSA (final, 13 August 2024)
- Document: "Module-Lattice-Based Digital Signature Standard",
  derived from CRYSTALS-Dilithium.
- PDF: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf
  (65 pp., fetched and read 2026-11-15).
- Landing page: https://csrc.nist.gov/pubs/fips/204/final
  ("Date Published: August 13, 2024").
- Table 2 (sizes in bytes): ML-DSA-44 — private key 2,560, public key
  1,312, signature 2,420; ML-DSA-65 — 4,032 / 1,952 / 3,309;
  ML-DSA-87 — 4,896 / 2,592 / 4,627.
- Section 4, Table 1 (claimed security categories): ML-DSA-44
  category 2, ML-DSA-65 category 3, ML-DSA-87 category 5.
  Categories are defined by reference attack, not bit counts.
- Section 4 caveat: ML-DSA-44 drops from category 2 to category 1 if
  the random bit generator provides less than 192 bits of security.
- Section 3.1 / Table 2 note: the private key may be stored as only
  the 32-byte seed, sufficient to regenerate the rest.
- Planning note on the landing page (31 Jul 2026): an errata
  spreadsheet lists minor issues for a future revision.

### S2 — NIST FIPS 205, SLH-DSA (final, 13 August 2024)
- Document: "Stateless Hash-Based Digital Signature Standard", based
  on SPHINCS+. Security rests only on the underlying hash functions
  (SHA-2 or SHAKE), not on lattice problems.
- PDF: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf
  (61 pp., fetched and read 2026-11-15).
- Landing page: https://csrc.nist.gov/pubs/fips/205/final.
- Table 2 (12 parameter sets: 2 hash families x 3 categories x
  "s"/"f" variants). Public keys 32 / 48 / 64 bytes; signatures:
  128s 7,856; 128f 17,088; 192s 16,224; 192f 35,664; 256s 29,792;
  256f 49,856 bytes.
- Section 11 nuance: all twelve parameter sets meet their claimed
  EUF-CMA security categories "except SLH-DSA-SHA2-128f and
  SLH-DSA-SHAKE-128f" for message-bound signatures.

### S3 — NIST FIPS 203, ML-KEM (final, 13 August 2024)
- Document: "Module-Lattice-Based Key-Encapsulation Mechanism
  Standard", derived from CRYSTALS-Kyber.
- PDF: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
  (56 pp., fetched and read 2026-11-15).
- Landing page: https://csrc.nist.gov/pubs/fips/203/final.
- Table 3 (sizes in bytes): ML-KEM-512 — encapsulation key 800,
  decapsulation key 1,632, ciphertext 768, shared secret 32;
  ML-KEM-768 — 1,184 / 2,400 / 1,088 / 32; ML-KEM-1024 — 1,568 /
  3,168 / 1,568 / 32.
- Section 8: "NIST recommends using ML-KEM-768 as the default
  parameter set, as it provides a large security margin at a
  reasonable performance cost."

### S4 — NIST SP 800-227, key-encapsulation mechanisms (final, 18 September 2025)
- Document: "Recommendations for Key-Encapsulation Mechanisms".
- PDF: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-227.pdf
  (fetched and read 2026-11-15).
- Landing page: https://csrc.nist.gov/pubs/sp/800/227/final
  (DOI 10.6028/NIST.SP.800-227).
- Section 4.6, "Multi-Algorithm KEMs and PQ/T Hybrids": a
  multi-algorithm scheme "will be secure if at least one of the
  component schemes is secure"; X-Wing KEM is given as the hybrid
  PQ/T example (ML-KEM + X25519). Approved key combiners are in
  Section 4.6.2.

### S5 — NIST SP 800-208 (October 2020)
- Document: "Recommendation for Stateful Hash-Based Signature Schemes".
- Landing page: https://csrc.nist.gov/pubs/sp/800/208/final
  ("Date Published: October 2020").
- Approves stateful hash-based signatures LMS/HSS and XMSS/XMSS^MT
  (RFC 8391/8554) for federal use, for firmware and software signing,
  requiring key generation and signing inside a hardware module that
  does not export the private key.

### S6 — NIST IR 8547, "Transition to Post-Quantum Cryptography Standards" (final, October 2026)
- PDF: https://nvlpubs.nist.gov/nistpubs/ir/2026/NIST.IR.8547.pdf
  (fetched and read 2026-11-15; final published 27 October 2026).
- Landing page: https://csrc.nist.gov/pubs/ir/8547/final.
- Quantum-vulnerable public-key algorithms (RSA, ECDSA, EdDSA
  signatures; DH/MQV/RSA key establishment) are deprecated after 2030
  and disallowed after 2035 under NIST standards and guidelines —
  in the final version this covers all strengths, including 128-bit
  (P-256, RSA-3072, Ed25519).
- Federal high-value/high-impact systems: post-quantum key
  establishment by 31 December 2030, post-quantum signatures by
  31 December 2031 (EO 14412, 22 Jun 2026; OMB M-26-15, 24 Jun 2026).
- National Security Memorandum 10 (NSM-10) sets 2035 as the target
  for completing the transition.

## Hybrid signatures and X.509

### S7 — IETF LAMPS draft-ietf-lamps-pq-composite-sigs, revision -19 (21 April 2026)
- Document: composite ML-DSA signatures (ML-DSA hybrid with RSA-PSS,
  ECDSA, Ed25519, Ed448) for X.509/PKIX.
- Status: **Internet-Draft, NOT an RFC**. Revision -19 expired
  23 October 2026.
- Datatracker: https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/
- Draft text (revision -19):
  https://ftp.registro.br/internet-drafts/draft-ietf-lamps-pq-composite-sigs-19.txt
- Verification is AND-mode: both component signatures must validate.
- Component keys used in a composite MUST NOT be reused standalone
  or in another composite.
- Example composite profile: `id-MLDSA65-Ed25519-SHA512`,
  OID 1.3.6.1.5.5.7.6.48.
- **UNVERIFIED:** whether a -20 revision exists after the 23 October
  2026 expiry; not checked.

### S8 — RFC 9881, "Internet X.509 PKI — Algorithm Identifiers for ML-DSA" (October 2025)
- Standards Track. Covers ML-DSA-44/65/87, pure variant only.
- https://datatracker.ietf.org/doc/html/rfc9881 (abstract, section 1).

### S9 — RFC 9909, SLH-DSA algorithm identifiers in X.509 (December 2025)
- **UNVERIFIED against the primary:** cited in secondary sources
  only; the RFC text was not re-checked in this pack. Do not rely
  on it without reading it first.

## The ledger, its whitepaper, and its inherited bridge code

### S10 — Post Fiat whitepaper
- https://postfiat.org/whitepaper/ (crawled 2026-11-15).
- Section 1.1: the native asset has a fixed genesis supply; every
  native fee burns; no validator reward exists.
- Section 1.3 (supply identity):
  s_native + s_shielded + s_external + s_in-flight = s_authorized.
  "A claim occupies exactly one category at each stage of its life.
  Export moves it from native through in-flight to external."
  Cash-leg identity: W_cash = S_cash + D + B - R.
- Section 1.11 ("What ML-DSA covers"): "Accounts and validators sign
  with ML-DSA-65 from genesis: 1,952-byte public keys, 3,309-byte
  signatures, deterministic verification, and domain-separated
  contexts for transactions, block certificates, bridge witnesses,
  and admission receipts." "A quorum of q=24 from 35 validators
  carries 24x3,309=79,416 signature bytes plus identifiers; prepare
  and precommit sets double that before framing."
- Section 1.11 (scope limit): "The scope ends there. Asset-Orchard
  authorization uses RedPallas, its proofs Halo2 over the Pasta
  curves, its note encryption classical key agreement; SP1 reserve
  and bridge proofs wrap in Groth16; external-chain contracts use
  their own cryptography."
- Section 2.3 (demonstrated bridge evidence): A666 primary-market
  route on Ethereum mainnet, "20 m 12 s mainnet round trip";
  "100.5 USDC -> 100 A666 -> 100 wA666, canonical and wrapped supply
  each rising by exactly 100,000,000 atoms"; "the Arbitrum pfUSDC
  route is closed to new ingress after roughly 6.4-day trustless
  confirmations."
- The whitepaper contains **zero** occurrences of "ERC-20" and no
  mention of the Base chain (all "Base" hits are the word "base" in
  formulas). See the assumptions register in findings.md.

### S11 — Post Fiat homepage
- https://postfiat.org/ (crawled 2026-11-15).
- "Every account and validator signs with keys quantum computers
  cannot break, from day one."
- Network snapshot (21 September 2026): 53 validators, 39 verified
  domains, 24h agreement 99.9%+, ledger ~6.5M.
- Note: the whitepaper's quorum arithmetic assumes 35 validators;
  the 53 figure is a later snapshot. The two figures are not
  reconciled in any source checked; the harness uses the
  whitepaper's 24-of-35 figure as stated.
- **UNVERIFIED:** the homepage links the text "How the bridge stays
  post-quantum", but no matching standalone page was located; the
  link target URL was not resolved.

### S12 — postfiatd source code, branch `main` (fetched 2026-11-15)
- Repository: https://github.com/postfiatorg/postfiatd
- Amendment thresholds, `include/xrpl/protocol/SystemParameters.h`:
  `preFixAmendmentMajorityCalcThreshold` = 204/256 (79.6875%),
  `postFixAmendmentMajorityCalcThreshold` = 67/100 (67%),
  majority hold time 2 weeks (`defaultAmendmentMajorityTime`).
- Amendment logic, `src/xrpld/app/misc/detail/AmendmentTable.cpp`:
  `AmendmentSet::computeThreshold` (pre-fix ratio while
  `fixAmendmentMajorityCalc` is not enabled, 67/100 once enabled);
  `passes()`: after the fix, votes must be strictly greater than
  the threshold (except the single-validator case).
- **UNVERIFIED:** whether `fixAmendmentMajorityCalc` is actually
  enabled on the live network. The amendment name was not located
  in `Feature.h`/`Feature.cpp`. The effective live threshold
  (79.6875% vs 67%) is therefore unverified pending a live ledger
  feature/amendment-status check.
- Bridge implementation, `src/xrpld/app/tx/detail/XChainBridge.cpp`
  (2,263 lines, fetched and read 2026-11-15):
  `claimHelper` accumulates signer-list weight and returns
  `tecXCHAIN_CLAIM_NO_QUORUM` unless `weight >= quorum`;
  attestations not matching the claim fields are skipped;
  `onNewAttestations` replaces (does not double-count) a duplicate
  attestation from the same signer; `applyClaimAttestations`
  rejects a sending-account mismatch
  (`tecXCHAIN_SENDING_ACCOUNT_MISMATCH`), a wrong destination chain
  (`tecXCHAIN_WRONG_CHAIN`), attestation sets with no signer-list
  member (`tecXCHAIN_PROOF_UNKNOWN_KEY`), and a missing claim ID
  (`tecXCHAIN_NO_CLAIM_ID`); `finalizeClaimHelper` erases the
  claim-ID ledger entry after a successful claim, so a second claim
  with the same ID finds no entry; `XChainCommit` increments the
  bridge's `sfXChainClaimID` counter per commit.
- Attestation objects, `include/xrpl/protocol/XChainAttestations.h`;
  bridge types, `include/xrpl/protocol/STXChainBridge.h`;
  `docs/DomainAttestation.md`; tests `src/test/app/XChain_test.cpp`.

### S13 — Upstream XRPL (XRPLF/rippled), branch `develop` (fetched 2026-11-15)
- `include/xrpl/protocol/SystemParameters.h`: a single threshold,
  `kAmendmentMajorityCalcThreshold` = 80/100 (80%), majority hold
  time 2 weeks. Upstream `AmendmentTable.cpp` contains zero
  occurrences of `fixAmendmentMajorityCalc` — the fix amendment
  and the 67% threshold are a postfiatd divergence, not upstream.

### S14 — XRPL witness-server and cross-chain bridge documentation
- Witness servers:
  https://xrpl.org/docs/concepts/xrpl-sidechains/witness-servers
  A witness server "acts as a neutral witness for transactions
  between a locking chain and an issuing chain. It listens to the
  door accounts on both sides of a bridge and signs attestations
  that confirm a transaction occurred." Witness signing keys are
  secp256k1 or ed25519 (`SigningKeyType` config).
- Bridge setup tutorial:
  https://xrpl.org/docs/tutorials/how-tos/use-xrpl-sidechains/set-up-xrp-xrp-bridge
  Bridge authorisation is via the door account's `SignerListSet`
  quorum (the tutorial example uses `SignerQuorum: 2` with two
  witnesses); funds release when "enough signatures are submitted
  by the witness servers to reach quorum". For XRP-XRP bridges the
  issuing-chain door must be the genesis account. Requires the
  XChainBridge amendment.
- XLS-38d transaction types:
  https://opensource.ripple.com/docs/xls-38d-cross-chain-bridge/transaction-types/xchainaddclaimattestation/
  (the XLS-38d landing page itself returned 301 when fetched
  directly; the transaction-type pages loaded).
- **UNVERIFIED:** the exact quorum rule for a ledger-specific bridge
  deployment (how many witnesses, what SignerQuorum, who operates
  them) — no deployment-specific document was found. The XRPL
  default above is the inherited mechanism only.

## Reference bridge designs (official docs only)

### S15 — Wormhole
- https://wormhole.com/docs/protocol/security/ and
  https://wormhole.com/docs/learn/infrastructure/guardians/
  (both "Last update: October 28, 2026");
  https://wormhole.com/docs/protocol/infrastructure/vaas/;
  https://wormhole.com/docs/protocol/infrastructure/core-contracts/
- Verifiable Action Approval (VAA): guardians independently observe
  a source-chain event and sign a keccak256 hash of the message
  body; once a two-thirds supermajority — 13 of 19 guardians —
  signs, the signatures plus message form a VAA, which a core
  contract on the destination chain verifies before executing.
  Replay protection comes from the VAA's unique
  (emitter_chain, emitter_address, sequence) index plus the
  destination contract's already-processed check. All guardian
  signatures are classical (secp256k1 ECDSA).

### S16 — Axelar
- Whitepaper v1.0 (January 2021):
  https://docs.axelar.dev/axelar_whitepaper.pdf (sections 1, 5.1).
  "80% of validators must approve and co-sign any transaction out
  of it" for outgoing bridges.
- Governance thresholds:
  https://www.axelar.network/blog/axelar-governance-explained
  (onboarding a new EVM chain: 60% by quadratic voting power,
  September 2023).
- **Caveat:** the 80% figure is from the 2021 whitepaper; current
  on-chain gateway thresholds are set by governance and were not
  re-verified live.

### S17 — LayerZero (OFT)
- https://docs.layerzero.network/v2/developers/canton/oft/overview ;
  https://docs.layerzero.network/v2/developers/starknet/oft/overview
- OFT moves tokens by burn-and-mint (or lock-and-unlock): the source
  OFT/adapter burns (or locks) tokens, a LayerZero message is
  verified by the application-chosen Decentralized Verifier Networks
  (DVNs) configured per lane plus block confirmations, and the
  destination OFT mints (or unlocks) via `lzReceive`. Security is
  application-configured as an X-of-Y-of-N DVN quorum; there is no
  fixed protocol-wide quorum. Replay protection is per-endpoint
  nonce / messaging-library state.

## Quantum-threat timelines

### S18 — Michele Mosca, "Cybersecurity in an Era with Quantum Computers: Will We Be Ready?"
- IACR ePrint 2015/1075 (November 2015):
  https://eprint.iacr.org/2015/1075 (abstract read 2026-11-15).
- Verbatim: "I estimate a 1/2 chance of breaking RSA-2048 by 2031."
- Mosca's inequality: if X (years data must stay secret) + Y (years
  to migrate) > Z (years until a cryptographically relevant quantum
  computer), the data is at risk.
- IEEE Security & Privacy 2018 version: Mosca (2018) 16(5), 38-41.

### S19 — Peter W. Shor, "Algorithms for Quantum Computation" (1995)
- arXiv: https://arxiv.org/abs/quant-ph/9508027
- Shor's algorithm: polynomial-time factoring and discrete
  logarithms on a quantum computer — the break that makes RSA,
  ECDSA, and EdDSA quantum-vulnerable.

### S20 — Global Risk Institute, Quantum Threat Timeline Report 2025 (March 2026)
- Executive summary PDF:
  https://globalriskinstitute.org/mp-files/pdf-quantum-threat-timeline-report-2025-exec-sum.pdf/
  (fetched and read 2026-11-15).
- Report page: https://globalriskinstitute.org/publication/quantum-threat-timeline-report-2025b/
- Seventh edition, dated 9 March 2026, based on a survey of 26
  experts. A cryptographically relevant quantum computer (defined
  as breaking RSA-2048 within 24 hours) is "quite possible"
  (28-49%) within 10 years and "likely" (51-70%) within 15 years.
  13 of 26 experts put the 10-year probability at 50% or higher;
  18 of 26 put the 15-year probability at 50% or higher; 92% put
  the 20-year probability at 50% or higher.
- This is an expert survey, not a measurement and not a prediction.

### S21 — NSA, Commercial National Security Algorithm Suite 2.0 (CNSA 2.0)
- Advisory: "Announcing the Commercial National Security Algorithm
  Suite 2.0", CSA U/OO/194427-22 | PP-22-1338, September 2022.
- FAQ: "CNSA Suite 2.0 and Quantum Computing FAQ",
  U/OO/194427-22 | PP-24-4014, December 2024, version 2.1:
  https://www.nsa.gov/Portals/75/documents/CNSA%20Suite%20documents%2009-2026/CSI_CNSA_2.0_FAQ_.pdf
  (text verified via the NSA page crawl 2026-11-15; the direct PDF
  download was not retrievable from this environment).
- Required suite: ML-KEM-1024 (Level V) for key establishment,
  ML-DSA-87 (Level V) for digital signatures, AES-256, SHA-384/512,
  LMS/XMSS for firmware and software signing.
- FAQ: "NSA does not know when there will be a CRQC. Expert
  assessments disagree significantly about timing."
- **UNVERIFIED against the primary:** the per-technology-class
  deadline ladder (new acquisitions from 1 January 2027;
  software/firmware signing exclusively CNSA 2.0 by 2030;
  web/cloud/OS by 2033; full transition by 2035). Secondary
  summaries agree on these dates, but the NSA PDF was not
  re-checked in this pack; the 2035 outer date is independently
  confirmed by IR 8547 (S6) via NSM-10.

### S22 — Joint CISA/NSA/NIST quantum-readiness factsheet (21 August 2023)
- Names "harvest now, decrypt later operations" explicitly.
- **UNVERIFIED against the primary:** the factsheet itself was not
  fetched in this pack; cited from secondary summaries only.

### S23 — CA/Browser Forum, ML-DSA in publicly trusted TLS certificates
- **UNVERIFIED:** as of October 2026 the CA/Browser Forum had
  reportedly not adopted a ballot allowing ML-DSA in publicly
  trusted TLS certificates. Reported by secondary sources only;
  not checked against CA/B Forum minutes. The pack does not rely
  on this claim.
