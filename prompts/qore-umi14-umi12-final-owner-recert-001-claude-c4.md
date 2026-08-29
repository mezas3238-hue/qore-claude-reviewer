# Claude C4 — QORE UMI14 / UMI12 final owner recertification

Act as the final independent adversarial reviewer of qore-core PR #461. Do not inherit any prior DeepSeek or Claude verdict. GitHub live bindings, exact checkout, CPython 3.12 behavior and reproducible evidence are authoritative.

## Exact corrected freeze
- BASE `ebd0adf000874797653df92ea1c08a892cce6c8c`, tree `08ce942dd944a2c02a1aa9971dbfbe011def919d`.
- HEAD `7d16609795e99052db66281749aefe406172f870`, tree `a028e374934a0587e6988bba08e3b4a04b1feaca`.
- SYNTHETIC `d55cee13735d1c50bb63cf43fb34e97385b8d138`; parent order MUST be BASE then HEAD and tree MUST equal HEAD tree.
- R62N target blob `4e70b47730cf3b67ea9be65a95490ada23651a36`.
- Immutable full-closure oracle blob `249caa1504e2b62277a9389dc7e73bcabf12e7db`.
- BASE→HEAD: 269 ahead, 0 behind, merge-base BASE; no `src/qore` delta.
- Exact required QORE CI run `33256530716`, job `99111137157` must be completed SUCCESS before adjudication.

## Your prior C3 finding
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

## Corrected semantics to re-falsify from scratch
The scanner now maps a known plain exception to a logical singleton member for TryStar matching, while retaining true ExceptionGroup/BaseExceptionGroup member semantics. It must not manufacture normal continuation for a nonmatching plain exception, and it must still route matching plain exceptions precisely through current/later sibling `except*` handlers.

Independent no-model evidence on exact HEAD passed six adversarial plain-exception cases: your exact C3 witness, safe inverse, direct matching safe/danger `finally`, later-sibling matching safe/danger; then permanent R62N suite passed 38/38. This is evidence to attack, not certification.

Construct NEW witnesses that vary exception hierarchy and grouping: ValueError/Exception/BaseException subclasses, tuple handlers, aliases/shadowing, ExceptionGroup/BaseExceptionGroup, nested groups, current/later/no sibling matching, outer ordinary `except`, outer `except*`, nested TryStar, `else` and `finally`, explicit raise, bare raise, pending handler exceptions, subgroup remainder and mixed re-raise+new exception. Check namespace state and dynamic eval/exec/__import__ reachability against real CPython.

Also attack the broader R62N scanner for control-flow-induced false negatives: with/async-with where applicable, loops, returns/break/continue, comprehensions/generators, BoolOp/IfExp, imports/star imports, lexical/deferred scopes, aliases and indirect dynamic execution. A reproducible runtime-dangerous path with no call marker is material. A deterministic safe path marked dangerous is material where exactness is part of the contract and a bounded sound correction is available.

## UMI closure
Independently inspect current complete D04 owner/qualification universe and all final-owner/full-closure guards. Verify `src/qore=0`, no staging artifacts, 19 Program-D family UMI-02 binding, provider/listing vs economic identity separation, anti-flattening of RATE/YIELD/SPREAD/PRICE/NAV/IV/NOTIONAL/QUANTITY/WEIGHT, generic/product qualification directionality, Sukuk/Shari'ah, ILS/event, SFT state/terms, SCF/Advanced-Payable non-collision, provider/runtime/network/dynamic-execution exclusions, determinism/immutability/secret-free specimens and unchanged historical oracle.

No provider support, operational support, execution, valuation-methodology, Production or real-capital readiness may be inferred.

For every material finding provide exact location, minimal witness, CPython result, scanner output, severity and smallest bounded correction. If binding or QG is mechanically invalid, report `MECHANICAL REVIEW FAILURE`. If any material semantic finding survives, end `VALIDACIÓN NO OK`. Only if no material finding survives end literally:

HALLAZGOS: NINGUNO
VALIDACIÓN OK
