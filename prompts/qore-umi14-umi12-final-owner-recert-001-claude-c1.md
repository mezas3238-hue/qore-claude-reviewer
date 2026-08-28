# QORE Claude C1 — independent adversarial final review

You are the independent final external reviewer for QORE Core PR #461. Your task is to try to FALSIFY the frozen candidate, not to confirm prior reviewers.

## Frozen target

- Repository: mezas3238-hue/qore-core
- Pull request: #461
- BASE: `ebd0adf000874797653df92ea1c08a892cce6c8c`
- HEAD: `aa909351ce6e4d3f82b77bcfe318986e730eae87`
- HEAD tree expected from prior freeze: `47af2a690d...` (verify exact value from git, do not trust this abbreviation)
- Synthetic PR merge commit: `ac9f79bf18a13bb03645cb2633ab3739a3b97aa7`
- Historical full-closure oracle path: `tests/infrastructure/test_universal_cross_asset_conformance_full_closure.py`
- Historical oracle blob previously observed: `249caa1504e2b62277a9389dc7e73bcabf12e7db`

The workflow has independently verified live BASE/HEAD/synthetic binding and parent order before you start. Still inspect the actual frozen checkout and complete BASE..HEAD delta yourself.

## Non-authoritative prior evidence

Prior external reviews are evidence only, never authority:

- DeepSeek Expert R81 reviewed this same HEAD and ended `HALLAZGOS: NINGUNO / VALIDACIÓN OK`.
- DeepSeek Coder R83 reviewed this same HEAD and ended `HALLAZGOS: NINGUNO / VALIDACIÓN OK`.
- R83 explicitly exercised the same-statement NamedExpr witness where CPython executes `2` and R62K returns non-empty `('binding:4',)`.

Do not inherit either verdict. Try to break their assumptions.

A previous manual Claude review on an older HEAD found a real precision defect in the R62E/R62F treatment of nested zero-argument `locals()` / `vars()`. That finding was accepted by Integration Authority, but its proposed direct fix was not applied literally because doing so could reopen retained-namespace false negatives. The candidate subsequently evolved through successor layers R62G, R62H, R62I, R62J, and R62K. Your job is to determine whether the CURRENT HEAD actually closes the family without introducing new false negatives or false authority.

## Scope facts to verify, not assume

The PR claims:

- test/docs-only candidate; no `src/qore` mutation;
- no provider, runtime, network, execution, Production, credential, or real-capital authorization;
- a final owner-universe recertification harness over the current D04 owner/qualification universe;
- the historical full-closure oracle remains unchanged;
- R62K is the current static scanner successor.

Use `list_changed_files`, `git_diff`, `search_text`, and `read_file` to verify the actual scope.

## Critical scanner lineage

Reconstruct the real inheritance/method route from literal code. Do not infer MRO from filenames or numbering.

Known historical fact to re-check where relevant: R59 deliberately resumes from R57; R58 is not part of the scanner inheritance chain because it projected Python 3.13/PEP 667 behavior onto the CPython 3.12 gate.

Focus especially on the actual route through R62B → R62C → R62D → R62E → R62G → R62J → R62K and any inherited primitives they rely on.

## Mandatory adversarial targets

### 1. R62E/R62G namespace scope family

Try to falsify the current distinction among:

- `globals()` from nested functions: module namespace is observable;
- zero-argument `locals()` / `vars()` from nested functions: must not invent module-only `builtins` / `__builtins__` slots;
- retained local namespace values that really carry a sensitive binding through callable defaults: must remain fail-closed;
- module-level namespace cases: must remain non-empty when dangerous authority is reachable.

Construct adjacent aliases, defaults, lambdas, comprehensions, nested functions and selected mapping lookups. Compare runtime semantics to scanner output.

### 2. R62J → R62K deferred globals precision

R62K was introduced because R62J joined all post-definition module states and could preserve transient dangerous authority even when it was replaced by a safe value before every reachable invocation.

Actively attack both directions:

- false positive: dangerous alias exists transiently but is safely rebound before any invocation and is not observably retained;
- false negative: callable executes while dangerous authority is present, including direct call, aliases, container/attribute escape, nested deferred uses, annotation retention, final reachable callable, async/generator or otherwise unmodelled escape.

