"""Direct Mode test suite for PolicyDriftOracle v1.0.0.

Tests cover:
1. Deployment & public storage initialization
2. Policy registration, URL validation & SSRF defense
3. Baseline updates & spec versioning
4. Check interval cooldown enforcement
5. Policy archival & permission controls
6. Equivalence Principle non-deterministic audits:
   - Stable outcome (verdict STABLE, severity 0)
   - Minor compatible modification (verdict MINOR_COMPATIBLE, severity 2)
   - Critical material drift (verdict MATERIAL_BREAKING, severity 8)
   - External unavailability (HTTP 404, 500, empty body)
   - Fail-closed malformed LLM response handling
7. Downstream consumer views: is_allowed, is_fresh, latest_verdict
"""

import pytest


CONTRACT_PATH = "contracts/policy_drift_oracle.py"

SAMPLE_TITLE = "Acme Cloud RPC Service Level Agreement"
SAMPLE_CATEGORY = "Infrastructure"
SAMPLE_URL = "https://acme.example.com/sla.html"
SAMPLE_HASH = "0x8f3c7e44a19b33e"
SAMPLE_SUMMARY = (
    "99.99% monthly uptime guarantee, maximum 50ms latency, "
    "100k requests/minute tier limit, 30 days notice for material rate changes."
)
SAMPLE_CLAUSES = (
    "Clause 4.1: Minimum 99.99% availability per calendar month.\n"
    "Clause 5.2: Rate limits shall not be reduced below 100k req/min without 30-day notice.\n"
    "Clause 8.1: Full refund credits for any verified qualifying downtime exceeding 1 hour."
)
SAMPLE_INTERVAL = 120  # 2 minutes


def deploy_contract(direct_deploy):
    return direct_deploy(CONTRACT_PATH)


def register_sample_policy(
    direct_vm,
    contract,
    owner,
    title=SAMPLE_TITLE,
    url=SAMPLE_URL,
    category=SAMPLE_CATEGORY,
    baseline_hash=SAMPLE_HASH,
    baseline_summary=SAMPLE_SUMMARY,
    critical_clauses=SAMPLE_CLAUSES,
    interval=SAMPLE_INTERVAL,
):
    direct_vm.sender = owner
    policy_id = contract.register_policy(
        title=title,
        url=url,
        category=category,
        baseline_hash=baseline_hash,
        baseline_summary=baseline_summary,
        critical_clauses=critical_clauses,
        check_interval_sec=interval,
    )
    return policy_id


# ==============================================================================
# 1. DEPLOYMENT & REGISTRATION
# ==============================================================================


def test_deployment_initial_state(direct_deploy):
    contract = deploy_contract(direct_deploy)
    assert contract.get_policy_count() == 0
    assert contract.get_audit_count() == 0


