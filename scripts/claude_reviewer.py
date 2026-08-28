#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5")
MAX_TOKENS = int(os.environ.get("CLAUDE_MAX_TOKENS", "32000"))
MAX_ROUNDS = int(os.environ.get("CLAUDE_MAX_ROUNDS", "8"))
QORE_ROOT = Path(os.environ["QORE_ROOT"]).resolve()
PROMPT_PATH = Path(os.environ["PROMPT_PATH"]).resolve()
OUTPUT_PATH = Path(os.environ.get("REVIEW_OUTPUT", "claude-review.md")).resolve()
EXPECTED_BASE = os.environ["EXPECTED_BASE"]
EXPECTED_HEAD = os.environ["EXPECTED_HEAD"]
PACKAGE_ID = os.environ["PACKAGE_ID"]
API_KEY = os.environ["ANTHROPIC_API_KEY"]


def _inside_root(relative: str) -> Path:
    path = (QORE_ROOT / relative).resolve()
    if path != QORE_ROOT and QORE_ROOT not in path.parents:
        raise ValueError("path escapes QORE_ROOT")
    return path


def _clip(text: str, limit: int = 40000) -> str:
    if len(text) <= limit:
        return text
    half = limit // 2
    return text[:half] + "\n...[CLIPPED]...\n" + text[-half:]


def _run(args: list[str], *, cwd: Path | None = None, input_text: str | None = None) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=90,
    )
    return f"EXIT={completed.returncode}\n{completed.stdout}"


def read_file(args: dict[str, Any]) -> str:
    relative = str(args.get("path", ""))
    start = max(1, int(args.get("start_line", 1)))
    end = max(start, int(args.get("end_line", start + 399)))
    end = min(end, start + 999)
    path = _inside_root(relative)
    if not path.is_file():
        return "ERROR: file not found"
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    selected = lines[start - 1 : end]
    return _clip("\n".join(f"{i}: {line}" for i, line in enumerate(selected, start=start)))


def search_text(args: dict[str, Any]) -> str:
    query = str(args.get("query", ""))
    if not query:
        return "ERROR: empty query"
    relative = str(args.get("path", "."))
    _inside_root(relative)
    result = _run(
        ["git", "grep", "-n", "-I", "-F", "--", query, "--", relative],
        cwd=QORE_ROOT,
    )
    return _clip(result, 30000)


def git_diff(args: dict[str, Any]) -> str:
    relative = str(args.get("path", ""))
    cmd = ["git", "diff", "--no-ext-diff", EXPECTED_BASE, EXPECTED_HEAD]
    if relative:
        _inside_root(relative)
        cmd.extend(["--", relative])
    return _clip(_run(cmd, cwd=QORE_ROOT), 50000)


_SCANNERS = {
    "r62f": (
        "test_universal_cross_asset_conformance_final_owner_r62f_guards",
        "_r62f_dynamic_execution_markers_from_source",
    ),
    "r62g": (
        "test_universal_cross_asset_conformance_final_owner_r62g_guards",
        "_r62g_dynamic_execution_markers_from_source",
    ),
    "r62j": (
        "test_universal_cross_asset_conformance_final_owner_r62j_guards",
        "_r62j_dynamic_execution_markers_from_source",
    ),
    "r62k": (
        "test_universal_cross_asset_conformance_final_owner_r62k_guards",
        "_r62k_dynamic_execution_markers_from_source",
    ),
}


def scanner_probe(args: dict[str, Any]) -> str:
    scanner = str(args.get("scanner", ""))
    source = str(args.get("source", ""))
    if scanner not in _SCANNERS:
        return "ERROR: unsupported scanner"
    if len(source) > 16000:
        return "ERROR: source too large"
    module, symbol = _SCANNERS[scanner]
    helper = (
        "import importlib,sys\n"
        "from pathlib import Path\n"
        "root=Path(sys.argv[1])\n"
        "sys.path.insert(0,str(root/'tests'/'infrastructure'))\n"
        "m=importlib.import_module(sys.argv[2])\n"
        "fn=getattr(m,sys.argv[3])\n"
        "src=sys.stdin.read()\n"
        "print(repr(fn(src)))\n"
    )
    return _run(
        [sys.executable, "-I", "-c", helper, str(QORE_ROOT), module, symbol],
        cwd=QORE_ROOT,
        input_text=source,
    )


def list_changed_files(_: dict[str, Any]) -> str:
    return _clip(
        _run(["git", "diff", "--name-status", EXPECTED_BASE, EXPECTED_HEAD], cwd=QORE_ROOT),
        30000,
    )


TOOLS = [
    {
        "name": "read_file",
        "description": "Read a bounded line range from the exact frozen qore-core checkout. Read-only.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer", "minimum": 1},
                "end_line": {"type": "integer", "minimum": 1},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
    {
        "name": "search_text",
        "description": "Literal git-grep in the exact frozen qore-core checkout. Read-only.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "path": {"type": "string"}},
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "git_diff",
        "description": "Read the frozen BASE-to-HEAD unified diff, optionally limited to one path. Read-only.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "additionalProperties": False,
        },
    },
    {
        "name": "list_changed_files",
        "description": "List exact BASE-to-HEAD changed files and statuses. Read-only.",
        "strict": True,
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "scanner_probe",
        "description": "Run a supported frozen QORE static scanner on supplied source without executing that source.",
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "scanner": {"type": "string", "enum": ["r62f", "r62g", "r62j", "r62k"]},
                "source": {"type": "string"},
            },
            "required": ["scanner", "source"],
            "additionalProperties": False,
        },
    },
]

