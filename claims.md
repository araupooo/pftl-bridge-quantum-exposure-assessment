# Claim-to-evidence index

Every testable claim in this pack, mapped to the script and output
that evidence it. Claims that rest on primary sources rather than on
the harness cite the source instead; claims that are assumptions
cite the assumptions register (findings.md, section 2).

## Harness-measured claims

| # | Claim | Script | Output | Result |
|---|---|---|---|---|
| C1 | Reordered validations (2 orders x 2 runs) yield identical final-state traces | `scripts/run_all.py` (t01_reorder), `scripts/bridge_model.py` | `outputs/t01_reorder.log`, `outputs/run-summary.json` | PASS — all 4 runs, digest `ea00ee470531c76d6e30f57eefcd97ee412cd1cfffef28d69c694962d5fee257` |
| C2 | A duplicated validation is rejected as an idempotent no-op; the mint is applied once | `scripts/run_all.py` (t02_duplicate) | `outputs/t02_duplicate.log` | PASS — balance 100,000,000, not 200,000,000; one mint in trace |
| C3 | A double-spend attempt (same source lock minted twice) is rejected; the second mint moves no value | `scripts/run_all.py` (t03_double_spend) | `outputs/t03_double_spend.log` | PASS — `ERR_ALREADY_MINTED`; second destination balance 0 |
| C4 | A tampered validation is rejected: altered amount | `scripts/run_all.py` (t04_tamper) | `outputs/t04_tamper.log` | PASS — `ERR_BAD_SIGNATURE` |
| C5 | A tampered validation is rejected: wrong domain separator | `scripts/run_all.py` (t04_tamper) | `outputs/t04_tamper.log` | PASS — `ERR_WRONG_DOMAIN` |
| C6 | A tampered validation is rejected: forged signature | `scripts/run_all.py` (t04_tamper) | `outputs/t04_tamper.log` | PASS — `ERR_BAD_SIGNATURE` |
| C7 | The 24-of-35 quorum is honored: 23 attestations insufficient, 24 sufficient | `scripts/run_all.py` (t05_quorum) | `outputs/t05_quorum.log` | PASS — 23 `ERR_NO_QUORUM`; 24 OK; 35 OK |
| C8 | A duplicated witness does not count twice toward quorum | `scripts/run_all.py` (t05_quorum) | `outputs/t05_quorum.log` | PASS — 24 attestations from 23 distinct witnesses, `ERR_NO_QUORUM` |
| C9 | An empty attestation set is rejected | `scripts/run_all.py` (t06_negative) | `outputs/t06_negative.log` | PASS — `ERR_EMPTY` |
| C10 | A stale-nonce replay (same lock and nonce, new amount/destination) is rejected | `scripts/run_all.py` (t06_negative) | `outputs/t06_negative.log` | PASS — `ERR_ALREADY_MINTED`; nothing minted |
| C11 | An exact replay of an executed claim is rejected | `scripts/run_all.py` (t06_negative) | `outputs/t06_negative.log` | PASS — `ERR_ALREADY_MINTED` |
| C12 | A cross-chain replay (attestation set from another bridge/domain) is rejected | `scripts/run_all.py` (t06_negative) | `outputs/t06_negative.log` | PASS — `ERR_WRONG_DOMAIN` |
| C13 | A lone attestation cannot execute a claim | `scripts/run_all.py` (t06_negative) | `outputs/t06_negative.log` | PASS — `ERR_NO_QUORUM` |
| C14 | Quorum signature arithmetic: 24 x 3,309 = 79,416 bytes; 24 x 1,952 = 46,848 bytes | `scripts/run_all.py` (t07_sizes) | `outputs/t07_sizes.log` | PASS — matches the whitepaper figure (S10, section 1.11) |
| C15 | SLH-DSA-256f signatures (49,856 B) are larger than ML-DSA-65 signatures (3,309 B); ML-KEM-768 ciphertext is 1,088 bytes | `scripts/run_all.py` (t07_sizes) | `outputs/t07_sizes.log` | PASS |

## Source-grounded claims (no harness test; evidence is the cited primary source)