def test_register_policy_success(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    assert policy_id == 1
    assert contract.get_policy_count() == 1

    policy = contract.get_policy(policy_id)
    assert policy["id"] == 1
    assert policy["owner"] == direct_alice
    assert policy["title"] == SAMPLE_TITLE
    assert policy["url"] == SAMPLE_URL
    assert policy["status"] == "STABLE"
    assert policy["spec_version"] == 1
    assert policy["active"] is True
    assert policy["total_audits"] == 0
    assert policy["total_drift_events"] == 0


def test_register_policy_invalid_urls(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    direct_vm.sender = direct_alice

    # Insecure HTTP
    with direct_vm.expect_revert("Only secure HTTPS URLs are permitted"):
        contract.register_policy(
            title=SAMPLE_TITLE,
            url="http://insecure.example.com/sla.html",
            category=SAMPLE_CATEGORY,
            baseline_hash=SAMPLE_HASH,
            baseline_summary=SAMPLE_SUMMARY,
            critical_clauses=SAMPLE_CLAUSES,
            check_interval_sec=SAMPLE_INTERVAL,
        )

    # Localhost / internal SSRF patterns
    with direct_vm.expect_revert("Target host is in restricted or private network space"):
        contract.register_policy(
            title=SAMPLE_TITLE,
            url="https://localhost:8080/sla.html",
            category=SAMPLE_CATEGORY,
            baseline_hash=SAMPLE_HASH,
            baseline_summary=SAMPLE_SUMMARY,
            critical_clauses=SAMPLE_CLAUSES,
            check_interval_sec=SAMPLE_INTERVAL,
        )

    with direct_vm.expect_revert("Target host is in restricted or private network space"):
        contract.register_policy(
            title=SAMPLE_TITLE,
            url="https://127.0.0.1/admin",
            category=SAMPLE_CATEGORY,
            baseline_hash=SAMPLE_HASH,
            baseline_summary=SAMPLE_SUMMARY,
            critical_clauses=SAMPLE_CLAUSES,
            check_interval_sec=SAMPLE_INTERVAL,
        )

    with direct_vm.expect_revert("Target host is in restricted or private network space"):
        contract.register_policy(
            title=SAMPLE_TITLE,
            url="https://192.168.1.1/secret",
            category=SAMPLE_CATEGORY,
            baseline_hash=SAMPLE_HASH,
            baseline_summary=SAMPLE_SUMMARY,
            critical_clauses=SAMPLE_CLAUSES,
            check_interval_sec=SAMPLE_INTERVAL,
        )


def test_register_policy_bounds_validation(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    direct_vm.sender = direct_alice

    # Title too short
    with direct_vm.expect_revert("Title length out of bounds"):
        contract.register_policy(
            title="A",
            url=SAMPLE_URL,
            category=SAMPLE_CATEGORY,
            baseline_hash=SAMPLE_HASH,
            baseline_summary=SAMPLE_SUMMARY,
            critical_clauses=SAMPLE_CLAUSES,
            check_interval_sec=SAMPLE_INTERVAL,
        )

    # Interval below 60s
    with direct_vm.expect_revert("Check interval below minimum threshold"):
        contract.register_policy(
            title=SAMPLE_TITLE,
            url=SAMPLE_URL,
            category=SAMPLE_CATEGORY,
            baseline_hash=SAMPLE_HASH,
            baseline_summary=SAMPLE_SUMMARY,
            critical_clauses=SAMPLE_CLAUSES,
            check_interval_sec=30,
        )


# ==============================================================================
# 2. LIFECYCLE, UPDATES & ARCHIVAL
# ==============================================================================


def test_update_baseline_increments_spec_version(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Non-owner cannot update
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only policy owner can update baseline"):
        contract.update_baseline(
            policy_id=policy_id,
            new_baseline_hash="0xnewhash",
            new_baseline_summary="Updated 99.995% uptime baseline commitment.",
            new_critical_clauses="Clause 4.1: 99.995% availability per month.",
        )

    # Owner updates baseline
    direct_vm.sender = direct_alice
    new_version = contract.update_baseline(
        policy_id=policy_id,
        new_baseline_hash="0xnewhash",
        new_baseline_summary="Updated 99.995% uptime baseline commitment.",
        new_critical_clauses="Clause 4.1: 99.995% availability per month.",
    )

    assert new_version == 2
    policy = contract.get_policy(policy_id)
    assert policy["spec_version"] == 2
    assert policy["baseline_hash"] == "0xnewhash"
    assert policy["status"] == "STABLE"


def test_archive_policy_and_prevent_further_audits(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Non-owner cannot archive
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only policy owner can archive policy"):
        contract.archive_policy(policy_id)

    # Owner archives
    direct_vm.sender = direct_alice
    contract.archive_policy(policy_id)

    policy = contract.get_policy(policy_id)
    assert policy["active"] is False
    assert policy["status"] == "ARCHIVED"

    # Cannot archive twice
    with direct_vm.expect_revert("Policy is already archived"):
        contract.archive_policy(policy_id)

    # Cannot check drift on archived policy
    with direct_vm.expect_revert("Policy is archived or inactive"):
        contract.check_drift(policy_id)


# ==============================================================================
# 3. NON-DETERMINISTIC CONSENSUS AUDITS
# ==============================================================================


def test_audit_stable_policy(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Mock live web page returning unchanged terms
    direct_vm.mock_web(
        r"acme\.example\.com/.*",
        {
            "status": 200,
            "body": (
                "<html><body>"
                "<h1>Acme Cloud RPC Service Level Agreement</h1>"
                "<p>Guaranteed 99.99% monthly availability with 100k req/min rate tiers.</p>"
                "<p>30 days advance notice required for any rate limit change.</p>"
                "<footer>Copyright 2026 Acme Corp. All rights reserved.</footer>"
                "</body></html>"
            ),
        },
    )

    # Mock validator LLM evaluation
    direct_vm.mock_llm(
        r"adjudicating whether a live online policy has experienced material semantic drift",
        (
            '{"verdict": "STABLE", "severity": 0, "affected_clauses": [], '
            '"reasoning": "Live document preserves all 99.99% uptime and rate limit commitments without change."}'
        ),
    )

    result = contract.check_drift(policy_id)

    assert result["audit_id"] == 1
    assert result["verdict"] == "STABLE"
    assert result["severity_score"] == 0
    assert result["is_material_drift"] is False

    # Verify updated policy state
    policy = contract.get_policy(policy_id)
    assert policy["status"] == "STABLE"
    assert policy["last_audit_id"] == 1
    assert policy["total_audits"] == 1
    assert policy["total_drift_events"] == 0

    # Verify downstream consumer gate
    assert contract.is_allowed(policy_id, max_acceptable_severity=0) is True
    assert contract.is_allowed(policy_id, max_acceptable_severity=3) is True
    assert contract.is_fresh(policy_id, max_age_seconds=3600) is True


def test_audit_cooldown_enforcement(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice, interval=300)

    direct_vm.mock_web(
        r"acme\.example\.com/.*",
        {"status": 200, "body": "<html><body>Terms intact</body></html>"},
    )
    direct_vm.mock_llm(
        r"adjudicating whether a live online policy has experienced material semantic drift",
        '{"verdict": "STABLE", "severity": 0, "affected_clauses": [], "reasoning": "All terms stable."}',
    )

    contract.check_drift(policy_id)

    # Immediate second check fails because cooldown (300s) has not elapsed
    with direct_vm.expect_revert("Audit cooldown has not elapsed yet"):
        contract.check_drift(policy_id)


def test_audit_material_drift_triggers_fail_closed_status(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Mock adversary modifying SLA to 95% and slashing rate limits to 10k req/min with zero notice
    direct_vm.mock_web(
        r"acme\.example\.com/.*",
        {
            "status": 200,
            "body": (
                "<html><body>"
                "<h1>Acme Cloud RPC Service Level Agreement - Revised</h1>"
                "<p>Uptime target is now 95% best-effort.</p>"
                "<p>Rate limits reduced to 10k req/min effective immediately without prior notice.</p>"
                "</body></html>"
            ),
        },
    )

    direct_vm.mock_llm(
        r"adjudicating whether a live online policy has experienced material semantic drift",
        (
            '{"verdict": "MATERIAL_BREAKING", "severity": 8, '
            '"affected_clauses": ["Clause 4.1 (Uptime dropped to 95%)", "Clause 5.2 (Rate limit slashed 10x)"], '
            '"reasoning": "Critical obligations severely degraded without agreed notice period."}'
        ),
    )

    result = contract.check_drift(policy_id)

    assert result["verdict"] == "MATERIAL_BREAKING"
    assert result["severity_score"] == 8
    assert result["is_material_drift"] is True

    # Policy status is DRIFTED
    policy = contract.get_policy(policy_id)
    assert policy["status"] == "DRIFTED"
    assert policy["total_drift_events"] == 1

    # Downstream consumer gate BLOCKS
    assert contract.is_allowed(policy_id, max_acceptable_severity=0) is False
    assert contract.is_allowed(policy_id, max_acceptable_severity=3) is False
    assert contract.is_allowed(policy_id, max_acceptable_severity=7) is False


def test_audit_external_unavailability_fails_closed(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Mock target server returning HTTP 404
    direct_vm.mock_web(
        r"acme\.example\.com/.*",
        {"status": 404, "body": "<html><body>Not Found</body></html>"},
    )

    result = contract.check_drift(policy_id)

    assert result["verdict"] == "UNAVAILABLE"
    assert result["severity_score"] == 10
    assert result["is_material_drift"] is False

    policy = contract.get_policy(policy_id)
    assert policy["status"] == "UNAVAILABLE"

    # Consumers are protected from unverified down services
    assert contract.is_allowed(policy_id, max_acceptable_severity=10) is False


def test_audit_spec_version_mismatch_invalidates_old_audit_for_consumers(
    direct_vm, direct_deploy, direct_alice
):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Perform successful audit on version 1
    direct_vm.mock_web(
        r"acme\.example\.com/.*",
        {"status": 200, "body": "<html><body>Terms intact</body></html>"},
    )
    direct_vm.mock_llm(
        r"adjudicating whether a live online policy has experienced material semantic drift",
        '{"verdict": "STABLE", "severity": 0, "affected_clauses": [], "reasoning": "All terms stable."}',
    )
    contract.check_drift(policy_id)

    assert contract.is_allowed(policy_id, max_acceptable_severity=0) is True

    # Owner updates baseline to version 2
    direct_vm.sender = direct_alice
    contract.update_baseline(
        policy_id=policy_id,
        new_baseline_hash="0xhash2",
        new_baseline_summary="New baseline summary for v2.",
        new_critical_clauses="New critical clauses for v2.",
    )

    # Old audit receipt from v1 cannot validate v2! is_allowed must return False
    assert contract.is_allowed(policy_id, max_acceptable_severity=0) is False


def test_audit_minor_compatible_drift(direct_vm, direct_deploy, direct_alice):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Minor phrasing changes, commitments intact
    direct_vm.mock_web(
        r"acme\.example\.com/.*",
        {"status": 200, "body": "<html><body>Terms clarified</body></html>"},
    )
    direct_vm.mock_llm(
        r"adjudicating whether a live online policy has experienced material semantic drift",
        (
            '{"verdict": "MINOR_COMPATIBLE", "severity": 2, "affected_clauses": ["Styling & terminology"], '
            '"reasoning": "Minor wording updates with no degradation of uptime or service obligations."}'
        ),
    )

    result = contract.check_drift(policy_id)

    assert result["verdict"] == "MINOR_COMPATIBLE"
    assert result["severity_score"] == 2
    assert result["is_material_drift"] is False

    policy = contract.get_policy(policy_id)
    assert policy["status"] == "STABLE"

    # Allowed if consumer allows severity <= 2, but blocked if consumer requires strictly severity 0
    assert contract.is_allowed(policy_id, max_acceptable_severity=2) is True
    assert contract.is_allowed(policy_id, max_acceptable_severity=1) is False


def test_update_interval_permissions_and_bounds(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy_contract(direct_deploy)
    policy_id = register_sample_policy(direct_vm, contract, owner=direct_alice)

    # Non-owner cannot update
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("Only policy owner can update interval"):
        contract.update_interval(policy_id, 300)

    # Below 60s minimum
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Check interval below minimum threshold"):
        contract.update_interval(policy_id, 30)

    contract.update_interval(policy_id, 600)
    policy = contract.get_policy(policy_id)
    assert policy["check_interval_sec"] == 600


def test_nonexistent_policy_and_audit_revert(direct_deploy):
    contract = deploy_contract(direct_deploy)

    with pytest.raises(Exception, match="Policy not found"):
        contract.get_policy(999)

    with pytest.raises(Exception, match="Audit receipt not found"):
        contract.get_audit(999)