TOOL_HANDLERS = {
    "read_file": read_file,
    "search_text": search_text,
    "git_diff": git_diff,
    "list_changed_files": list_changed_files,
    "scanner_probe": scanner_probe,
}

_NAMED_EXPR = (
    "import builtins\n"
    "def run():\n"
    "    return globals()['b'].eval('1+1')\n"
    "result = ((b := builtins), run())[1]\n"
    "print(result)\n"
)
_TRANSIENT = (
    "def run():\n"
    "    return globals()['b'].eval('1+1')\n"
    "import builtins as b\n"
    "b = len\n"
    "try:\n"
    "    result = run()\n"
    "except AttributeError:\n"
    "    result = 3\n"
    "print(result)\n"
)
_DANGEROUS = (
    "def run():\n"
    "    return globals()['b'].eval('1+1')\n"
    "import builtins as b\n"
    "result = run()\n"
    "b = len\n"
    "print(result)\n"
)


def mandatory_evidence() -> str:
    probes = {
        "runtime_namedexpr_same_statement": _run([sys.executable, "-I", "-c", _NAMED_EXPR], cwd=QORE_ROOT),
        "scanner_r62k_namedexpr_same_statement": scanner_probe({"scanner": "r62k", "source": _NAMED_EXPR}),
        "runtime_transient_rebound": _run([sys.executable, "-I", "-c", _TRANSIENT], cwd=QORE_ROOT),
        "scanner_r62j_transient_rebound": scanner_probe({"scanner": "r62j", "source": _TRANSIENT}),
        "scanner_r62k_transient_rebound": scanner_probe({"scanner": "r62k", "source": _TRANSIENT}),
        "runtime_dangerous_direct": _run([sys.executable, "-I", "-c", _DANGEROUS], cwd=QORE_ROOT),
        "scanner_r62k_dangerous_direct": scanner_probe({"scanner": "r62k", "source": _DANGEROUS}),
    }
    return json.dumps(probes, indent=2, sort_keys=True)


def call_api(messages: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": 0,
        "messages": messages,
        "tools": TOOLS,
        "tool_choice": {"type": "auto", "disable_parallel_tool_use": False},
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "content-type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": API_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=900) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Anthropic HTTP {exc.code}: {detail}") from exc


def main() -> int:
    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    binding = _run(
        ["git", "show", "-s", "--format=HEAD=%H%ntree=%T", EXPECTED_HEAD],
        cwd=QORE_ROOT,
    )
    changed = list_changed_files({})
    evidence = mandatory_evidence()
    user_text = (
        prompt
        + "\n\n## MACHINE-VERIFIED FROZEN CONTEXT\n"
        + binding
        + "\n\nCHANGED FILES:\n"
        + changed
        + "\n\nMANDATORY RAW EXECUTABLE EVIDENCE:\n"
        + evidence
        + "\n\nUse the read-only tools to investigate independently before finalizing. "
        + "Do not treat prior reviewer verdicts as authority."
    )
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]
    usage_totals = {"input_tokens": 0, "output_tokens": 0}
    final_text = ""

    for _round in range(MAX_ROUNDS):
        response = call_api(messages)
        usage = response.get("usage") or {}
        usage_totals["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
        usage_totals["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
        content = response.get("content") or []
        messages.append({"role": "assistant", "content": content})
        stop_reason = response.get("stop_reason")

        if stop_reason == "tool_use":
            tool_results = []
            for block in content:
                if block.get("type") != "tool_use":
                    continue
                name = str(block.get("name", ""))
                handler = TOOL_HANDLERS.get(name)
                try:
                    result = handler(block.get("input") or {}) if handler else "ERROR: unknown tool"
                    is_error = False
                except Exception as exc:  # bounded tool errors become evidence
                    result = f"ERROR: {type(exc).__name__}: {exc}"
                    is_error = True
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": _clip(result),
                        "is_error": is_error,
                    }
                )
            if not tool_results:
                final_text = "MECHANICAL REVIEW FAILURE: tool_use stop without client tool call."
                break
            messages.append({"role": "user", "content": tool_results})
            continue

        text_blocks = [str(block.get("text", "")) for block in content if block.get("type") == "text"]
        final_text = "\n".join(text_blocks).strip()
        if stop_reason == "end_turn" and final_text:
            break
        final_text = (
            f"MECHANICAL REVIEW FAILURE: Claude stop_reason={stop_reason!r}; "
            "no authoritative final review produced."
        )
        break
    else:
        final_text = "MECHANICAL REVIEW FAILURE: Claude exceeded bounded tool rounds."

    usage_comment = (
        "\n\n<!-- QORE-CLAUDE-USAGE "
        + json.dumps({"model": MODEL, **usage_totals}, sort_keys=True, separators=(",", ":"))
        + " -->\n"
    )
    OUTPUT_PATH.write_text(final_text.rstrip() + usage_comment, encoding="utf-8")
    print(f"Claude review written to {OUTPUT_PATH}")
    print(json.dumps({"package_id": PACKAGE_ID, "model": MODEL, **usage_totals}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
