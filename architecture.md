# Pinned bridge architecture

This document pins the proposed bridge architecture as far as primary
sources allow. Every element is tagged **CONFIRMED** (with its source)
or **ASSUMPTION** (planned, unverified, or inferred — see the
assumptions register in findings.md). Nothing tagged ASSUMPTION is
presented as an implemented fact anywhere in this pack.

## 1. What the bridge is (as assessed)

A cross-chain bridge that moves value between the native asset on the
ledger and a wrapped representation on an external chain.

| Element | Status | Detail |
|---|---|---|
| Source chain | CONFIRMED | The ledger (postfiatd, an XRPL-derived codebase). Source: S12. |
| Destination chain | ASSUMPTION | Base, an EVM chain. No primary source confirms a Base deployment; the premise is assessed as stated, not as fact. See A1. |
| Destination representation | ASSUMPTION | An ERC-20 representation of the native asset. The whitepaper contains zero occurrences of "ERC-20". See A1. |
| Direction | ASSUMPTION | Native asset locked on the ledger, wrapped representation minted on the external chain; redemption burns the wrapped representation and releases the lock. This is the standard lock-and-mint pattern; no deployment document confirms it for this bridge. |

## 2. Custody

| Element | Status | Detail |
|---|---|---|
| Source-chain lock | ASSUMPTION (mechanism CONFIRMED) | The lock is held by a door account / lock contract on the source chain. The mechanism is the inherited XRPL XChainBridge door-account design (S14): a bridge has a locking-chain door and an issuing-chain door; the issuing-chain door for an XRP-XRP bridge must be the genesis account. Whether this bridge uses door accounts, a lock contract, or another custodian is not documented. |
| Custody perimeter | CONFIRMED (concept) | The whitepaper defines a custody perimeter as "where the backing sits and who can move it: a broker, a venue vault, a source-chain contract" (S10, section 1.1). Custodian honesty, undisclosed liabilities, and legal recovery in insolvency lie outside what any proof establishes. |
| Who operates custody | ASSUMPTION | No operator, custodian, or key-holder list is published for this bridge. |

## 3. Mint / burn authority

| Element | Status | Detail |
|---|---|---|
| Mint authority | ASSUMPTION | The destination token contract mints only on a verified quorum of witness attestations. This is the standard pattern (Wormhole VAA consumption, S15; LayerZero OFT adapter mint permission, S17) and the inherited XChainBridge claim flow (S12), but no contract for this bridge is published. |
| Burn authority | ASSUMPTION | Redemption burns the wrapped representation on the external chain and releases the source lock on presentation of a quorum attestation in the reverse direction. Same basis as above. |
| Supply accounting | CONFIRMED | s_native + s_shielded + s_external + s_in-flight = s_authorized (S10, section 1.3). "A claim occupies exactly one category at each stage of its life. Export moves it from native through in-flight to external." A correct bridge must preserve this identity at every step; a double-mint breaks it by counting one claim twice. |
| Cash-leg identity (reference) | CONFIRMED | W_cash = S_cash + D + B - R (S10, section 1.3). The same conservation discipline applies to the bridge: locked value, outstanding wrapped supply, in-flight claims, and released value must reconcile exactly. |

## 4. Signer quorum

| Element | Status | Detail |
|---|---|---|
| Validator quorum stated in the whitepaper | CONFIRMED | "A quorum of q=24 from 35 validators carries 24x3,309=79,416 signature bytes plus identifiers" (S10, section 1.11). ML-DSA-65 signatures are 3,309 bytes (S1). The harness verifies 24 x 3,309 = 79,416 (t07_sizes). |
| Bridge-witness quorum | ASSUMPTION | No deployment document states how many bridge witnesses exist, what quorum they use, or who operates them (S14, UNVERIFIED). This pack models the bridge-witness quorum as the whitepaper's 24-of-35 figure, because it is the only quorum figure the project itself states, and labels it as an assumption everywhere it is used. |
| Inherited quorum mechanism | CONFIRMED | The inherited XRPL design authorises a bridge through the door account's `SignerListSet` quorum; funds release when "enough signatures are submitted by the witness servers to reach quorum" (S14). In code, `claimHelper` returns `tecXCHAIN_CLAIM_NO_QUORUM` unless accumulated signer weight is at least the quorum (S12). The tutorial example uses `SignerQuorum: 2` with two witnesses — an example, not this bridge's configuration. |
| Validator count | CONFLICT, UNRESOLVED | The whitepaper's quorum arithmetic assumes 35 validators; the homepage snapshot (21 September 2026) reports 53 validators (S11). The two figures are not reconciled in any source checked. If the witness set is 53 rather than 35, a 24-of-35 quorum is 68.6% of the set, while 24-of-53 is 45.3% — a materially weaker threshold. The harness uses 24-of-35 as stated in the whitepaper and flags the discrepancy. |

