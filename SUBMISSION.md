# GenLayer Intelligent Contract Resubmission: PolicyDriftOracle v1.0.1

## Basic Information

- **Contract Name**: PolicyDriftOracle
- **Builder / Submitter**: `9ytshade`
- **Deployer Address**: `0xb704b624ae5f776b3a3fa7496adcda4db4dcab56` (`9ytshade_Deployer`)
- **Category**: Decentralized Infrastructure / Oracle / Legal & SLA Governance
- **License**: MIT
- **Canonical Address**: `0x8C2C70F47147274F1694A6E8Ad9066121B082c45`
- **Network**: GenLayer Studionet (Chain ID `61999`)
- **Explorer Link**: [https://explorer-studio.genlayer.com/address/0x8C2C70F47147274F1694A6E8Ad9066121B082c45](https://explorer-studio.genlayer.com/address/0x8C2C70F47147274F1694A6E8Ad9066121B082c45)
- **Source Repository**: `https://github.com/9ytshade/PolicyDriftOracle` (Branch: `master`)

---

## 280-Character Short Pitch

> PolicyDriftOracle brings off-chain legal promises, SLAs, and ToS into smart contracts. GenLayer validators continuously fetch live web documents, evaluate semantic drift via equivalence consensus, and fail-closed against unauthorized term changes.

---

## Steward Rejection Remediation Summary

### Steward Feedback
> *"The validator allows severity scores to differ by one, but the stored severity directly controls the is_allowed authorization threshold. This lets two validator-compatible scores produce opposite allow/deny results. Please require exact agreement on severity, or validate a canonical severity bucket whose accepted values cannot cross any downstream decision threshold, before resubmitting."*

### Architectural Fix Implemented (v1.0.1)
We have implemented **both** suggested solutions in tandem:

1. **Exact Severity Consensus Agreement**:
   - In `contracts/policy_drift_oracle.py`, the previous tolerance `abs(leader_val["severity"] - validator_val["severity"]) > 1` has been completely eliminated.
   - Validators must now agree with **exact equality**:
     ```python
     if int(leader_val["severity"]) != int(validator_val["severity"]):
         return False
     ```

2. **Canonical Discrete Severity Buckets**:
   - All audit verdicts map strictly to invariant discrete canonical severity levels:
     - `STABLE` (`0`): Zero drift, baseline obligations preserved intact.
     - `MINOR_COMPATIBLE` (`2`): Clarifications or formatting without weakening protections.
     - `MATERIAL_BREAKING` (`7`): Core obligations weakened, rate limits slashed, refund liabilities compromised.
     - `UNAVAILABLE` (`10`): Document gone (404/410), server offline (5xx/429), or empty body.
   - Consensus requires that the proposed severity matches the discrete bucket for the verdict:
     ```python
     expected_severity = {
         self.VERDICT_STABLE: self.SEVERITY_STABLE,               # 0
         self.VERDICT_MINOR_COMPATIBLE: self.SEVERITY_MINOR_COMPATIBLE, # 2
         self.VERDICT_MATERIAL_BREAKING: self.SEVERITY_MATERIAL_BREAKING, # 7
         self.VERDICT_UNAVAILABLE: self.SEVERITY_UNAVAILABLE,       # 10
     }.get(leader_val["verdict"])
     if int(leader_val["severity"]) != expected_severity:
         return False
     ```

3. **Downstream Decision Threshold Invariant**:
   - Because canonical severities are discrete `{0, 2, 7, 10}` and validators must agree with exact equality, **no two validator-compatible proposals can ever cross any downstream decision threshold (`is_allowed`) or produce opposite allow/deny results**.
   - A gate requiring `max_acceptable_severity = 0` allows only `STABLE`.
   - A gate requiring `max_acceptable_severity = 2` allows `STABLE` and `MINOR_COMPATIBLE`.
   - `MATERIAL_BREAKING` (`7`) and `UNAVAILABLE` (`10`) can never satisfy any operational threshold `<= 3`, and their status immediately fails-closed (`DRIFTED` / `UNAVAILABLE`).

4. **Auditable Public View (`validate_equivalence`)**:
   - Exposes `@gl.public.view def validate_equivalence(leader_payload_json, validator_payload_json) -> bool` for external on-chain and off-chain auditability.

---

## Verified On-Chain Evidence on Studionet

- **Deployment Transaction**:
  `0xa00b36f50192e2878fce9cf9b34d5b52ee84f3f6f91fc90105db92b0b819e6fa`
  - Result: `MAJORITY_AGREE` (5/5 validators unanimous agree), `ACCEPTED`
- **Policy Registration Transaction**:
  `0x84ffb14eb2d2be0fdd6ea1377f17c739f7ae7a075fee54b7d208fdb9ee939c55`
  - Result: `MAJORITY_AGREE` (5/5 validators agree), `FINALIZED`
- **Live Multi-Validator Semantic Audit Transaction**:
  `0xb76668af4a7654112a830413d86e29d1f64444ad7bc8989a6844461e54117af8`
  - Result: `MAJORITY_AGREE`, `ACCEPTED`
  - On-Chain Consensus Verdict: `MATERIAL_BREAKING`
  - Canonical Severity Score: `7` (Exact Canonical Discrete Bucket)
  - Affected Clauses Recorded: `["Clause 5.2: Rate limits not reduced below 100k req/min without 30-day notice", "Clause 8.1: Full refund credits for verified qualifying downtime", "Baseline latency commitment: maximum 50ms latency", "Baseline notice obligation: 30 days notice for material rate changes"]`
  - Downstream Security Gate `is_allowed(1, 0)`: Returned `false` (fails closed, protecting downstream consumers).

---

## Verification Reproducibility

1. **Preflight Linter**:
   ```powershell
   python scripts/preflight.py
   # Preflight checks passed: 20/20 assertions verified.
   ```

2. **Direct Mode Unit Tests**:
   ```powershell
   python -m pytest tests/direct/test_policy_drift_oracle.py -v
   # 16 passed in 0.77s
   ```

3. **Studionet Integration Tests**:
   ```powershell
   python -m pytest tests/integration/test_policy_drift_oracle_studionet.py -v
   # 5 passed in 42.88s
   ```
