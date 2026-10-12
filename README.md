# PolicyDriftOracle

> **Autonomous Semantic Policy & SLA Drift Oracle for GenLayer**
>
> A standalone GenLayer Intelligent Contract that continuously tracks off-chain operational documents, terms of service, SLAs, and privacy commitments, using decentralized validator consensus to detect unauthorized modifications and fail-closed against downstream protocol risks.

[![GenLayer Studionet](https://img.shields.io/badge/GenLayer-Studionet-blue)](https://explorer-studio.genlayer.com/address/0x8C2C70F47147274F1694A6E8Ad9066121B082c45)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: Direct Mode](https://img.shields.io/badge/Direct_Mode_Tests-16%2F16_PASS-brightgreen)](#)
[![Tests: Studionet](https://img.shields.io/badge/Studionet_Integration-5%2F5_PASS-brightgreen)](#)
[![Preflight Linter](https://img.shields.io/badge/Preflight-20%2F20_PASS-brightgreen)](#)

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

### Equivalence Principle & Discrete Canonical Buckets (v1.0.1 Fix)
In v1.0.1, the contract binds validator consensus to exact canonical severity buckets:
- `STABLE` (`0`): Baseline obligations intact.
- `MINOR_COMPATIBLE` (`2`): Formatting, clarification, non-breaking administrative updates.
- `MATERIAL_BREAKING` (`7`): Core obligations weakened, rate limits slashed, refund credits omitted.
- `UNAVAILABLE` (`10`): Document gone (404/410), server outage (5xx/429), or empty content.

Validators must agree with zero tolerance on severity, ensuring that accepted validator proposals cannot cross downstream decision boundaries (`is_allowed`).

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
|  [Deterministic Gate: is_allowed]                                               |
|  - Verifies policy is active                                                    |
|  - Verifies audit matches current spec_version                                  |
|  - Rejects if status == "DRIFTED" or severity > max_allowed                     |
|                                                                                 |
|  [Non-Deterministic Consensus Audit: check_drift]                              |
|  - Leader fetches live web document (HTTPS)                                     |
|  - Validators execute equivalence prompt comparing baseline against live prose  |
|  - Strict Equivalence Principle validation: exact verdict & canonical severity  |
|  - Quorum reaches MAJORITY_AGREE on structured verdict & canonical severity     |
+---------------------------------------------------------------------------------+
```

---

## 3. Canonical Studionet Deployment

- **Contract Address**: [`0x8C2C70F47147274F1694A6E8Ad9066121B082c45`](https://explorer-studio.genlayer.com/address/0x8C2C70F47147274F1694A6E8Ad9066121B082c45)
- **Deployer**: `0xb704b624ae5f776b3a3fa7496adcda4db4dcab56` (`9ytshade_Deployer`)
- **Deployment Transaction**: `0xa00b36f50192e2878fce9cf9b34d5b52ee84f3f6f91fc90105db92b0b819e6fa`
- **Network**: GenLayer Studionet (Chain ID `61999`)
- **Contract Version**: `1.0.1`

---

## 4. Repository Structure

```text
PolicyDriftOracle/
├── contracts/
│   └── policy_drift_oracle.py         # Canonical GenLayer Intelligent Contract (v1.0.1)
├── docs/
│   ├── CONSENSUS.md                   # Detailed consensus & equivalence boundaries
│   ├── SECURITY.md                    # SSRF defense, prompt injection mitigations
│   ├── INTEGRATION.md                 # Downstream Solidity & GenLayer guides
│   └── DEPLOYMENT.md                  # Studionet proof and transaction log
├── fixtures/
│   ├── sample_policy.md               # Live baseline fixture on GitHub
│   └── drifted_policy.md              # Live drifted policy fixture
├── scripts/
│   ├── preflight.py                   # AST, schema, and security linter (20 checks)
│   └── deploy_studionet.py            # Deployment automation script
├── tests/
│   ├── conftest.py                    # Direct Mode environment patch & fixtures
│   ├── direct/
│   │   └── test_policy_drift_oracle.py# 16 Direct Mode comprehensive unit tests
│   └── integration/
│       └── test_policy_drift_oracle_studionet.py # 5 live Studionet on-chain tests
├── DECISION.md                        # Design rationale & primitive selection
├── requirements.txt                   # Production dependencies
├── requirements-test.txt              # Test dependencies
├── LICENSE                            # MIT License
└── SUBMISSION.md                      # Ecosystem submission & resubmission narrative
```

---

## 5. Verification & Testing

### 1. Run Preflight Linter
```powershell
python scripts/preflight.py
# Preflight checks passed: 20/20 assertions verified.
```

### 2. Run Direct Mode Tests
```powershell
python -m pytest tests/direct/test_policy_drift_oracle.py -v
# 16 passed in 0.77s
```

### 3. Run Live Studionet Integration Tests
```powershell
python -m pytest tests/integration/test_policy_drift_oracle_studionet.py -v
# 5 passed in 42.88s
```

---

## 6. Live State Queries

You can query the deployed contract on Studionet using the GenLayer CLI:

```powershell
# Query policy record #1
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 get_policy --args 1

# Query validator consensus audit receipt #1
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 get_audit --args 1

# Query latest verdict for policy #1
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 latest_verdict --args 1

# Verify fail-closed security gate (returns false due to DRIFTED status)
genlayer call 0x8C2C70F47147274F1694A6E8Ad9066121B082c45 is_allowed --args 1 0
```