| # | Claim | Source | Where used |
|---|---|---|---|
| C16 | ML-DSA-65: public key 1,952 B, signature 3,309 B, category 3; ML-DSA-44/87 sizes and categories as tabulated | S1 (FIPS 204, Table 2, §4) | findings.md §6; migration.md §2.1 |
| C17 | SLH-DSA: 12 parameter sets; signatures 7,856-49,856 B; 128f sets do not meet their category for message-bound signatures | S2 (FIPS 205, Table 2, §11) | migration.md §2.1 |
| C18 | ML-KEM-768 is the NIST-recommended default; sizes per Table 3 | S3 (FIPS 203, Table 3, §8) | migration.md §2.3 |
| C19 | Hybrid KEMs: multi-algorithm schemes, approved key combiners, X-Wing example | S4 (SP 800-227, §4.6) | migration.md §2.2-2.3 |
| C20 | LMS/XMSS approved for firmware/software signing, hardware-module key custody required | S5 (SP 800-208) | migration.md §2.3, §3 phase 3 |
| C21 | Quantum-vulnerable algorithms deprecated after 2030, disallowed after 2035; post-quantum signatures by 31 Dec 2031 | S6 (IR 8547, final Oct 2026) | findings.md §4; migration.md §2.4 |
| C22 | Composite ML-DSA is an expired Internet-Draft (-19, expired 23 Oct 2026), not an RFC; AND-mode verification; keys must not be reused | S7 (LAMPS draft-ietf-lamps-pq-composite-sigs-19) | migration.md §2.2 |
| C23 | Single ML-DSA in X.509 is standardised (RFC 9881, Oct 2025) | S8 (RFC 9881) | migration.md §2.2, §3 phase 3 |
| C24 | Accounts and validators sign with ML-DSA-65 from genesis; domain-separated contexts include bridge witnesses; q=24 from 35 validators | S10 (whitepaper §1.11) | architecture.md §4-5; findings.md §1, §3 |
| C25 | Bridge proofs wrap in Groth16; external-chain contracts use their own cryptography; the post-quantum claim ends there | S10 (whitepaper §1.11) | threat-model.md T7, T8; findings.md §1 |
| C26 | Supply identity s_native + s_shielded + s_external + s_in-flight = s_authorized; one category per claim per stage | S10 (whitepaper §1.3) | architecture.md §3; threat-model.md T4 |
| C27 | A666 route: 20 m 12 s mainnet round trip; 100.5 USDC -> 100 A666 -> 100 wA666; Arbitrum pfUSDC route closed to new ingress after ~6.4-day trustless confirmations | S10 (whitepaper §2.3) | architecture.md §6 |
| C28 | postfiatd amendment thresholds: 67/100 post-fix, 204/256 pre-fix, 2-week hold; upstream XRPL: single 80/100, no fix amendment | S12, S13 (source code) | architecture.md §7; threat-model.md T9 |
| C29 | Inherited bridge code: quorum weight check, duplicate-attestation replacement, claim-ID erasure on finalisation, wrong-chain and sending-account rejection | S12 (XChainBridge.cpp) | findings.md §5; threat-model.md T3-T5 |
| C30 | Witness keys are secp256k1 or ed25519; authorisation via door-account SignerListSet quorum | S14 (XRPL docs) | architecture.md §4-5; threat-model.md T1, T2 |
| C31 | Wormhole: 13-of-19 guardian VAA quorum; replay protection via (emitter_chain, emitter_address, sequence) + processed check | S15 (Wormhole docs) | threat-model.md T2, T3 |
| C32 | Mosca: "a 1/2 chance of breaking RSA-2048 by 2031"; Mosca's inequality X+Y>Z | S18 (ePrint 2015/1075) | findings.md §4; threat-model.md §2 |
| C33 | GRI 2025 survey (26 experts, Mar 2026): CRQC 28-49% within 10 years, 51-70% within 15 years | S20 (GRI executive summary PDF) | findings.md §4; threat-model.md §2 |
| C34 | CNSA 2.0 requires ML-KEM-1024 and ML-DSA-87; LMS/XMSS for firmware/software signing | S21 (NSA CNSA 2.0 FAQ) | migration.md §2.1, §2.3 |

## Assumption claims (not asserted as fact)

| # | Claim | Status | Reference |
|---|---|---|---|
| A1 | An ERC-20 representation on Base exists or is planned before mainnet | UNVERIFIED — no primary source found | findings.md §2 |
| A2 | The destination chain is Base | UNVERIFIED | findings.md §2 |
| A3 | The bridge deployment follows the inherited XChainBridge design | UNVERIFIED — mechanism confirmed, application assumed | findings.md §2 |
| A4 | The 24-of-35 quorum applies to bridge witnesses | ASSUMPTION | findings.md §2 |
| A5 | The validator set is 35 | CONFLICT — homepage reports 53 | findings.md §2 |
| A6 | `fixAmendmentMajorityCalc` is enabled on the live network | UNVERIFIED | findings.md §2 |
| A7 | The "How the bridge stays post-quantum" page exists | UNVERIFIED — link target not resolved | findings.md §2 |

## Claims explicitly NOT made

- The harness does not claim to test real cryptography (see A8).
- The pack does not claim the assessed bridge exists, is deployed,
  or has any published contract, witness set, or operator list.
- The pack does not claim the residual double-spend paths in
  threat-model.md (T4) are closed; they are listed as open.
- The pack does not claim Groth16 bridge proofs or destination-chain
  cryptography are migrated; both are open dependencies
  (migration.md, section 7).
