# Consensus Architecture & Equivalence Principle Specification

## 1. Overview & Consensus Flaw Resolution (v1.0.1)

In v1.0.0, the contract allowed validator severity scores to differ by up to 1:
```python
# VULNERABLE v1.0.0 LOGIC:
if abs(int(leader_val["severity"]) - int(validator_val["severity"])) > 1:
    return False
```
Because `is_allowed(policy_id, max_acceptable_severity)` directly compares `audit.severity_score <= max_acceptable_severity`, this tolerance enabled a critical consensus boundary defect:
> **Steward Rejection Finding:**
> *"The validator allows severity scores to differ by one, but the stored severity directly controls the is_allowed authorization threshold. This lets two validator-compatible scores produce opposite allow/deny results. Please require exact agreement on severity, or validate a canonical severity bucket whose accepted values cannot cross any downstream decision threshold, before resubmitting."*

### The v1.0.1 Dual-Defense Architectural Fix
`PolicyDriftOracle` v1.0.1 implements **both** remediations in lockstep:
1. **Exact Severity Agreement**: In `validate()`, severity scores must agree with zero tolerance (`int(leader_val["severity"]) == int(validator_val["severity"])`).
2. **Canonical Discrete Severity Buckets**: All audit verdicts map strictly to invariant discrete canonical severity levels:
   - `STABLE` (`0`): Zero drift, baseline preserved intact.
   - `MINOR_COMPATIBLE` (`2`): Formatting, clarification, non-breaking administrative updates.
   - `MATERIAL_BREAKING` (`7`): Core obligations weakened, rate limits slashed, refund credits omitted.
   - `UNAVAILABLE` (`10`): Document gone (404/410), server outage (5xx/429), or empty content.
3. **Threshold-Crossing Invariant**: Because accepted values are strictly discrete canonical buckets `{0, 2, 7, 10}` and exact consensus is required, no validator-compatible proposal can ever cross any downstream decision threshold (`is_allowed`).

```
Canonical Severity Ladder:
[0] STABLE              --> Allowed by thresholds >= 0
      --- Threshold Boundary Gap ---
[2] MINOR_COMPATIBLE    --> Allowed by thresholds >= 2, Blocked by threshold 0 or 1
      --- Wide Threshold Boundary Gap ---
[7] MATERIAL_BREAKING   --> Blocked by normal operational gates (<= 3) AND status = DRIFTED
[10] UNAVAILABLE        --> Blocked by status = UNAVAILABLE
```

---

## 2. Non-Deterministic Boundary (`run_nondet_unsafe`)

Non-deterministic operations are strictly quarantined inside `check_drift`:

1. **Web Document Retrieval**:
   - Executed via `gl.nondet.web.get(target_url)`.
   - Only secure public HTTPS URLs permitted (strict SSRF filter blocking loopback, RFC1918, and link-local ranges).
   - Validators independently fetch the live policy content and capture the HTTP status code.

2. **Comparative LLM Prompt Evaluation**:
   - Impartial validator prompt comparing live text against `baseline_summary` and `critical_clauses`.
   - Explicit prompt instructions requiring canonical discrete severity ratings (`0`, `2`, `7`, `10`).

3. **Equivalence Principle Validation (`validate`)**:
   ```python
   def validate(leader_result: gl.vm.Result) -> bool:
       if not isinstance(leader_result, gl.vm.Return):
           return False
       try:
           leader_val = self._normalize_audit_payload(leader_result.calldata)
           validator_val = evaluate()

           # 1. Exact verdict agreement
           if leader_val["verdict"] != validator_val["verdict"]:
               return False

           # 2. Exact breaking status agreement
           leader_is_breaking = leader_val["verdict"] == self.VERDICT_MATERIAL_BREAKING
           validator_is_breaking = validator_val["verdict"] == self.VERDICT_MATERIAL_BREAKING
           if leader_is_breaking != validator_is_breaking:
               return False

           # 3. Exact severity agreement (zero tolerance - eliminates threshold drift)
           if int(leader_val["severity"]) != int(validator_val["severity"]):
               return False

           # 4. Strict discrete bucket membership
           expected_severity = {
               self.VERDICT_STABLE: self.SEVERITY_STABLE,               # 0
               self.VERDICT_MINOR_COMPATIBLE: self.SEVERITY_MINOR_COMPATIBLE, # 2
               self.VERDICT_MATERIAL_BREAKING: self.SEVERITY_MATERIAL_BREAKING, # 7
               self.VERDICT_UNAVAILABLE: self.SEVERITY_UNAVAILABLE,       # 10
           }.get(leader_val["verdict"])
           if int(leader_val["severity"]) != expected_severity:
               return False

           return True
       except Exception:
           return False
   ```

4. **Auditable Public View (`validate_equivalence`)**:
   The contract exposes `@gl.public.view def validate_equivalence(leader_payload_json, validator_payload_json) -> bool`, allowing off-chain clients, stewards, and unit tests to deterministically verify whether any two payloads satisfy consensus equivalence rules.

---

## 3. Deterministic State Execution

Once consensus completes, state transitions execute deterministically:

1. **Status Transitions**:
   - `MATERIAL_BREAKING` -> `policy.status = "DRIFTED"`
   - `UNAVAILABLE` -> `policy.status = "UNAVAILABLE"`
   - `STABLE` or `MINOR_COMPATIBLE` -> `policy.status = "STABLE"`

2. **Downstream Security Gate (`is_allowed`)**:
   ```python
   @gl.public.view
   def is_allowed(self, policy_id: u256, max_acceptable_severity: u32) -> bool:
       p = self._require_policy(policy_id)
       if not p.active or p.last_audit_id == 0:
           return False
       if p.status in (self.STATUS_DRIFTED, self.STATUS_UNAVAILABLE, self.STATUS_ARCHIVED):
           return False
       if p.last_audit_id not in self.audits:
           return False
       a = self.audits[p.last_audit_id]
       if a.spec_version != p.spec_version:
           return False
       return a.severity_score <= max_acceptable_severity
   ```

3. **Spec Version Invalidation**:
   Updating baseline via `update_baseline` increments `spec_version`, immediately invalidating older audit receipts for downstream authorization.
