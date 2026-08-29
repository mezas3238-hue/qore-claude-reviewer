# Claude C5 — QORE UMI14 / UMI12 final owner recertification

Act as the final independent adversarial reviewer of qore-core PR #461. Do not inherit any DeepSeek or prior Claude verdict. GitHub live bindings, the exact frozen checkout, CPython 3.12 behavior, and reproducible evidence are authoritative. This is a fresh package; do not reuse C3 or the never-dispatched C4.

## Exact frozen target

- BASE `ebd0adf000874797653df92ea1c08a892cce6c8c`, tree `08ce942dd944a2c02a1aa9971dbfbe011def919d`.
- HEAD `476a93cdd08a064d0b99a139cd1b49287b937f21`, tree `5e2b37b23b01fe23fd373d39b01573e9607a73ad`.
- SYNTHETIC `871def531b0f1222e6a1e61252af700f4ed204e3`; parents must be BASE then HEAD and its tree must equal the HEAD tree.
- PR must remain OPEN, DRAFT, unmerged and mergeable; base branch must remain `main`.
- BASE→HEAD is 277 commits ahead, 0 behind, merge-base BASE, and has zero `src/qore` changed files.
- R62G target blob `bcc95c5b8c57cee26f0a5680dba5fd1399e08ef0`.
- R62N target blob `4e70b47730cf3b67ea9be65a95490ada23651a36`.
- Immutable full-closure oracle blob `249caa1504e2b62277a9389dc7e73bcabf12e7db`; it must be byte-identical.

The exact native QORE CI binding is run `33260165867` / job `99120615940`, completed SUCCESS for HEAD `476a93c...` and synthetic `871def531b...`: Ruff PASS, Mypy PASS over 740 source files, 4862 passed, 7 warnings, TOTAL coverage 87%. Treat this as supplied quality evidence and independently falsify semantics.

## Serial-gate context, not authority

Fresh DeepSeek Expert R92 (run `33269245726`, job `99144638627`) and fresh DeepSeek Coder R93 (run `33269515784`, job `99145356939`) each ended `HALLAZGOS: NINGUNO / VALIDACIÓN OK` on this same freeze. Their verdicts do not transfer authority to you.

## R62N: prior C3 material finding must remain fixed

Claude C3 correctly invalidated old HEAD `858510a...`: a known plain exception entering `try/except*` could be modeled as an empty group, creating an impossible normal successor and hiding an outer reachable dangerous call.

Minimal prior witness:

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

CPython result is 2. The current R62N model maps a known plain exception to a logical singleton member for TryStar matching while retaining ExceptionGroup/BaseExceptionGroup behavior. Re-falsify matching/nonmatching siblings, outer ordinary and star handlers, nested groups, pending handler exceptions, bare re-raise, subgroup remainder, `else`/`finally`, and namespace sequencing. The permanent R62N suite is evidence to attack, not certification.

## R62G: distinguish receiver type from runtime context

The safe case is an explicitly imported module receiver:

```python
import builtins
result = builtins["eval"]("1+1")
```

CPython raises `TypeError: 'module' object is not subscriptable` before eval. R62G must not fabricate an executed `call:` marker.

Executable cases must remain detected, including:

```python
import builtins
result = builtins.__dict__["eval"]("1+1")
```

and an explicit mapping-valued `__builtins__`:

```python
__builtins__ = {"eval": eval}
result = __builtins__["eval"]("1+1")
```

Also retain detection for `builtins.eval`, `vars(builtins)["eval"]`, `getattr(builtins, "eval")`, mapping aliases/transports, and conservative module↔mapping unions.

### Why R90 must not be repeated as a context-blind finding

DeepSeek R90 used these different sources:

```python
result = globals()["__builtins__"]["eval"]("1+1")
print(result)
```

```python
from builtins import __dict__ as namespace
result = namespace["globals"]()["__builtins__"]["eval"]("1+1")
print(result)
```

Those witnesses are context-sensitive. Under exact `python -I -B -c`, `__main__.__builtins__` is the module and they raise TypeError. Under normal imported-module / fresh-globals-`exec` context, `__builtins__` is a dict and both execute eval, producing 2. A static scanner marker is therefore sound unless the scanner has established a definitely-module receiver.

The R90 contradiction was independently classified as `REVIEWER INFRA / EVIDENCE ROUTING DEFECT`: direct R62G and the evidence-builder scanner were byte-for-byte equal; the evidence paired a single `-c` runtime context with sources executable in an imported-module context. DeepSeek reviewer guard run `33268987310` / job `99143953465` passed after the evidence correction.

Claude's free exact-HEAD context guard run `33269894582` / job `99146383037` also passed:

- explicit imported-module subscript source SHA-256 `1037a5d5f2a36e6c786c3f16e8f594a33bc28ade1ee6e149a88b8ee353c3fcea`: TypeError in both contexts, R62G `()`;
- `builtins.__dict__` source SHA-256 `d601e32ccd3ffa39bb9e20711d91f94378c9b9d627f315dfb17e2f02c25f0b4d`: result 2 in both, R62G `('call:2',)`;
- explicit mapping source SHA-256 `036fffa141f5fb27154423884530aee9132091c15d12e38bb5e200eaae6c86a4`: result 2 in both, R62G `('binding:1', 'call:2')`;
- the two context-sensitive witnesses raise TypeError under `-c`, produce 2 under imported-module context, and retain `call:` markers.

The mandatory evidence attached to this package binds scanner and runtime observations to identical source bytes and labels both execution contexts. Inspect it, then attempt new counterexamples. Do not accept either CI green or this explanation without falsification.

Attack aliases, tuple/list/dict/set carriers, unpacking, BoolOp/IfExp/NamedExpr joins, rebinding/deletion/shadowing, comprehensions and deferred scopes, closures/defaults, custom receivers, side effects, `.get`, `.__getitem__`, `operator.getitem`, `operator.itemgetter`, `__dict__`, `vars`, `globals`/`locals`, module-vs-dict contexts, and module↔mapping unions. Binding provenance alone is not an executed-call claim.

## UMI closure

Independently inspect the complete D04 owner/qualification universe and all final-owner/full-closure guards. Verify zero `src/qore` delta, no staging artifacts, all 19 Program-D family UMI-02 bindings, provider/listing versus economic identity separation, anti-flattening of RATE/YIELD/SPREAD/PRICE/NAV/IV/NOTIONAL/QUANTITY/WEIGHT, generic/product qualification directionality, Sukuk/Shari'ah, ILS/event, SFT state/terms, SCF/Advanced-Payable non-collision, provider/runtime/network/dynamic-execution exclusions, determinism/immutability/secret-free specimens, and unchanged historical oracle.

Do not infer provider support, operational support, execution, valuation methodology, Production readiness, or authorization for real capital.

For every material finding provide exact location, a minimal witness, CPython result, scanner output, severity, and the smallest bounded correction. If live binding or evidence generation is mechanically invalid, report `MECHANICAL REVIEW FAILURE`. If any material semantic finding survives, end `VALIDACIÓN NO OK`. Only if no material finding survives end literally:

HALLAZGOS: NINGUNO
VALIDACIÓN OK
