# Consensus Architecture & Non-Deterministic Boundaries

## 1. Overview

`PolicyDriftOracle` uses GenLayer's hybrid consensus architecture to bridge off-chain operational reality (e.g. Terms of Service, SLAs, privacy commitments, insurance terms) with on-chain governance and smart contracts.

Because external web documents and natural-language specifications are inherently non-deterministic, the contract enforces a strict demarcation between non-deterministic semantic observation and deterministic state execution.

```
       +-----------------------------------------------------------+
       |                  GenLayer Studionet                       |
       |                                                           |
       |   Leader Node                      Validator Nodes        |
       |   +-----------------------+        +------------------+   |
       |   | 1. HTTP GET (url)     |        | 1. Independent   |   |
       |   | 2. LLM Equivalence    |        |    Verification  |   |
       |   |    Evaluation         |        | 2. Equivalence   |   |
       |   | 3. Propose Verdict    |        |    Agreement     |   |
       |   +-----------+-----------+        +--------+---------+   |
       |               |                             |             |
       |               +--------------+--------------+             |
       |                              |                            |
       |                    Consensus Agreement                    |
       |                      (MAJORITY_AGREE)                     |
       |                              |                            |
       |                              v                            |
       |                  +-----------------------+                |
       |                  |  Deterministic State  |                |
       |                  |  - Spec Version Match |                |
       |                  |  - Audit Receipt      |                |
       |                  |  - Fail-Closed Gate   |                |
       |                  +-----------------------+                |
       +-----------------------------------------------------------+
```

---

## 2. Non-Deterministic Boundary

Non-deterministic operations are strictly quarantined within the leader-validator consensus execution of `check_drift`:

1. **Web Document Retrieval**:
   - Executed via `gl.get_webpage(url, mode="text")`.
   - Only standard public HTTPS endpoints are allowed.
   - Validators fetch the resource independently to verify data authenticity and HTTP status code.

2. **Comparative Semantic Analysis**:
   - Executed using `gl.exec_prompt(...)`.
   - The LLM compares the live fetched document against the on-chain recorded `critical_clauses` and `baseline_summary`.
   - Output is constrained to a strict JSON schema:
     ```json
     {
       "verdict": "STABLE | MINOR_COMPATIBLE | MATERIAL_DRIFT | DRIFT_DETECTED | ERROR",
       "severity_score": "<integer 0-100>",
       "affected_clauses": "<list of strings>",
       "reasoning": "<string justification>"
     }
     ```

3. **Equivalence Principle**:
   - Validators execute the prompt under the equivalence principle.
   - Validators agree on the categorized verdict (`verdict`) and numerical severity band (`severity_score`), ensuring that minor syntactic variances in the LLM's free-form reasoning do not disrupt consensus.

---

## 3. Deterministic Boundary

Once consensus resolves the non-deterministic observation, all downstream state logic is 100% deterministic and provable:

1. **Policy Status Transitions**:
   - If `verdict == "MATERIAL_DRIFT"` or `severity_score >= 50`, `policy.status` deterministically transitions to `"DRIFT_DETECTED"`.
   - If `verdict == "STABLE"` or `severity_score < 25`, `policy.status` deterministically remains/transitions to `"STABLE"`.
   - If HTTP status != 200, `policy.status` deterministically becomes `"UNAVAILABLE"`.

2. **Spec Version Invalidation**:
   - Each policy maintains a monotonically increasing `spec_version`.
   - When `update_baseline` is called, `spec_version` increments.
   - The security gate `is_allowed(policy_id, max_severity)` deterministically verifies:
     ```python
     if audit.spec_version != policy.spec_version:
         return False  # Fail-closed: audit evaluated an obsolete specification
     ```

3. **Cooldown & Rate Limiting**:
   - Deterministic verification of `current_timestamp >= policy.last_audit_timestamp + policy.check_interval_sec`.
   - Prevents spamming validator consensus resources.

4. **Bounding & Sanitation**:
   - All string inputs (URLs, titles, critical clauses) are strictly length-bounded.
   - All state collections (`policies`, `audits`) use sequential integer indexing.

---

## 4. Fail-Closed Guarantees

In autonomous systems, a false negative (failing to flag a broken SLA or leaked terms) can lead to catastrophic unauthorized token releases. `PolicyDriftOracle` enforces:

- **Unreachable Endpoints**: Default to severity 100 (`DRIFT_DETECTED`).
- **Parsing Failures**: Default to severity 100 (`DRIFT_DETECTED`).
- **Outdated Audits**: Downstream calls to `is_allowed()` return `False`.
- **Archived Policies**: Inactive policies reject all new audits and fail all authorization checks.
