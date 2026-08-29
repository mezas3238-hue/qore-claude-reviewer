# Claude C4 — QORE UMI14 / UMI12 final owner recertification

Act as the final independent adversarial reviewer of qore-core PR #461. Do not inherit any prior DeepSeek or Claude verdict. GitHub live bindings, exact checkout, CPython 3.12 behavior and reproducible evidence are authoritative.

## Exact corrected freeze
- BASE `ebd0adf000874797653df92ea1c08a892cce6c8c`, tree `08ce942dd944a2c02a1aa9971dbfbe011def919d`.
- HEAD `476a93cdd08a064d0b99a139cd1b49287b937f21`, tree `5e2b37b23b01fe23fd373d39b01573e9607a73ad`.
- HEAD is a no-op recertification over clean repair commit `558b3868620375df917891c4202eae695d1c9eba`; GitHub compare reports one commit ahead and zero files changed.
- SYNTHETIC `871def531b0f1222e6a1e61252af700f4ed204e3`; parent order MUST be BASE then HEAD and tree MUST equal HEAD tree.
- R62G target blob `bcc95c5b8c57cee26f0a5680dba5fd1399e08ef0`.
- R62N target blob `4e70b47730cf3b67ea9be65a95490ada23651a36`.
- Immutable full-closure oracle blob `249caa1504e2b62277a9389dc7e73bcabf12e7db`.
- BASE→HEAD: 277 ahead, 0 behind, merge-base BASE; docs/tests only; no `src/qore` delta.
- Required native exact-head QORE CI is run `33260165867` / job `99120615940`, completed SUCCESS on synthetic `871def531b...`: Ruff clean, Mypy 740 source files, 4862 collected/passed tests, 7 warnings, TOTAL coverage 87%. Independently inspect authoritative evidence before adjudication.

## Your prior C3 finding — must remain fixed
C3 correctly invalidated old HEAD `858510a...` with `R62N-F1` CRITICAL: a known plain exception entering a `try/except*` could be treated as an empty group, creating an impossible normal successor and hiding an outer dangerous call.

Old minimal witness:
```python
b = eval
try:
    try:
        raise ValueError("v")
    except* TypeError:
        pass
except ValueError:
    result = b("1+1")
```
CPython result is 2 and the outer call is reachable/dangerous.

The current R62N model maps a known plain exception to a logical singleton member for TryStar matching while retaining ExceptionGroup/BaseExceptionGroup semantics. Re-falsify nonmatching/matching siblings, outer ordinary and star handlers, nested groups, pending handler exceptions, bare re-raise, subgroup remainder, `else`/`finally`, and namespace sequencing. Permanent current R62N suite is 38/38 on the repaired tree, but that is evidence to attack, not certification.

## R88 R62G finding — current additional correction
DeepSeek Expert R88 invalidated the subsequent freeze with a valid deterministic R62G false positive: explicitly imported `builtins` is a Python module, not a mapping. For example:
```python
import builtins
result = builtins["eval"]("1+1")
```
CPython raises `TypeError` before dynamic execution, so the current scanner must not claim an executed dangerous `call:` for this module-mapping misuse. Attribute-style `.get` / `.__getitem__` on the module analogously fail with `AttributeError`.

The correction deliberately does NOT generalize this to real mappings: `builtins.__dict__`, `vars(builtins)`, and mapping-valued `__builtins__` remain executable routes and must stay detected. Valid attribute routes such as `builtins.eval` / `getattr(builtins, "eval")` also remain dangerous.

A free adversarial falsification of the first repair discovered transported module identity was initially too syntactic: `(builtins,)[0]["eval"](...)` still false-positived. That predecessor was rejected. The current R62G implementation distinguishes the builtins module by abstract value and propagates that identity through relevant tuple/list/index/alias transport. Containers themselves are not collapsed to definitely-module, preventing unsafe suppression of module↔mapping unions.

Attack this current implementation aggressively with NEW witnesses: aliases, nested tuple/list/dict/set carriers, starred unpacking, BoolOp/IfExp/NamedExpr joins, assignment/rebinding/deletion/shadowing, comprehensions/deferred scopes, closures/defaults, custom objects, side-effecting receiver/key expressions, `getattr`/attrgetter, `.get`, `.__getitem__`, `operator.getitem`, `operator.itemgetter`, `__dict__`, `vars`, `globals`/`locals`, real `__builtins__` module-vs-dict contexts, and unions mixing module and mapping. Compare actual CPython reachability/result against scanner markers. Binding provenance alone is not an executed-call claim. A constructible dangerous route with no required marker is material; a deterministic runtime-safe route claimed as executed danger is material when a bounded sound correction exists.

## UMI closure
Independently inspect current complete D04 owner/qualification universe and all final-owner/full-closure guards. Verify `src/qore=0`, no staging artifacts, all 19 Program-D family UMI-02 bindings, provider/listing vs economic identity separation, anti-flattening of RATE/YIELD/SPREAD/PRICE/NAV/IV/NOTIONAL/QUANTITY/WEIGHT, generic/product qualification directionality, Sukuk/Shari'ah, ILS/event, SFT state/terms, SCF/Advanced-Payable non-collision, provider/runtime/network/dynamic-execution exclusions, determinism/immutability/secret-free specimens and unchanged historical oracle.

No provider support, operational support, execution, valuation-methodology, Production or real-capital readiness may be inferred.

For every material finding provide exact location, minimal witness, CPython result, scanner output, severity and smallest bounded correction. If binding or QG is mechanically invalid, report `MECHANICAL REVIEW FAILURE`. If any material semantic finding survives, end `VALIDACIÓN NO OK`. Only if no material finding survives end literally:

HALLAZGOS: NINGUNO
VALIDACIÓN OK
