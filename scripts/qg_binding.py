#!/usr/bin/env python3
"""Fail-closed binding of a Claude package to one authoritative QORE CI job."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class BindingError(ValueError):
    """The supplied Quality Gate evidence does not match the frozen package."""


@dataclass(frozen=True)
class ExpectedSummary:
    ruff_passed: bool
    mypy_source_files: int
    pytest_collected: int
    pytest_passed: int
    pytest_warnings: int
    coverage_total_statements: int
    coverage_missed_statements: int
    coverage_percent: int


@dataclass(frozen=True)
class QualitySummary:
    ruff_passed: bool
    mypy_source_files: int
    pytest_collected: int
    pytest_passed: int
    pytest_warnings: int
    coverage_total_statements: int
    coverage_missed_statements: int
    coverage_percent: int


@dataclass(frozen=True)
class VerifiedBinding:
    run_id: int
    job_id: int
    head_sha: str
    synthetic_sha: str
    summary: QualitySummary


_EXPECTED_KEYS = frozenset(
    {
        "ruff_passed",
        "mypy_source_files",
        "pytest_collected",
        "pytest_passed",
        "pytest_warnings",
        "coverage_total_statements",
        "coverage_missed_statements",
        "coverage_percent",
    }
)
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_TIMESTAMP_RE = re.compile(
    r"^\ufeff?\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z "
)


def _strict_int(value: object, label: str, *, minimum: int) -> int:
    if type(value) is not int or value < minimum:
        raise BindingError(f"{label} must be an integer >= {minimum}")
    return value


def parse_expected_summary(raw: str) -> ExpectedSummary:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BindingError("expected QG summary must be valid JSON") from exc
    if type(payload) is not dict or set(payload) != _EXPECTED_KEYS:
        raise BindingError(
            "expected QG summary must contain exactly: "
            + ", ".join(sorted(_EXPECTED_KEYS))
        )
    if payload["ruff_passed"] is not True:
        raise BindingError("ruff_passed must be the JSON boolean true")
    summary = ExpectedSummary(
        ruff_passed=True,
        mypy_source_files=_strict_int(
            payload["mypy_source_files"], "mypy_source_files", minimum=1
        ),
        pytest_collected=_strict_int(
            payload["pytest_collected"], "pytest_collected", minimum=1
        ),
        pytest_passed=_strict_int(
            payload["pytest_passed"], "pytest_passed", minimum=1
        ),
        pytest_warnings=_strict_int(
            payload["pytest_warnings"], "pytest_warnings", minimum=0
        ),
        coverage_total_statements=_strict_int(
            payload["coverage_total_statements"],
            "coverage_total_statements",
            minimum=1,
        ),
        coverage_missed_statements=_strict_int(
            payload["coverage_missed_statements"],
            "coverage_missed_statements",
            minimum=0,
        ),
        coverage_percent=_strict_int(
            payload["coverage_percent"], "coverage_percent", minimum=0
        ),
    )
    if summary.pytest_collected != summary.pytest_passed:
        raise BindingError("expected full pytest gate must be all-pass")
    if summary.coverage_missed_statements > summary.coverage_total_statements:
        raise BindingError("expected coverage missed count exceeds statement count")
    if summary.coverage_percent > 100:
        raise BindingError("coverage_percent must be <= 100")
    return summary


def _normalized_lines(log_text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in log_text.splitlines():
        line = _TIMESTAMP_RE.sub("", raw_line)
        lines.append(_ANSI_RE.sub("", line).rstrip())
    return lines


def _run_step_window(lines: list[str], command: str) -> list[str]:
    marker = f"##[group]Run {command}"
    starts = [index for index, line in enumerate(lines) if line == marker]
    if len(starts) != 1:
        raise BindingError(
            f"authoritative log must contain exactly one {command!r} step; "
            f"found {len(starts)}"
        )
    start = starts[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("##[group]Run "):
            end = index
            break
    return lines[start:end]


def _single_match(
    lines: list[str], pattern: re.Pattern[str], label: str
) -> re.Match[str]:
    matches = [match for line in lines if (match := pattern.fullmatch(line))]
    if len(matches) != 1:
        raise BindingError(
            f"authoritative log must contain exactly one {label}; found {len(matches)}"
        )
    return matches[0]


def _bind_checkout_synthetic(lines: list[str], expected_synthetic: str) -> None:
    checkout = _run_step_window(lines, "actions/checkout@v4")
    command = "[command]/usr/bin/git log -1 --format=%H"
    indexes = [index for index, line in enumerate(checkout) if line == command]
    if len(indexes) != 1:
        raise BindingError(
            "checkout evidence must contain exactly one executed "
            f"git log command; found {len(indexes)}"
        )
    following = [line for line in checkout[indexes[0] + 1 :] if line]
    if not following:
        raise BindingError("checkout git log command has no output")
    if following[0] != expected_synthetic:
        raise BindingError(
            "checkout git log output mismatch: "
            f"expected {expected_synthetic!r}, got {following[0]!r}"
        )


def parse_quality_log(log_text: str, *, expected_synthetic: str) -> QualitySummary:
    lines = _normalized_lines(log_text)
    _bind_checkout_synthetic(lines, expected_synthetic)

    ruff = _run_step_window(lines, "ruff check .")
    if sum(line == "All checks passed!" for line in ruff) != 1:
        raise BindingError("Ruff step lacks its unique clean completion marker")

    mypy = _run_step_window(lines, "mypy src tests")
    mypy_match = _single_match(
        mypy,
        re.compile(r"Success: no issues found in (\d+) source files"),
        "Mypy success summary",
    )

    pytest = _run_step_window(
        lines, "pytest --cov=src/qore --cov-report=term-missing"
    )
    collected_match = _single_match(
        pytest, re.compile(r"collected (\d+) items"), "pytest collection summary"
    )
    coverage_match = _single_match(
        pytest,
        re.compile(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%"),
        "TOTAL coverage summary",
    )
    pytest_match = _single_match(
        pytest,
        re.compile(
            r"=+\s+(\d+) passed(?:, (\d+) warnings?)? in "
            r"\d+(?:\.\d+)?s(?: \([^)]*\))?\s+=+"
        ),
        "pytest pass/warnings summary",
    )

    summary = QualitySummary(
        ruff_passed=True,
        mypy_source_files=int(mypy_match.group(1)),
        pytest_collected=int(collected_match.group(1)),
        pytest_passed=int(pytest_match.group(1)),
        pytest_warnings=int(pytest_match.group(2) or 0),
        coverage_total_statements=int(coverage_match.group(1)),
        coverage_missed_statements=int(coverage_match.group(2)),
        coverage_percent=int(coverage_match.group(3)),
    )
    if summary.pytest_collected != summary.pytest_passed:
        raise BindingError(
            "full pytest gate is not all-pass: "
            f"collected={summary.pytest_collected}, passed={summary.pytest_passed}"
        )
    if summary.coverage_missed_statements > summary.coverage_total_statements:
        raise BindingError("TOTAL coverage missed count exceeds statement count")
    return summary


def _payload_int(payload: Mapping[str, Any], key: str, label: str) -> int:
    if key not in payload:
        raise BindingError(f"{label} is missing {key!r}")
    return _strict_int(payload[key], f"{label}.{key}", minimum=1)


def _require_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise BindingError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def verify_quality_binding(
    *,
    job_payload: Mapping[str, Any],
    run_payload: Mapping[str, Any],
    log_text: str,
    expected_run_id: int,
    expected_job_id: int,
    expected_head: str,
    expected_synthetic: str,
    expected_summary: ExpectedSummary,
) -> VerifiedBinding:
    expected_run_id = _strict_int(expected_run_id, "expected_run_id", minimum=1)
    expected_job_id = _strict_int(expected_job_id, "expected_job_id", minimum=1)
    for value, label in (
        (expected_head, "expected_head"),
        (expected_synthetic, "expected_synthetic"),
    ):
        if not _SHA_RE.fullmatch(value):
            raise BindingError(f"{label} must be a lowercase 40-hex SHA")
    if not isinstance(job_payload, Mapping):
        raise BindingError("job payload must be an object")
    if not isinstance(run_payload, Mapping):
        raise BindingError("run payload must be an object")

    _require_equal(_payload_int(job_payload, "id", "job"), expected_job_id, "job.id")
    _require_equal(
        _payload_int(job_payload, "run_id", "job"), expected_run_id, "job.run_id"
    )
    _require_equal(job_payload.get("name"), "quality", "job.name")
    _require_equal(job_payload.get("status"), "completed", "job.status")
    _require_equal(job_payload.get("conclusion"), "success", "job.conclusion")
    _require_equal(job_payload.get("head_sha"), expected_head, "job.head_sha")

    _require_equal(_payload_int(run_payload, "id", "run"), expected_run_id, "run.id")
    _require_equal(run_payload.get("status"), "completed", "run.status")
    _require_equal(run_payload.get("conclusion"), "success", "run.conclusion")
    _require_equal(run_payload.get("head_sha"), expected_head, "run.head_sha")

    actual = parse_quality_log(log_text, expected_synthetic=expected_synthetic)
    for label in _EXPECTED_KEYS:
        _require_equal(getattr(actual, label), getattr(expected_summary, label), label)

    return VerifiedBinding(
        run_id=expected_run_id,
        job_id=expected_job_id,
        head_sha=expected_head,
        synthetic_sha=expected_synthetic,
        summary=actual,
    )


def render_markdown(binding: VerifiedBinding) -> str:
    summary = binding.summary
    return "\n".join(
        [
            "## Authoritative qore-core Quality Gate binding",
            "",
            f"- Run: `{binding.run_id}` (`completed/success`; HEAD `{binding.head_sha}`)",
            f"- Job: `{binding.job_id}` (`quality`, `completed/success`; HEAD `{binding.head_sha}`)",
            f"- Executed synthetic: `{binding.synthetic_sha}` (checkout `git log -1 --format=%H`)",
            "- Ruff: `PASS` (`ruff check .`; unique `All checks passed!`)",
            f"- Mypy: `PASS` ({summary.mypy_source_files} source files)",
            "- Pytest: `PASS` "
            f"({summary.pytest_collected} collected; {summary.pytest_passed} passed; "
            f"{summary.pytest_warnings} warnings)",
            "- Coverage: `PASS` "
            f"(TOTAL {summary.coverage_total_statements} statements; "
            f"{summary.coverage_missed_statements} missed; {summary.coverage_percent}%)",
        ]
    )


def _load_object(path: Path, label: str) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BindingError(f"could not read {label} JSON") from exc
    if not isinstance(payload, dict):
        raise BindingError(f"{label} JSON must be an object")
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-json", type=Path, required=True)
    parser.add_argument("--run-json", type=Path, required=True)
    parser.add_argument("--job-log", type=Path, required=True)
    parser.add_argument("--expected-run-id", type=int, required=True)
    parser.add_argument("--expected-job-id", type=int, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-synthetic", required=True)
    parser.add_argument("--expected-summary-json", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        binding = verify_quality_binding(
            job_payload=_load_object(args.job_json, "job"),
            run_payload=_load_object(args.run_json, "run"),
            log_text=args.job_log.read_text(encoding="utf-8-sig"),
            expected_run_id=args.expected_run_id,
            expected_job_id=args.expected_job_id,
            expected_head=args.expected_head,
            expected_synthetic=args.expected_synthetic,
            expected_summary=parse_expected_summary(args.expected_summary_json),
        )
        rendered = render_markdown(binding) + "\n"
        args.output.write_text(rendered, encoding="utf-8")
    except (BindingError, OSError, UnicodeError) as exc:
        print(f"QG BINDING FAILURE: {exc}", file=sys.stderr)
        return 2
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
