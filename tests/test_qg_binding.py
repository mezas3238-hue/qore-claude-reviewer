from __future__ import annotations

import json
import sys
import unittest
from dataclasses import asdict, replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from qg_binding import (  # noqa: E402
    BindingError,
    ExpectedSummary,
    parse_expected_summary,
    verify_quality_binding,
)


HEAD = "b" * 40
SYNTHETIC = "a" * 40
RUN_ID = 8001
JOB_ID = 9001
EXPECTED = ExpectedSummary(
    ruff_passed=True,
    mypy_source_files=742,
    pytest_collected=4877,
    pytest_passed=4877,
    pytest_warnings=3,
    coverage_total_statements=48123,
    coverage_missed_statements=5775,
    coverage_percent=88,
)


def _line(value: str) -> str:
    return f"2026-08-29T20:00:00.0000000Z {value}"


def valid_log(*, warnings: int = 3) -> str:
    warning_fragment = f", {warnings} warnings" if warnings else ""
    return "\n".join(
        [
            _line("##[group]Run actions/checkout@v4"),
            _line("with:"),
            _line("##[endgroup]"),
            _line("[command]/usr/bin/git checkout --force refs/remotes/pull/999/merge"),
            _line("##[endgroup]"),
            _line("[command]/usr/bin/git log -1 --format=%H"),
            _line(SYNTHETIC),
            _line("##[group]Run actions/setup-python@v6"),
            _line("##[endgroup]"),
            _line("##[group]Run ruff check ."),
            _line("ruff check ."),
            _line("##[endgroup]"),
            _line("All checks passed!"),
            _line("##[group]Run mypy src tests"),
            _line("mypy src tests"),
            _line("##[endgroup]"),
            _line("Success: no issues found in 742 source files"),
            _line("##[group]Run pytest --cov=src/qore --cov-report=term-missing"),
            _line("pytest --cov=src/qore --cov-report=term-missing"),
            _line("##[endgroup]"),
            _line("collected 4877 items"),
            _line("TOTAL 48123 5775 88%"),
            _line(
                "================= 4877 passed"
                f"{warning_fragment} in 10.25s (0:00:10) ================="
            ),
            _line("Post job cleanup."),
        ]
    )


def job_payload() -> dict[str, object]:
    return {
        "id": JOB_ID,
        "run_id": RUN_ID,
        "name": "quality",
        "status": "completed",
        "conclusion": "success",
        "head_sha": HEAD,
    }


def run_payload() -> dict[str, object]:
    return {
        "id": RUN_ID,
        "status": "completed",
        "conclusion": "success",
        "head_sha": HEAD,
    }


