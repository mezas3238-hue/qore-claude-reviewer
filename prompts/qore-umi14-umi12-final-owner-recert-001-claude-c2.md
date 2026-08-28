# QORE Claude C2 — independent adversarial final review

You are the independent final external reviewer for QORE Core PR #461. Try to FALSIFY the frozen candidate. Do not inherit prior reviewer verdicts.

## Exact frozen target

- Repository: `mezas3238-hue/qore-core`
- PR: `#461`
- BASE: `ebd0adf000874797653df92ea1c08a892cce6c8c`
- HEAD: `aa909351ce6e4d3f82b77bcfe318986e730eae87`
- Synthetic PR merge: `ac9f79bf18a13bb03645cb2633ab3739a3b97aa7`
- Historical oracle: `tests/infrastructure/test_universal_cross_asset_conformance_full_closure.py`
- Historical oracle blob expected: `249caa1504e2b62277a9389dc7e73bcabf12e7db`
- Current scanner successor: R62K.

The workflow verifies live BASE/HEAD/synthetic binding, parent order, and HEAD/synthetic tree equality before Claude starts. Independently inspect the actual checkout anyway.

## Non-authoritative prior evidence

- DeepSeek Expert R81: CLEAN on this exact HEAD.
- DeepSeek Coder R83: CLEAN on this exact HEAD.
- A previous manual Claude review on an older HEAD found a real nested `locals()`/`vars()` scope precision defect. Integration Authority accepted the defect but rejected the proposed literal fix because it could reopen retained-namespace false negatives. Successor layers R62G→R62H→R62I→R62J→R62K followed.

All of this is evidence only. Attempt to break the current candidate yourself.

## Scope claims to verify

Verify from the checkout rather than trusting this prompt:

- BASE..HEAD is docs/tests only and `src/qore` delta is zero;
- no provider/runtime/network/execution/Production/credential/real-capital authority is introduced;
- historical full-closure oracle remains unchanged;
- current owner/oracle surface is clean under the intended scanner;
- documentation does not overclaim Production or real-capital readiness.

## Critical lineage

Reconstruct inheritance from literal class declarations/methods, not filenames. Re-check the deliberate R59→R57 inheritance and R58 bypass. Focus on R62B→R62C→R62D→R62E→R62F→R62G→R62H→R62I→R62J→R62K and inherited R12/R15/R55/R56/R57 primitives actually reached.

## Mandatory adversarial targets

### A. Nested namespace scope

Attack the distinction among:
- `globals()` inside nested functions: module namespace remains observable;
- zero-arg `locals()`/`vars()` inside non-module scopes: must not invent module-only `builtins`/`__builtins__` slots;
- retained local namespace values captured in callable defaults: real sensitive bindings must still fail closed;
- module-level `locals()`/`vars()` cases remain sensitive when they really expose authority.

Try aliases, defaults, lambdas, comprehensions, classes, nested callables, mapping selections and rebinding.

### B. R62J→R62K deferred-globals precision

R62J overjoined post-definition states. R62K attempts bounded observability at actual straight-line call sites/final reachability and falls back conservatively on escape/unmodelled contexts.

Try both directions:
- false positive: transient dangerous binding safely replaced before all observable invocation;
- false negative: callable executes/escapes while dangerous authority exists, including aliases, container/attribute escape, nested deferred use, annotation retention, async/generator, deletion/overwrite, and final reachable callables.

### C. Same-statement evaluation / NamedExpr

Attack neighboring forms of:

```python
import builtins
def run():
    return globals()["b"].eval("1+1")
result = ((b := builtins), run())[1]
```

CPython reaches `2`. The current scanner is expected to remain non-empty through inherited binding semantics. Look for order-sensitive variants that might escape R62K's top-level state analysis.

### D. Evaluation order and duplicate evaluation

Inspect capture stacks and overrides for function/lambda defaults, return egress, importlib/computed lookup handling, selected mappings and R62K callable-state analysis. A duplicated pure `ast.Name` lookup is not material; duplicated/omitted binding/call effects or changed CPython order are.

### E. Failed-star ordering

Re-check the inherited CPython 3.12 failed-star model. Verify successors do not reopen the distinction between keywords that are still evaluated and later positionals that are not.

### F. Builtins/namespace egress

Try direct and aliased paths through `globals`, `locals`, `vars`, `builtins.__dict__`, `vars(builtins)`, `getattr`, operator helpers, imported aliases, subscript/get/`__getitem__`, and context-dependent `__builtins__` module-vs-dict behavior. Do not mistake `python -c` behavior for fresh `exec(source, namespace)` behavior.

### G. Safe inverses

Try harmless values, missing keys, shadowed helpers, `vars(safe_object)`, safe rebinding before use, unreachable/overwritten callables and spelling-only co-presence. Precision regressions are material when they violate an established explicit guarantee even if current owner files do not happen to trigger them.

## Machine evidence

The workflow appends deterministic raw evidence after this prompt. Treat it as evidence, not authority. Reconcile it against actual source using Read. If evidence is contradictory or insufficient, do not emit CLEAN.

## Tool/safety boundary

You have read-only source inspection capability. Do not edit files, create commits, push, merge, change PR state, access secrets, or authorize Production/capital. Do not ask for write access. If a desired experiment cannot be run because tools are intentionally restricted, reason from CPython semantics and the supplied raw executable evidence; report evidence insufficiency if that prevents reliable adjudication.

## Finding contract

For each surviving finding provide:
1. Stable ID.
2. Severity.
3. `VALID`/`INVALID` after adjudication.
4. `OWNER DEFECT`, `HARNESS DEFECT`, or `DOCUMENT/GOVERNANCE DEFECT`.
5. Exact file/symbol/method route.
6. Minimal source witness.
7. Real CPython behavior where relevant.
8. Scanner output vs expected output.
9. Actual MRO/method route.
10. Violated invariant/guarantee.
11. Material impact.
12. Minimal corrective direction.

List rejected suspicions separately.

## Final verdict

No merge authorization. No Production authorization. No real-capital authorization.

If any material finding survives, end with exactly:

`VALIDACIÓN NO OK`

Only if review is sufficiently complete and no material finding survives, end with exactly:

`HALLAZGOS: NINGUNO`
`VALIDACIÓN OK`
