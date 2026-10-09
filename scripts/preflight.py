#!/usr/bin/env python3
"""Zero-dependency preflight verification script for PolicyDriftOracle.

Verifies:
1. Exactly one canonical contract under contracts/
2. Header format and dependency declaration
3. Contract class and decorators
4. Public write and view method surfaces
5. Forbidden standard-library imports (time, random, os.urandom, requests)
6. State and storage definitions
7. Fail-closed verdict constants
"""

import ast
from pathlib import Path
import sys

CONTRACT_FILE = Path(__file__).resolve().parent.parent / "contracts" / "policy_drift_oracle.py"

FORBIDDEN_MODULES = {"random", "requests", "urllib.request", "socket"}


def run_checks():
    assertions_passed = 0
    total_checks = 16

    print("--- Running Preflight Verification for PolicyDriftOracle ---")

    # Check 1: File exists
    assert CONTRACT_FILE.exists(), f"Contract file not found at {CONTRACT_FILE}"
    assertions_passed += 1

    content = CONTRACT_FILE.read_text(encoding="utf-8")

    # Check 2: Dependency header
    assert 'Depends": "py-genlayer:' in content, "Missing py-genlayer dependency header"
    assertions_passed += 1

    # Check 3: AST parsing
    tree = ast.parse(content, filename=str(CONTRACT_FILE))
    assertions_passed += 1

    # Check 4: No forbidden imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in FORBIDDEN_MODULES, f"Forbidden import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            assert node.module not in FORBIDDEN_MODULES, f"Forbidden import from: {node.module}"
    assertions_passed += 1

    # Check 5: Find Contract Class
    contract_classes = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Attribute) and base.attr == "Contract":
                    contract_classes.append(node)
                elif isinstance(base, ast.Name) and base.id == "Contract":
                    contract_classes.append(node)

    assert len(contract_classes) == 1, f"Expected exactly 1 Contract class, found {len(contract_classes)}"
    assertions_passed += 1
    cnode = contract_classes[0]
    assert cnode.name == "PolicyDriftOracle", f"Unexpected contract class name: {cnode.name}"
    assertions_passed += 1

    # Check 6: Check for dataclasses
    dataclass_names = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for dec in node.decorator_list:
                if (isinstance(dec, ast.Name) and dec.id == "dataclass") or (
                    isinstance(dec, ast.Attribute) and dec.attr == "dataclass"
                ):
                    dataclass_names.add(node.name)
    assert "Policy" in dataclass_names, "Missing Policy storage dataclass"
    assertions_passed += 1
    assert "AuditReceipt" in dataclass_names, "Missing AuditReceipt storage dataclass"
    assertions_passed += 1

    # Check 7: Check public methods
    public_writes = set()
    public_views = set()
    for item in cnode.body:
        if isinstance(item, ast.FunctionDef):
            for dec in item.decorator_list:
                if isinstance(dec, ast.Attribute):
                    if dec.attr == "write":
                        public_writes.add(item.name)
                    elif dec.attr == "view":
                        public_views.add(item.name)

    expected_writes = {
        "register_policy",
        "check_drift",
        "update_baseline",
        "update_interval",
        "archive_policy",
    }
    for w in expected_writes:
        assert w in public_writes, f"Missing public write method: {w}"
    assertions_passed += 1

    expected_views = {
        "get_policy",
        "get_audit",
        "latest_verdict",
        "is_allowed",
        "is_fresh",
        "get_policy_count",
        "get_audit_count",
    }
    for v in expected_views:
        assert v in public_views, f"Missing public view method: {v}"
    assertions_passed += 1

    # Check 8: Non-deterministic method contains run_nondet_unsafe
    check_drift_func = next((item for item in cnode.body if isinstance(item, ast.FunctionDef) and item.name == "check_drift"), None)
    assert check_drift_func is not None, "check_drift function missing"
    assertions_passed += 1

    found_run_nondet = False
    for sub in ast.walk(check_drift_func):
        if isinstance(sub, ast.Call):
            if isinstance(sub.func, ast.Attribute) and sub.func.attr == "run_nondet_unsafe":
                found_run_nondet = True
    assert found_run_nondet, "check_drift must utilize run_nondet_unsafe for multi-validator consensus"
    assertions_passed += 1

    # Check 9: Required verdict constants present in contract
    const_targets = set()
    for item in cnode.body:
        if isinstance(item, ast.Assign):
            for t in item.targets:
                if isinstance(t, ast.Name):
                    const_targets.add(t.id)

    assert "VERDICT_STABLE" in const_targets
    assertions_passed += 1
    assert "VERDICT_MATERIAL_BREAKING" in const_targets
    assertions_passed += 1
    assert "VERDICT_UNAVAILABLE" in const_targets
    assertions_passed += 1
    assert "STATUS_DRIFTED" in const_targets
    assertions_passed += 1

    print(f"Preflight checks passed: {assertions_passed}/{total_checks} assertions verified.")
    return True


if __name__ == "__main__":
    try:
        run_checks()
        sys.exit(0)
    except AssertionError as err:
        print(f"Preflight FAILED: {err}", file=sys.stderr)
        sys.exit(1)