class QualityBindingTests(unittest.TestCase):
    def verify(
        self,
        *,
        job: dict[str, object] | None = None,
        run: dict[str, object] | None = None,
        log: str | None = None,
        expected_run_id: int = RUN_ID,
        expected_job_id: int = JOB_ID,
        expected_head: str = HEAD,
        expected_synthetic: str = SYNTHETIC,
        expected: ExpectedSummary = EXPECTED,
    ):
        return verify_quality_binding(
            job_payload=job if job is not None else job_payload(),
            run_payload=run if run is not None else run_payload(),
            log_text=log if log is not None else valid_log(),
            expected_run_id=expected_run_id,
            expected_job_id=expected_job_id,
            expected_head=expected_head,
            expected_synthetic=expected_synthetic,
            expected_summary=expected,
        )

    def test_valid_binding_uses_head_metadata_and_synthetic_checkout(self) -> None:
        binding = self.verify()
        self.assertEqual(binding.head_sha, HEAD)
        self.assertEqual(binding.synthetic_sha, SYNTHETIC)
        self.assertEqual(asdict(binding.summary), asdict(EXPECTED))

    def test_valid_zero_warning_summary(self) -> None:
        expected = replace(EXPECTED, pytest_warnings=0)
        actual = self.verify(log=valid_log(warnings=0), expected=expected).summary
        self.assertEqual(asdict(actual), asdict(expected))

    def test_rejects_stale_run_or_job_ids(self) -> None:
        for field, value in (
            ("expected_job_id", JOB_ID + 1),
            ("expected_run_id", RUN_ID + 1),
        ):
            with self.subTest(field=field), self.assertRaises(BindingError):
                self.verify(**{field: value})
        stale_job = job_payload()
        stale_job["run_id"] = RUN_ID + 1
        with self.assertRaises(BindingError):
            self.verify(job=stale_job)

    def test_rejects_stale_head_metadata(self) -> None:
        for payload_name in ("job", "run"):
            payload = job_payload() if payload_name == "job" else run_payload()
            payload["head_sha"] = "c" * 40
            with self.subTest(payload=payload_name), self.assertRaises(BindingError):
                self.verify(**{payload_name: payload})

    def test_rejects_wrong_job_identity_or_non_success(self) -> None:
        for key, value in {
            "name": "quality / shard-1",
            "status": "in_progress",
            "conclusion": "failure",
        }.items():
            payload = job_payload()
            payload[key] = value
            with self.subTest(key=key), self.assertRaises(BindingError):
                self.verify(job=payload)
        run = run_payload()
        run["conclusion"] = "cancelled"
        with self.assertRaises(BindingError):
            self.verify(run=run)

    def test_rejects_checkout_command_or_synthetic_output_drift(self) -> None:
        mutations = (
            valid_log().replace("git log -1 --format=%H", "git rev-parse HEAD"),
            valid_log().replace(_line(SYNTHETIC), _line("c" * 40)),
            valid_log().replace(
                _line("[command]/usr/bin/git log -1 --format=%H"),
                _line("[command]/usr/bin/git log -1 --format=%H")
                + "\n"
                + _line("unexpected output"),
            ),
        )
        for log in mutations:
            with self.subTest(log=log), self.assertRaises(BindingError):
                self.verify(log=log)

    def test_rejects_each_expected_summary_drift(self) -> None:
        for field in asdict(EXPECTED):
            value = getattr(EXPECTED, field)
            replacement = False if field == "ruff_passed" else value + 1
            with self.subTest(field=field), self.assertRaises(BindingError):
                self.verify(expected=replace(EXPECTED, **{field: replacement}))

    def test_rejects_missing_or_cross_step_evidence(self) -> None:
        markers = (
            "All checks passed!",
            "Success: no issues found in 742 source files",
            "collected 4877 items",
            "TOTAL 48123 5775 88%",
            "================= 4877 passed, 3 warnings in 10.25s (0:00:10) =================",
        )
        for marker in markers:
            with self.subTest(marker=marker), self.assertRaises(BindingError):
                self.verify(log=valid_log().replace(_line(marker), ""))

    def test_rejects_non_all_pass_collection(self) -> None:
        with self.assertRaises(BindingError):
            self.verify(log=valid_log().replace("collected 4877 items", "collected 4878 items"))

    def test_expected_summary_schema_is_exact_and_strict(self) -> None:
        valid = asdict(EXPECTED)
        self.assertEqual(parse_expected_summary(json.dumps(valid)), EXPECTED)
        invalid_payloads = (
            {**valid, "extra": 1},
            {key: value for key, value in valid.items() if key != "ruff_passed"},
            {**valid, "ruff_passed": 1},
            {**valid, "pytest_warnings": -1},
            {**valid, "mypy_source_files": True},
            {**valid, "coverage_percent": "88"},
            {**valid, "coverage_percent": 101},
            {**valid, "pytest_collected": valid["pytest_passed"] + 1},
            {
                **valid,
                "coverage_missed_statements": valid["coverage_total_statements"] + 1,
            },
        )
        for invalid in invalid_payloads:
            with self.subTest(invalid=invalid), self.assertRaises(BindingError):
                parse_expected_summary(json.dumps(invalid))


if __name__ == "__main__":
    unittest.main()