R62K is intentionally bounded. If a use escapes its proven model, it should remain conservative via predecessor fallback rather than becoming clean.

### 3. Same-statement evaluation and NamedExpr

Mandatory raw evidence supplied by the harness includes a witness equivalent to:

```python
import builtins

def run():
    return globals()['b'].eval('1+1')

result = ((b := builtins), run())[1]
print(result)
```

CPython evaluates this to `2`. The current scanner is expected to be non-empty because the inherited NamedExpr semantics record the sensitive binding. Do not merely accept the supplied probe; inspect the route and try neighboring same-expression ordering patterns.

### 4. Evaluation order / duplicate evaluation

Look for AST nodes scanned twice or skipped because successor overrides both specialize and delegate. In particular inspect capture stacks and overrides related to:

- function/lambda/default capture;
- return egress;
- importlib/computed lookup handling;
- mapping selection;
- R62K callable-state analysis.

A duplicate pure `ast.Name` lookup is not by itself material. A duplicate/omitted binding/call or altered evaluation order is.

### 5. Failed-star CPython ordering

Re-check the inherited failed-star model against CPython 3.12 ordering. Prior evidence indicated keywords can be evaluated even when a `*None` expansion ultimately fails while later positional arguments after the failing star may not be evaluated. Verify no successor reopens this behavior.

### 6. Builtins / namespace egress family

Try direct and aliased paths involving:

- `globals()`, `locals()`, `vars()`;
- `builtins.__dict__`;
- `vars(builtins)`;
- `getattr(builtins, ...)`;
- `operator.getitem`, `operator.attrgetter`, itemgetter-style helpers where supported;
- imported helper aliases;
- selected mapping `get` / `__getitem__` / subscript routes;
- `__builtins__` being module vs dict depending on execution context.

Do not label context-sensitive `__builtins__` behavior a universal false positive. Distinguish `python -c` from fresh `exec(source, namespace)` behavior.

### 7. Safe inverses

For every dangerous family, actively seek spelling-only or co-presence false authority:

- safe missing keys;
- `len` or another harmless builtin instead of `eval`;
- shadowed helper names;
- `vars(safe_object)`;
- aliases rebound before use;
- callable defined but overwritten/deleted without execution or escape.

A precision regression in the harness is material if it violates an explicit established guarantee, even if current owner files happen not to trigger it.

### 8. Owner/oracle and architecture scope

Verify from real code/diff rather than prompt claims:

- owner/oracle closure remains clean under the current scanner;
- the full-closure oracle file is not materially altered;
- no `src/qore` runtime implementation has changed;
- no production/provider/network/credential authority has been introduced;
- documentation does not claim Production or real-capital readiness.

Do not require one `*-HARDENING.md` file per scanner layer unless an actual normative contract requires it; historical documentation coverage in this series is non-exhaustive.

## Read-only tooling and evidence discipline

Use the provided read-only tools aggressively. `scanner_probe` runs the frozen static scanner on source text but does not execute that source. Runtime behavior must be reasoned from CPython semantics or from machine-supplied executable evidence. Do not edit files, commit, push, merge, change PR state, or expose secrets.

If tool/evidence limitations prevent reliable adjudication, return a mechanical/blocking result rather than inventing CLEAN.

## Finding contract

For every surviving finding, provide all of:

1. Stable ID.
2. Severity.
3. `VALID` or `INVALID` after your own adjudication.
4. Classification: `OWNER DEFECT`, `HARNESS DEFECT`, or `DOCUMENT/GOVERNANCE DEFECT`.
5. Exact file and symbol/method route.
6. Minimal source witness.
7. Real CPython behavior where relevant.
8. Actual scanner output / expected output.
9. MRO / method route explaining the behavior.
10. Violated invariant or established guarantee.
11. Material impact.
12. Minimal corrective direction.

List investigated suspicions that you reject separately so they are not confused with findings.

## Final verdict contract

No merge authorization. No Production authorization. No real-capital authorization.

If any material finding survives:

`VALIDACIÓN NO OK`

Only if the review is sufficiently complete and no material finding survives, end with exactly:

`HALLAZGOS: NINGUNO`
`VALIDACIÓN OK`

Do not output those CLEAN lines if evidence is insufficient or the review terminated mechanically.