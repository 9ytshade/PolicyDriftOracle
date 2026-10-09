# Downstream Integration Guide

`PolicyDriftOracle` provides a standardized on-chain gate for decentralized protocols whose execution depends on external legal, regulatory, or operational terms.

---

## 1. Interface Specification

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IPolicyDriftOracle {
    struct Policy {
        uint256 id;
        address owner;
        string title;
        string url;
        string category;
        string baseline_hash;
        string baseline_summary;
        string critical_clauses;
        uint256 check_interval_sec;
        uint256 spec_version;
        string status; // "STABLE", "DRIFT_DETECTED", "UNAVAILABLE", "ARCHIVED"
        uint256 last_audit_id;
        uint256 last_audit_timestamp;
        uint256 total_audits;
        uint256 total_drift_events;
        bool active;
        uint256 created_at;
    }

    struct AuditReceipt {
        uint256 id;
        uint256 policy_id;
        uint256 spec_version;
        uint256 audited_at;
        string verdict; // "STABLE", "MINOR_COMPATIBLE", "MATERIAL_DRIFT", "ERROR"
        uint256 severity_score; // 0 to 100
        string affected_clauses;
        string reasoning;
        bool is_material_drift;
        uint256 evidence_status_code;
    }

    function is_allowed(uint256 policy_id, uint256 max_severity) external view returns (bool);
    function is_fresh(uint256 policy_id, uint256 max_age_sec) external view returns (bool);
    function latest_verdict(uint256 policy_id) external view returns (string memory, uint256, bool);
    function get_policy(uint256 policy_id) external view returns (Policy memory);
    function get_audit(uint256 audit_id) external view returns (AuditReceipt memory);
}
```

---

## 2. Example: Autonomous Escrow Vault (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IPolicyDriftOracle.sol";

contract AutonomousEscrowVault {
    IPolicyDriftOracle public immutable oracle;
    uint256 public immutable policyId;
    address public immutable provider;
    uint256 public immutable maxAllowedSeverity;
    uint256 public immutable maxAuditAgeSeconds;

    event PaymentReleased(address indexed recipient, uint256 amount);
    event PaymentBlocked(string reason);

    constructor(
        address _oracle,
        uint256 _policyId,
        address _provider,
        uint256 _maxAllowedSeverity,
        uint256 _maxAuditAge
    ) {
        oracle = IPolicyDriftOracle(_oracle);
        policyId = _policyId;
        provider = _provider;
        maxAllowedSeverity = _maxAllowedSeverity;
        maxAuditAgeSeconds = _maxAuditAge;
    }

    /// @notice Releases milestone funds only if the SLA/ToS has not materially drifted
    function releaseMilestonePayment() external {
        // 1. Verify freshness
        require(
            oracle.is_fresh(policyId, maxAuditAgeSeconds),
            "Escrow: Audit is stale. Trigger oracle check_drift first."
        );

        // 2. Verify security gate (fail-closed if drift or spec changed)
        require(
            oracle.is_allowed(policyId, maxAllowedSeverity),
            "Escrow: Policy drift detected or specification mismatch. Payment blocked."
        );

        // 3. Execute release
        uint256 balance = address(this).balance;
        payable(provider).transfer(balance);
        emit PaymentReleased(provider, balance);
    }
}
```

---

## 3. Example: GenLayer Python Consumer

```python
import genlayer.gl as gl

class EnterpriseComplianceGate(gl.Contract):
    def __init__(self, oracle_address: str, policy_id: int):
        self.oracle_address = oracle_address
        self.policy_id = policy_id

    @gl.public.write
    def execute_governed_action(self, payload: str) -> bool:
        # Call the canonical oracle gate
        is_compliant = gl.get_contract(self.oracle_address).is_allowed(self.policy_id, 25)
        if not is_compliant:
            raise Exception("Compliance action rejected: policy baseline has drifted")
        
        return True
```
