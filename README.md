# PolicyDriftOracle

> **Autonomous Semantic Policy & SLA Drift Oracle for GenLayer**
>
> A standalone GenLayer Intelligent Contract that continuously tracks off-chain operational documents, terms of service, SLAs, and privacy commitments, using decentralized validator consensus to detect unauthorized modifications and fail-closed against downstream protocol risks.

[![GenLayer Studionet](https://img.shields.io/badge/GenLayer-Studionet-blue)](https://explorer-studio.genlayer.com/address/0x123D9c10743eA27da684e3606C5a232848C948D5)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: Direct Mode](https://img.shields.io/badge/Direct_Mode_Tests-14%2F14_PASS-brightgreen)](#)
[![Tests: Studionet](https://img.shields.io/badge/Studionet_Integration-5%2F5_PASS-brightgreen)](#)

---

## 1. The 30-Second Reviewer Summary

### The Trust Problem
Smart contracts frequently govern high-stakes capital (escrow vaults, insurance pools, bridges, DAO partnerships) conditioned on off-chain legal promises, SLAs, and technical specifications hosted on the public web. 

When service providers or counterparties quietly revise their online terms, traditional EVM contracts have no way to observe the semantic drift without trusted, centralized multisig oracles.

### Why GenLayer is Strictly Required
Traditional oracles (e.g. Chainlink) can only fetch raw JSON numbers or fixed strings. They cannot:
1. Parse legal or technical natural-language prose across arbitrary web pages.
2. Formulate subjective semantic judgments (e.g. *"Did this modification weaken the arbitration guarantee or merely update a contact email?"*).
3. Reach decentralized validator consensus on natural language equivalence without a centralized LLM operator.

`PolicyDriftOracle` uses GenLayer validators to fetch live web documents and achieve equivalence consensus on semantic drift, creating tamper-proof on-chain audit receipts.

---

## 2. Architecture & Flow

```
+---------------------------------------------------------------------------------+
|                                 CONSUMER PROTOCOL                               |
|        (Autonomous Escrow Vault / DAO Treasury / Insurance Claim Engine)        |
+---------------------------------------------------------------------------------+
                                       |
                   Calls is_allowed(policy_id, max_severity)
                                       v
+---------------------------------------------------------------------------------+
|                            PolicyDriftOracle (GenVM)                            |
|                                                                                 |
|  [Deterministic Gate]                                                           |
|  - Verifies policy is active                                                    |
|  - Verifies audit matches current spec_version                                  |
|  - Rejects if status == "DRIFT_DETECTED" or severity > max_allowed              |
|                                                                                 |
|  [Non-Deterministic Consensus Audit: check_drift]                              |
|  - Leader fetches live web document (HTTPS)                                     |
|  - Validators execute equivalence prompt comparing baseline against live prose  |
|  - Quorum reaches MAJORITY_AGREE on structured verdict & severity score         |
+---------------------------------------------------------------------------------+
```

---

## 3. Canonical Studionet Deployment

- **Contract Address**: [`0x123D9c10743eA27da684e3606C5a232848C948D5`](https://explorer-studio.genlayer.com/address/0x123D9c10743eA27da684e3606C5a232848C948D5)
- **Deployer**: `0xb704b624ae5f776b3a3fa7496adcda4db4dcab56`
- **Deployment Transaction**: `0xe8346c0749da0200398542b7e3aaeb08a2e8f4fb4a95993c070f584bfb03beab`
- **Network**: GenLayer Studionet (Chain ID `61999`)
- **Source Commit**: `d8da93e857efc151c28def9a72a1abf4df180d9e`
- **Contract Blob Hash**: `958efc28f75c7333b2140483ee1bb704e0e34085`

---

## 4. Repository Structure

```text
PolicyDriftOracle/
├── contracts/
│   └── policy_drift_oracle.py         # Canonical GenLayer Intelligent Contract
├── docs/
│   ├── CONSENSUS.md                   # Detailed consensus & equivalence boundaries
│   ├── SECURITY.md                    # SSRF defense, prompt injection mitigations
│   ├── INTEGRATION.md                 # Downstream Solidity & GenLayer guides
│   └── DEPLOYMENT.md                  # Studionet proof and transaction log
├── scripts/
│   └── preflight.py                   # AST, schema, and security linter
├── tests/
│   ├── conftest.py                    # Direct Mode environment patch & fixtures
│   ├── direct/
│   │   └── test_policy_drift_oracle.py# 14 Direct Mode comprehensive unit tests
│   └── integration/
│       └── test_policy_drift_oracle_studionet.py # 5 live Studionet on-chain tests
├── DECISION.md                        # Design rationale & primitive selection
├── requirements.txt                   # Production dependencies
├── requirements-test.txt              # Test dependencies
├── LICENSE                            # MIT License
└── SUBMISSION.md                      # Ecosystem submission form summary
```

---

## 5. Verification & Testing

### 1. Run Preflight Linter
```powershell
python scripts/preflight.py
# Preflight checks passed: 16/16 assertions verified.
```

### 2. Run Direct Mode Tests
```powershell
python -m pytest tests/direct/test_policy_drift_oracle.py -v
# 14 passed in 0.57s
```

### 3. Run Live Studionet Integration Tests
```powershell
python -m pytest tests/integration/test_policy_drift_oracle_studionet.py -v
# 5 passed in 25.97s
```

---

## 6. Live State Queries

You can query the deployed contract on Studionet using the GenLayer CLI:

```powershell
# Query policy record #1
genlayer call 0x123D9c10743eA27da684e3606C5a232848C948D5 get_policy --args 1

# Query validator consensus audit receipt #1
genlayer call 0x123D9c10743eA27da684e3606C5a232848C948D5 get_audit --args 1

# Verify fail-closed security gate
genlayer call 0x123D9c10743eA27da684e3606C5a232848C948D5 is_allowed --args 1 0
```
