# Studionet Canonical Deployment Record

## 1. Network & Deployment Summary

| Parameter | Value |
| :--- | :--- |
| **Network** | GenLayer Studionet |
| **Chain ID** | `61999` |
| **Canonical Contract Address** | `0x8C2C70F47147274F1694A6E8Ad9066121B082c45` |
| **Deployer Address** | `0xb704b624ae5f776b3a3fa7496adcda4db4dcab56` (`9ytshade_Deployer`) |
| **Deployment Transaction** | `0xa00b36f50192e2878fce9cf9b34d5b52ee84f3f6f91fc90105db92b0b819e6fa` |
| **Consensus Result** | `MAJORITY_AGREE` (5/5 validators unanimous) |
| **Status** | `ACCEPTED` / `FINALIZED` |
| **Explorer URL** | [GenLayer Explorer](https://explorer-studio.genlayer.com/address/0x8C2C70F47147274F1694A6E8Ad9066121B082c45) |
| **Contract Version** | `1.0.1` (Equivalence Principle Exact Severity & Canonical Bucket Fix) |

---

## 2. On-Chain Transaction & Consensus Log

### Deployment Transaction
- **Tx Hash**: `0xa00b36f50192e2878fce9cf9b34d5b52ee84f3f6f91fc90105db92b0b819e6fa`
- **Sender**: `0xb704b624ae5f776b3a3fa7496adcda4db4dcab56`
- **Result**: `MAJORITY_AGREE` (Unanimous 5 validators agree).
- **Outcome**: Contract deployed with Equivalence Principle exact severity binding and discrete canonical buckets (`0`, `2`, `7`, `10`).

### Transaction 1: Policy Registration
- **Method**: `register_policy`
- **Tx Hash**: `0x84ffb14eb2d2be0fdd6ea1377f17c739f7ae7a075fee54b7d208fdb9ee939c55`
- **Status**: `FINALIZED` (`MAJORITY_AGREE`)
- **Parameters**:
  - `title`: `"Acme Cloud RPC Service Level Agreement"`
  - `url`: `"https://raw.githubusercontent.com/9ytshade/PolicyDriftOracle/master/fixtures/sample_policy.md"`
  - `category`: `"Infrastructure"`
  - `baseline_hash`: `"0x8f3c7e44a19b33e"`
  - `baseline_summary`: `"99.99% monthly uptime guarantee, maximum 50ms latency, 100k requests/minute tier limit, 30 days notice for material rate changes."`
  - `critical_clauses`: `"Clause 4.1: Minimum 99.99% availability per month. Clause 5.2: Rate limits not reduced below 100k req/min without 30-day notice. Clause 8.1: Full refund credits for verified qualifying downtime."`
  - `check_interval_sec`: `60`
- **Outcome**: Policy #1 registered on-chain, status `STABLE`, spec_version `1`.

### Transaction 2: Live Multi-Validator Consensus Semantic Audit
- **Method**: `check_drift`
- **Tx Hash**: `0xb76668af4a7654112a830413d86e29d1f64444ad7bc8989a6844461e54117af8`
- **Status**: `ACCEPTED` (`MAJORITY_AGREE`)
- **Consensus Verdict**: `MATERIAL_BREAKING`
- **Severity Score**: `7` (Exact Canonical Discrete Bucket)
- **Is Material Drift**: `true`
- **Affected Clauses**:
  `["Clause 5.2: Rate limits not reduced below 100k req/min without 30-day notice", "Clause 8.1: Full refund credits for verified qualifying downtime", "Baseline latency commitment: maximum 50ms latency", "Baseline notice obligation: 30 days notice for material rate changes"]`
- **Reasoning Recorded On-Chain**:
  > "The live policy preserves the 99.99% monthly availability commitment, but it omits multiple baseline protections and critical obligations. There is no mention of the 100k requests/minute tier limit or the 30-day notice requirement for reducing rate limits or making material rate changes. The maximum 50ms latency commitment is also absent. Clause 8.1 is materially altered/omitted: instead of full refund credits for verified qualifying downtime, the live text introduces autonomous escrow release to the provider upon successful uptime verification, which does not preserve the customer refund-credit protection for downtime. These omissions and substitutions constitute material semantic drift weakening protected obligations."
- **State Transition**: Policy #1 transitioned to `DRIFTED`.
- **Consumer Security Gate**: `is_allowed(1, 0)` returns `false` (fails closed, blocking downstream smart contracts/DAOs).

---

## 3. Live Verification Commands

```powershell
# Read policy record #1
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 get_policy --args 1

# Read consensus audit receipt #1
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 get_audit --args 1

# Read latest verdict for policy #1
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 latest_verdict --args 1

# Read downstream security gate (returns false due to DRIFTED status)
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 is_allowed --args 1 0

# Verify policy count
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 get_policy_count
```
