# Claude C6 — QORE UMI14 / UMI12 final owner recertification

Act as the final independent adversarial semantic reviewer of qore-core PR #461. This is a fresh package. Do not inherit DeepSeek verdicts, prior Claude verdicts, or the mechanically rejected C5 result.

## Deliberate trust and tool boundary

Your session is intentionally read-only and has no Bash, git, gh, network, WebFetch, or WebSearch. That is not a defect and is not grounds for `MECHANICAL REVIEW FAILURE`.

Before invoking you, the workflow itself has already:

1. queried the live PR and matched state, BASE, HEAD, and SYNTHETIC;
2. checked out the exact frozen HEAD;
3. verified synthetic parent order and tree equality;
4. executed the mandatory CPython/scanner matrix from that checkout; and
5. appended the generated evidence below this prompt.

After you finish, the workflow will verify that the checkout and live HEAD remain unchanged. Treat those workflow-produced observations as the mechanical evidence layer. Your independent authority is semantic: inspect the exact checkout with the available read/search tools, trace the implementation, challenge the supplied matrix, and construct new counterexamples.

Do not claim you were asked to query GitHub or re-run Python yourself. If you discover a candidate outside the mandatory matrix, give its exact minimal source and predicted CPython/scanner behavior; the Integration Authority will reproduce it before adjudication. Report `MECHANICAL REVIEW FAILURE` only if the workflow evidence is missing, internally inconsistent, bound to the wrong freeze, or the exact checkout cannot be read.

## Exact frozen target

- BASE `ebd0adf000874797653df92ea1c08a892cce6c8c`, tree `08ce942dd944a2c02a1aa9971dbfbe011def919d`.
- HEAD `476a93cdd08a064d0b99a139cd1b49287b937f21`, tree `5e2b37b23b01fe23fd373d39b01573e9607a73ad`.
- SYNTHETIC `871def531b0f1222e6a1e61252af700f4ed204e3`, with parents BASE then HEAD and tree equal to HEAD.
- BASE→HEAD: 277 ahead, 0 behind, merge-base BASE; zero `src/qore` changed files.
- R62G target blob `bcc95c5b8c57cee26f0a5680dba5fd1399e08ef0`.
- R62N target blob `4e70b47730cf3b67ea9be65a95490ada23651a36`.
- Immutable full-closure oracle blob `249caa1504e2b62277a9389dc7e73bcabf12e7db`.
- Native QORE CI run `33260165867` / job `99120615940`: SUCCESS; Ruff PASS, Mypy PASS over 740 source files, 4862 passed, 7 warnings, TOTAL coverage 87%.

The workflow-produced evidence below independently restates the exact checkout/tree/blob observations and runtime/scanner results.

## R62N: prior material defect must remain fixed

A prior freeze mishandled a known plain exception entering `try/except*`, allowing an impossible normal successor and hiding an outer reachable dangerous call:

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

CPython reaches the outer handler and produces 2. The current model maps a known plain exception to a logical singleton member for TryStar matching while preserving ExceptionGroup/BaseExceptionGroup semantics.

Trace and attack matching/nonmatching sibling handlers, outer ordinary/star handlers, nested groups, pending handler exceptions, bare re-raise, subgroup remainder, `else`/`finally`, and namespace sequencing. A permanent green suite is evidence, not certification.

## R62G: receiver type and runtime context are separate facts

Definitely safe:

```python
import builtins
result = builtins["eval"]("1+1")
```

The explicitly imported `builtins` receiver is a module in every relevant context, so CPython raises TypeError before eval and R62G must not emit an executed `call:` marker.

Dangerous and required to remain detected:

```python
import builtins
result = builtins.__dict__["eval"]("1+1")
```

```python
__builtins__ = {"eval": eval}
result = __builtins__["eval"]("1+1")
```

Also retain detection for `builtins.eval`, `vars(builtins)["eval"]`, `getattr(builtins, "eval")`, mapping aliases/transports, and conservative module↔mapping unions.

These different witnesses are context-sensitive:

```python
result = globals()["__builtins__"]["eval"]("1+1")
print(result)
```

```python
from builtins import __dict__ as namespace
result = namespace["globals"]()["__builtins__"]["eval"]("1+1")
print(result)
```

They raise TypeError when run directly as `python -I -B -c`, because `__main__.__builtins__` is a module. They execute eval and produce 2 in an imported-module / fresh-globals-`exec` context, where `__builtins__` is a dict. Therefore a static `call:` marker is sound unless analysis proves a definitely-module receiver.

The mandatory evidence binds scanner and runtime observations to identical source SHA-256 values and labels both contexts. Challenge it with new aliases, containers, unpacking, BoolOp/IfExp/NamedExpr joins, rebinding/deletion/shadowing, comprehensions/deferred scopes, closures/defaults, custom receivers, side effects, `.get`, `.__getitem__`, `operator.getitem`, `operator.itemgetter`, `__dict__`, `vars`, `globals`/`locals`, and module↔mapping unions. Binding provenance alone is not an executed-call claim.

## UMI closure

Independently inspect the complete D04 owner/qualification universe and final-owner/full-closure guards. Verify zero `src/qore` delta, no staging artifacts, all 19 Program-D family UMI-02 bindings, provider/listing versus economic identity separation, anti-flattening of RATE/YIELD/SPREAD/PRICE/NAV/IV/NOTIONAL/QUANTITY/WEIGHT, generic/product qualification directionality, Sukuk/Shari'ah, ILS/event, SFT state/terms, SCF/Advanced-Payable non-collision, provider/runtime/network/dynamic-execution exclusions, determinism/immutability/secret-free specimens, and the unchanged historical oracle.

Do not infer provider support, operational support, execution, valuation methodology, Production readiness, or authorization for real capital.

For every material finding provide exact location, minimal witness, predicted CPython result, predicted scanner output, severity, and smallest bounded correction. If any material semantic finding survives, end literally `VALIDACIÓN NO OK`. Only if no material finding survives, end with exactly these final two lines:

HALLAZGOS: NINGUNO
VALIDACIÓN OK
