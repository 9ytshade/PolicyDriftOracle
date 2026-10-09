# DECISION.md — PolicyDriftOracle

## 1. Executive Primitive Thesis

`PolicyDriftOracle` is a reusable GenLayer Intelligent Contract primitive that continuously audits public machine-readable policies, API Service Level Agreements (SLAs), Model Cards, and terms against an immutable baseline commitment, reaching validator consensus on whether **material semantic drift** has occurred without generating false alarms from trivial whitespace, copyright, or styling changes.

---

## 2. Builder Identity & Isolation

- **Builder**: `9ytshade`
- **Deployer Signer**: `9ytshade_Deployer` (`0xb704b624ae5f776b3a3fa7496adcda4db4dcab56`)
- **Dedicated Testers**: `9ytshade_Tester_1` (`0x71dc2e10c22d14f39ed6c9c7e45708060f0d5de8`), `9ytshade_Tester_2` (`0xd339df2a002d4c8c4257e8e9d2508a31e9e036a9`)
- **Remote Push Policy**: 100% Local verification only. Zero remote pushing; manual upload by author.

---

## 3. Portfolio Collision Audit

Collision check across `9ytshade`'s existing repositories:

| Existing Repo | Core Trust Question | Evidence | Consensus Decision | Overlap with PolicyDriftOracle? |
| :--- | :--- | :--- | :--- | :--- |
| `chainsettle` | Did worker deliver agreed freelance milestone? | Git commit / demo URL | Payout split (BPS) vs Dispute | **No** — Freelance milestone court |
| `proofpay` | Did reviewer submit valid purchase receipt? | Store receipt URL | Bounty release / Slash stake | **No** — Consumer purchase bounty |
| `Trust-Checker`| Is an address or domain reputable? | Off-chain heuristics | Heuristic rating | **No** — Web3 reputation bot |
| **`PolicyDriftOracle`** | **Has a published legal/technical policy materially drifted from baseline?** | **Live HTTPS policy text** | **Semantic drift severity enum & bitmask** | **NEW PRIMITIVE** |

---

## 4. Candidate Scoring & The Delete-GenLayer Test

### Scoring (0–10)
1. **GenLayer Necessity**: 10/10 — Natural language comparison over live web documents cannot be performed deterministically without hallucination or single-point-of-failure.
2. **Novelty against Owner Portfolio**: 10/10 — Completely orthogonal to milestone and receipt escrow.
3. **Ecosystem Utility**: 9/10 — Any DeFi protocol, DAO treasury, or smart agent consuming external Web2/Web3 services requires SLA guarantees.
4. **State Machine & Failure Bounds**: 10/10 — Fail-closed on fetch errors; strict monotonically incrementing audit rounds; immutable baseline versioning.

### The "Delete-GenLayer" Test
> *If GenLayer is removed, what exact trust property disappears?*
Without GenLayer, an application relying on external SLAs or terms must either:
1. Rely on a **centralized keeper / oracle node** to author the drift verdict (creating extortion/bribery risk where the keeper colludes with the service provider).
2. Rely on a **rigid sha256 byte hash**, which fails immediately whenever the service updates their copyright footer, fixes a typo, or reorganizes HTML headers (false alarm crisis).

GenLayer is load-bearing because independent validators fetch the live document, parse the clauses, and agree on whether **substantive obligations** were breached.

---

## 5. The Three-Consumer Test

`PolicyDriftOracle` exposes a small, strongly typed view interface (`is_allowed`, `latest_verdict`, `is_fresh`) consumed by three distinct architectures without modifying the primitive:

1. **Autonomous DAO Treasury (Subscription Gatekeeper)**:
   - A treasury contract paying monthly/annual fees to an RPC or infrastructure provider calls `is_allowed(policy_id, max_severity=1)`.
   - If the provider quietly modifies their rate limits or data retention clauses, the treasury halts recurring payment streams.

2. **DeFi Insurance Vault (Parametric Policy Breach Claims)**:
   - Users lock collateral or buy insurance against cloud/API SLA breaches.
   - The claims contract queries `latest_verdict(policy_id)`. If status is `DRIFTED` with severity $\ge 5$, it automatically unlocks parametric indemnification payouts.

3. **Cross-Chain Bridge Circuit Breaker**:
   - A bridge or oracle layer that relies on external validator set specifications or security policies checks `is_fresh(policy_id, max_age=86400)` and `is_allowed(policy_id, max_severity=0)`.
   - If a breaking change occurs, cross-chain message execution is paused to prevent exploits.

---

## 6. Deterministic vs. Non-Deterministic Boundary

```
+-------------------------------------------------------------+
| NON-DETERMINISTIC STAGE (Validators in GenVM)               |
| - Fetch live policy web page via gl.nondet.get_web_page     |
| - Parse document text against baseline summary & clauses    |
| - Classify drift severity (NONE, MINOR, MATERIAL) via prompt|
| - Equivalence Principle: Comparative consensus on verdict   |
+-------------------------------------------------------------+
                              |
                              v (Structured observation)
+-------------------------------------------------------------+
| DETERMINISTIC STAGE (Contract Logic)                        |
| - Enforce URL admission (HTTPS only, length <= 256)         |
| - Enforce check cooldown intervals                          |
| - Enforce baseline version increments                       |
| - Map consensus observation into strict status transition   |
| - Maintain bounded audit ring buffer & monotonic IDs        |
| - Expose machine-readable boolean views for consumers       |
+-------------------------------------------------------------+
```