## 5. Attestations

| Element | Status | Detail |
|---|---|---|
| Witness attestation | CONFIRMED (mechanism) | A witness server "listens to the door accounts on both sides of a bridge and signs attestations that confirm a transaction occurred" (S14). Attestation objects carry the attestation signer account, witness public key, and witness signature (S12, `XChainAttestations.h`). |
| Witness signing keys | CONFIRMED (inherited) | secp256k1 or ed25519 (`SigningKeyType` config, S14). Both are classical and quantum-vulnerable: Shor's algorithm breaks ECDSA and EdDSA (S19). |
| Domain separation | CONFIRMED (design intent) | "domain-separated contexts for transactions, block certificates, bridge witnesses, and admission receipts" (S10, section 1.11). The code enforces chain separation: a wrong destination chain is rejected with `tecXCHAIN_WRONG_CHAIN`, a sending-account mismatch with `tecXCHAIN_SENDING_ACCOUNT_MISMATCH` (S12). |
| Claim identity and replay | CONFIRMED (mechanism) | Each bridge carries a sequential claim-ID counter, incremented per commit (`XChainCommit`, S12). `finalizeClaimHelper` erases the claim-ID ledger entry after a successful claim; a second claim with the same ID finds no entry and fails (`tecXCHAIN_NO_CLAIM_ID`). Duplicate attestations from the same signer replace rather than double-count (`onNewAttestations`, S12). |
| Attestation cryptography | CONFIRMED (scope limit) | Account and validator authorisation is ML-DSA-65 from genesis. But: "SP1 reserve and bridge proofs wrap in Groth16; external-chain contracts use their own cryptography" (S10, section 1.11). Bridge proofs are therefore classical (pairing-based), and external-chain contracts are classical, even though ledger accounts sign with ML-DSA. |

## 6. Wrapped representations

| Element | Status | Detail |
|---|---|---|
| Representation categories | CONFIRMED | The supply identity partitions authorised supply into native, shielded, external, and in-flight (S10, section 1.3). A wrapped representation on an external chain is an `s_external` claim; while a transfer is in progress it is `s_in-flight`. |
| Demonstrated wrapped routes | CONFIRMED | A666 on Ethereum mainnet: "100.5 USDC -> 100 A666 -> 100 wA666, canonical and wrapped supply each rising by exactly 100,000,000 atoms", "20 m 12 s mainnet round trip" (S10, section 2.3). The Arbitrum pfUSDC route "is closed to new ingress after roughly 6.4-day trustless confirmations" (S10, section 2.3). These are demonstrated routes for other assets, not for the assessed bridge. |
| This bridge's wrapped representation | ASSUMPTION | No contract address, token standard confirmation, supply, or audit is published for a wrapped representation of the native asset on Base. |

## 7. Amendment and governance surface

| Element | Status | Detail |
|---|---|---|
| Amendment threshold in code | CONFIRMED | postfiatd: 67/100 after `fixAmendmentMajorityCalc` activates, 204/256 (79.6875%) before it; majority hold time 2 weeks (S12). Upstream XRPL: a single 80/100 threshold, no fix amendment at all (S13). |
| Threshold live on the network | UNVERIFIED | Whether `fixAmendmentMajorityCalc` is enabled on the live network could not be determined from code; the amendment name was not located in `Feature.h`/`Feature.cpp` (S12). The effective live threshold is therefore 79.6875% or 67%, unknown. Any bridge change that depends on an amendment inherits this uncertainty. |

## 8. What the pinned architecture deliberately excludes

- No bridge contract address, no witness list, no operator identities:
  none are published, and none are invented here.
- No live-chain state: this pack contains no mainnet or testnet
  queries, no ledger data, and no claim about current on-chain
  balances.
- No assertion that the assessed bridge exists or is deployed. The
  architecture above is the proposed design as far as primary
  sources pin it, plus explicitly marked assumptions where the
  sources stop.
