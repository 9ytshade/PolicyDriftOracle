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
| **`PolicyDriftOracle`** | **Has a published legal/technical policy materially drifted from baseline?** | **Live HTTPS policy text** | **Semantic drift severity enum & bitmask** | **NEW PRIMITIVE (Zero Collision)** |

---

## 4. Candidate Exploration & Selection Matrix

Ten candidate primitives were evaluated during architecture scouting:

| Candidate Primitive | Core Trust Question | GenLayer Necessity (0-10) | State Reusability | Status / Rejection Rationale |
| :--- | :--- | :---: | :---: | :--- |
| 1. `PolicyDriftOracle` | Has a published web policy/SLA materially drifted from committed baseline? | **10** | High | **SELECTED**: Universal trust primitive for DAOs, escrow, insurance. |
| 2. `SocialSentimentIndex` | What is general twitter sentiment on token X? | 4 | Low | **REJECTED**: Sybil-prone, noisy, subjective chatter, not a protocol gate. |
| 3. `OnChainResume` | Did an applicant work at company Y? | 6 | Low | **REJECTED**: Requires private HR verification, inaccessible to validators. |
| 4. `BugBountyCourt` | Does submitted vulnerability meet payout severity? | 8 | Medium | **REJECTED**: Highly domain-complex code exploit verification. |
| 5. `CodeAuditOracle` | Does a smart contract repository contain critical bugs? | 8 | Medium | **REJECTED**: Repository scale exceeds validator execution timeouts. |
| 6. `WeatherParametric` | Did rainfall fall below X mm? | 3 | Medium | **REJECTED**: Deterministic API numbers; traditional Chainlink suffices. |
| 7. `AgentTuringGate` | Is an external caller an autonomous agent? | 5 | Low | **REJECTED**: Adversarially unstable; heuristic rather than protocol primitive. |
| 8. `LegalContractSigner` | Did two parties sign a legal agreement? | 4 | Low | **REJECTED**: Static e-signature verification; better served by standard crypto. |
| 9. `ModelCardAuditor` | Did an AI model's safety weights/bias change? | 7 | Medium | **REJECTED**: Special case of policy drift with heavy binary dependencies. |
| 10. `DomainSquatShield` | Did a trademark holder's domain get hijacked? | 6 | Low | **REJECTED**: ICANN/WHOIS privacy blocks live validator inspection. |

---

## 5. Candidate Scoring & The Delete-GenLayer Test

### Scoring Dimensions (0–10)
1. **GenLayer Necessity**: 10/10 — Natural language comparison over live web documents cannot be performed deterministically without single-point-of-failure or false alarms.
2. **Novelty against Owner Portfolio**: 10/10 — Completely orthogonal to freelance and purchase escrow.
3. **Ecosystem Utility**: 9/10 — Any DeFi protocol, DAO treasury, or smart agent consuming external Web2/Web3 services requires SLA guarantees.
4. **State Machine & Failure Bounds**: 10/10 — Fail-closed on fetch errors; strict monotonically incrementing audit rounds; immutable baseline versioning.

### The "Delete-GenLayer" Test
> *If GenLayer is removed, what exact trust property disappears?*
Without GenLayer, an application relying on external SLAs or terms must either:
1. Rely on a **centralized keeper / oracle node** to author the drift verdict (creating extortion/bribery risk where the keeper colludes with the service provider).
2. Rely on a **rigid sha256 byte hash**, which fails immediately whenever the service updates their copyright footer, fixes a typo, or reorganizes HTML headers (false alarm crisis).

GenLayer is load-bearing because independent validators fetch the live document, parse the clauses, and agree on whether **substantive obligations** were breached.

---

## 6. The Three-Consumer Test

`PolicyDriftOracle` exposes a small, strongly typed view interface (`is_allowed`, `latest_verdict`, `is_fresh`) consumed by three distinct architectures without modifying the primitive:

1. **Autonomous DAO Treasury (Subscription Gatekeeper)**:
   - A treasury contract paying monthly/annual fees to an RPC or infrastructure provider calls `is_allowed(policy_id, max_severity=1)`.
   - If the provider quietly modifies their rate limits or data retention clauses, the treasury halts recurring payment streams.

2. **DeFi Insurance Vault (Parametric Policy Breach Claims)**:
   - Users lock collateral or buy insurance against cloud/API SLA breaches.
   - The claims contract queries `latest_verdict(policy_id)`. If status is `DRIFTED` with severity $\ge 50$, it automatically unlocks parametric indemnification payouts.

3. **Cross-Chain Bridge Circuit Breaker**:
   - A bridge or oracle layer that relies on external validator set specifications or security policies checks `is_fresh(policy_id, max_age=86400)` and `is_allowed(policy_id, max_severity=0)`.
   - If a breaking change occurs, cross-chain message execution is paused to prevent exploits.

---

## 7. Hardest Technical Risk & Mitigation

- **Risk**: Semantic nondeterminism causing validator splits over benign syntactic or stylistic revisions.
- **Mitigation**: Comparative equivalence principle focusing strictly on categorical verdict (`STABLE` vs `MATERIAL_DRIFT`) and numeric severity bands (0, 25, 50, 75, 100), rather than free-form text matching.

---

## 8. Deterministic vs. Non-Deterministic Boundary

```
+-------------------------------------------------------------+
| NON-DETERMINISTIC STAGE (Validators in GenVM)               |
| - Fetch live policy web page via gl.get_webpage             |
| - Parse document text against baseline summary & clauses    |
| - Classify drift severity (NONE, MINOR, MATERIAL) via prompt|
| - Equivalence Principle: Comparative consensus on verdict   |
+-------------------------------------------------------------+
                              |
                              v (Structured observation)
+-------------------------------------------------------------+
| DETERMINISTIC STAGE (Contract Logic)                        |
| - Enforce URL admission (HTTPS only, RFC1918 / SSRF blocked)|
| - Enforce check cooldown intervals                          |
| - Enforce baseline version increments                       |
| - Map consensus observation into strict status transition   |
| - Maintain bounded audit ring buffer & monotonic IDs        |
| - Expose machine-readable boolean views for consumers       |
+-------------------------------------------------------------+
```
