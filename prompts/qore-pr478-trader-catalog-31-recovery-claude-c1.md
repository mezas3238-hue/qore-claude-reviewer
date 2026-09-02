# Claude C1 — PR #478 recovered 31-trader capability inventory

Act as the final independent adversarial semantic reviewer of qore-core PR #478. This is a fresh package. Do not inherit DeepSeek Expert, DeepSeek Coder, or Integration Authority verdicts as truth; use them only as context to challenge.

## Deliberate trust and tool boundary

Your session is intentionally read-only. The workflow itself verifies the live PR binding, exact frozen HEAD, synthetic merge, authoritative QORE Quality Gate evidence, checkout integrity, and post-review immutability. Treat those observations as the mechanical evidence layer. Your authority is semantic: inspect the exact checkout with the available read/search tools, trace source/contracts/tests/docs, and falsify the claims in the changed document.

Report `MECHANICAL REVIEW FAILURE` only if the workflow evidence is missing, internally inconsistent, bound to the wrong freeze, or the exact checkout cannot be read. Do not treat lack of Bash/network in the Claude session itself as a defect.

## Exact frozen target

- Repository: `mezas3238-hue/qore-core`
- PR: `#478 — Recover 31-trader capability inventory from completed Harness evidence`
- BASE: `5a158ef0fb2e21db95f2be0685373780bf1ab197`
- BASE TREE: `5e2b37b23b01fe23fd373d39b01573e9607a73ad`
- HEAD: `bdeb7525a1249f4f328bc618249f1df80c804f56`
- HEAD TREE: `67c77fbe016b6688e5114165a5a14c3026832027`
- SYNTHETIC: `6ea11290b501c4276a4da7db0d8ea01668042e3b`
- SYNTHETIC TREE: `67c77fbe016b6688e5114165a5a14c3026832027`
- Changed files: exactly one
- Changed file: `docs/audits/QORE-TRADER-CATALOG-31-CAPABILITY-INVENTORY-001.md`
- Diff: `+195/-0`
- `src/` delta: 0
- `tests/` delta: 0
- Authoritative QORE CI run: `33681607355`
- quality job: `100419247337`
- Ruff: PASS
- Mypy: PASS over 740 source files
- Pytest: 4862/4862 PASS, 7 warnings
- Coverage TOTAL: 47568 statements, 6234 missed, 87%

Any mismatch in these bindings is blocking and must be reported as mechanical failure rather than semantically reviewing a different candidate.

## Purpose of this PR

This is a docs-only recovery/adjudication of completed Harness Batch 003 evidence. It does NOT implement the 31 traders. It materializes the capability inventory and engineering route for subsequent Trader implementation, Trader Lab, CIBO, and DEMO work.

## Primary claims to falsify

1. Exactly 31 canonical Trader identities are represented and no identity is duplicated or omitted.

2. The document does not falsely claim concrete methodology evaluators for the 31 named Traders. The expected state is that concrete evaluator implementations are absent, except that VT-30 has supporting infrastructure but no concrete Midpoints evaluator.

3. VT-30 Trader Midpoints must be accurately classified as:

`SUPPORTING_INFRA_PRESENT / CONCRETE_EVALUATOR_ABSENT / TRADER_LAB_NOT_YET_PASSED`

Supporting infrastructure may include native-BID/market-observation provenance, deterministic retained market-event replay, and DST-aware market-clock/schedule primitives. Verify that these foundations exist and that no concrete Midpoints evaluator is being laundered from them.

4. All 31 Traders require individual Trader Lab qualification before DEMO admission. No cohort/family inheritance, CI-green shortcut, CIBO preference, or reviewer verdict may silently substitute for individual qualification.

5. The first DEMO cohort is only a target, conditional on individual qualification:

- VT-01
- VT-08
- VT-09
- VT-17
- VT-31

Alternate: VT-29.

This target must not imply profitability, DEMO eligibility, execution authority, provider availability, or readiness.

6. Synthetic Traders VT-20..VT-28 must remain blocked on real provider/instrument capability unless such capability is actually established. The document must not silently assume provider availability.

7. CIBO gains no execution authority, Risk bypass, Trader Lab bypass, provider-native order authority, Production authority, or real-capital authority.

8. The document must not invent methodology semantics. Any qualitative methodology term that is not deterministically formalized must remain explicitly pending/formalization/evidence bound rather than silently converted into rules or thresholds.

9. The proposed next engineering delta must not materially direct implementation toward duplicate contracts where exact reusable identity/order/research/replay/market-clock/Risk seams already exist.

## Hard safety and readiness laws

`CATALOG ENTRY != IMPLEMENTED TRADER`

`IMPLEMENTED TRADER != TRADER LAB PASS`

`TRADER LAB PASS != PROFITABILITY`

`DEMO_ELIGIBLE != DEMO_PROFITABLE`

`CIBO MANAGEMENT != EXECUTION AUTHORITY`

`CIBO MANAGEMENT != RISK BYPASS`

`DEMO EVIDENCE != PRODUCTION AUTHORIZATION`

No Production accounts. No real capital. No real-money autonomous execution.

## Known prior non-blocking observations to challenge independently

Previous reviewers noted possible documentation imprecisions around:

- zone-parametric DST clock wording versus `America/New_York` wording;
- M15 implemented versus qualified/wired wording;
- M1 ingress dependency for VT-31;
- VT-17 90-minute methodology provenance requiring formalization;
- unused PROVIDER/TF taxonomy tokens;
- undefined `31×N` / `31×31` shorthand;
- CIBO `advisory` wording versus existing supervised TEST/DEMO decision semantics;
- trader naming/slug normalization;
- external PR provenance wording;
- prospective versus present tense around Midpoints infrastructure.

Do not automatically preserve these as MINOR. Re-evaluate whether any causes a material false claim, authority expansion, incorrect readiness state, provider assumption, implementation misdirection, or lifecycle bypass. If not, keep them non-blocking.

## Material finding standard

A finding is material if the frozen document would materially:

- misstate actual implementation;
- invent methodology;
- wrongly classify a Trader;
- authorize or imply an unauthorized DEMO/Production path;
- allow Trader Lab bypass;
- allow Risk bypass;
- grant CIBO execution authority;
- silently assume provider capability;
- materially misdirect the next implementation;
- contradict a previously closed architectural invariant;
- falsely claim qualification, readiness, profitability, or provider support.

Cosmetic wording, optional taxonomy cleanup, or maintainability recommendations are not material unless they create one of those consequences.

## Required review focus

Inspect the exact HEAD and changed document against source/contracts/tests/architecture. Pay special attention to:

A. VT-30 supporting-infrastructure-versus-evaluator boundary.

B. 31/31 identity/count/status integrity.

C. First-five target versus readiness/profitability implication.

D. Trader Lab lifecycle language versus other governing promotion/approval stages.

E. CIBO authority boundaries.

F. Risk/execution/Production boundaries.

G. Provider capability claims for VT-20..VT-28.

H. Reuse versus duplicate-contract risk in the proposed next engineering direction.

I. Any statement that turns external methodology records or CEO-supplied fichas into implied implementation without evidence.

## Output

Separate MATERIAL findings from MINOR/non-blocking observations.

For each material finding provide:

- ID
- severity
- exact file/line or section
- exact claim
- repository evidence
- consequence
- falsification/reproduction reasoning
- smallest bounded correction

If any material semantic finding survives, end with exactly:

`VALIDACIÓN NO OK`

Only if no material finding survives, end with exactly these final two lines:

HALLAZGOS: NINGUNO
VALIDACIÓN OK

Do not authorize merge, DEMO eligibility, Production, or real capital. Your role is review only.