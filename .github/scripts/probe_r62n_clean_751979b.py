from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

REVIEWER = Path.cwd()
CORE = REVIEWER / "core"


def _heredoc(path: str) -> str:
    lines = (REVIEWER / path).read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if "python - <<'PY'" in line) + 1
    end = next(i for i in range(start, len(lines)) if lines[i].strip() == "PY")
    return textwrap.dedent("\n".join(lines[start:end]))


def _run(label: str, script: str) -> None:
    print(f"=== {label} ===", flush=True)
    subprocess.run([sys.executable, "-c", script], cwd=CORE, check=True)


_run("historical-current-freeze-payload", _heredoc(".github/workflows/probe-r62n-current-freeze.yml"))
_run("historical-star-nested-final-payload", _heredoc(".github/workflows/probe-r62n-star-nested-final.yml"))

fresh = r'''
import importlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path("tests/infrastructure").resolve()))
n = importlib.import_module("test_universal_cross_asset_conformance_final_owner_r62n_guards")

def check(label: str, source: str, expected_runtime: int, call_line: int, dangerous: bool) -> None:
    runtime = n._runtime_result(source)
    markers = n._r62n_dynamic_execution_markers_from_source(source)
    marker = f"call:{call_line}"
    print(label, "runtime=", runtime, "markers=", markers)
    assert runtime == expected_runtime
    assert (marker in markers) is dangerous, (label, marker, markers)

check("static_cross_handler_safe", '''\
b = eval
try:
    raise ExceptionGroup("eg", [AttributeError("a"), ValueError("v")])
except* AttributeError:
    b = len
except* ValueError:
    result = b("1+1")
''', 3, 7, False)
check("static_cross_handler_danger", '''\
b = len
try:
    raise ExceptionGroup("eg", [AttributeError("a"), ValueError("v")])
except* AttributeError:
    b = eval
except* ValueError:
    result = b("1+1")
''', 2, 7, True)
check("final_chain_safe", '''\
b = eval
try:
    raise ExceptionGroup("eg", [AttributeError("a"), ValueError("v")])
except* AttributeError:
    b = eval
except* ValueError:
    b = len
finally:
    result = b("1+1")
''', 3, 9, False)
check("final_chain_danger", '''\
b = len
try:
    raise ExceptionGroup("eg", [AttributeError("a"), ValueError("v")])
except* AttributeError:
    b = len
except* ValueError:
    b = eval
finally:
    result = b("1+1")
''', 2, 9, True)
'''
_run("fresh-static-sequencing-inversions", fresh)
