# Studionet Canonical Deployment Record

## 1. Network & Deployment Summary

| Parameter | Value |
| :--- | :--- |
| **Network** | GenLayer Studionet |
| **Chain ID** | `61999` |
| **Canonical Contract Address** | `0x123D9c10743eA27da684e3606C5a232848C948D5` |
| **Deployer Address** | `0xb704b624ae5f776b3a3fa7496adcda4db4dcab56` (`9ytshade_Deployer`) |
| **Deployment Transaction** | `0xe8346c0749da0200398542b7e3aaeb08a2e8f4fb4a95993c070f584bfb03beab` |
| **Consensus Result** | `MAJORITY_AGREE` |
| **Status** | `ACCEPTED` / `FINALIZED` |
| **Explorer URL** | [GenLayer Explorer](https://explorer-studio.genlayer.com/address/0x123D9c10743eA27da684e3606C5a232848C948D5) |
| **Source Commit SHA** | `d8da93e857efc151c28def9a72a1abf4df180d9e` |
| **Contract Blob Hash** | `958efc28f75c7333b2140483ee1bb704e0e34085` |

---

## 2. On-Chain Transaction & Consensus Log

### Deployment Transaction
- **Tx Hash**: `0xe8346c0749da0200398542b7e3aaeb08a2e8f4fb4a95993c070f584bfb03beab`
- **Sender**: `0xb704b624ae5f776b3a3fa7496adcda4db4dcab56`
- **Result**: Contract initialized with zero policies and zero audits.

### Transaction 1: Policy Registration
- **Method**: `register_policy`
- **Tx Hash**: `0x7160fdc645dac16fcc8fb9614e42c80ca04c7c8a6c46ed2d701a9ef144c8a134`
- **Status**: `ACCEPTED` (`MAJORITY_AGREE`)
- **Parameters**:
  - `title`: `"Acme Cloud RPC Service Level Agreement"`
  - `url`: `"https://raw.githubusercontent.com/9ytshade/chainsettle/main/README.md"`
  - `category`: `"Infrastructure"`
  - `baseline_hash`: `"0x123456789abcdef"`
  - `baseline_summary`: `"Autonomous milestone release and dispute resolution."`
  - `critical_clauses`: `"Clause 1: Autonomous milestone release upon 100 percent criteria pass."`
  - `check_interval_sec`: `120`

### Transaction 2: Consensus Semantic Audit
- **Method**: `check_drift`
- **Tx Hash**: `0x5f90b039f3ea8523aac922ec87fa312e7c21564b3ed9bcfcc92e3e5c83272759`
- **Status**: `FINALIZED` (`MAJORITY_AGREE` after 3 validator rounds)
- **Consensus Verdict**: `STABLE`
- **Severity Score**: `0`
- **Reasoning Recorded On-Chain**:
  > "The live policy content from the ChainSettle README preserves the critical obligation intact. The baseline commitment of 'Autonomous smart contract milestone and dispute resolution platform' is fully reflected. Specifically, Clause 1 is clearly upheld: the live document states 'GenLayer validators perform an autonomous initial AI audit: if 100% of criteria pass, escrow is autonomously released to the builder without client delay' and the verification matrix Case B confirms live execution of 'Autonomous AI Audit & Auto-Payout' at 100% consensus. The dispute resolution mechanism (Adversarial Dispute Court with continuous Basis Points) is also present and operational. No material semantic drift detected; only formatting, documentation expansion, and live deployment metadata have been added."

### Transaction 3: Baseline Governance Update
- **Method**: `update_baseline`
- **Tx Hash**: `0xe811caf980c13489de09ad816bb6dc09e8f6e580483c354ffc8c2b0dc566bc12`
- **Status**: `ACCEPTED` (`MAJORITY_AGREE`)
- **Outcome**: `spec_version` incremented from `1` to `2`.

---

## 3. Live Verification Commands

```powershell
# Read policy record #1
genlayer call 0x123D9c10743eA27da684e3606C5a232848C948D5 get_policy --args 1

# Read consensus audit receipt #1
genlayer call 0x123D9c10743eA27da684e3606C5a232848C948D5 get_audit --args 1

# Read security gate (returns false due to spec_version bump)
genlayer call 0x123D9c10743eA27da684e3606C5a232848C948D5 is_allowed --args 1 0
```
