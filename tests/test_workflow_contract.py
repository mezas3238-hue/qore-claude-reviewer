from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


class WorkflowContractTests(unittest.TestCase):
    def test_review_dispatch_has_exact_nine_inputs(self) -> None:
        text = (WORKFLOWS / "claude-qore-review.yml").read_text(encoding="utf-8")
        header = text.split("permissions:", 1)[0]
        names = re.findall(r"^      ([a-z][a-z0-9_]*):$", header, re.MULTILINE)
        self.assertEqual(
            names,
            [
                "pr_number",
                "package_id",
                "expected_base",
                "expected_head",
                "expected_synthetic",
                "qg_run_id",
                "qg_job_id",
                "expected_qg_summary",
                "prompt_path",
            ],
        )

    def test_review_workflow_binds_live_qg_without_historical_constants(self) -> None:
        text = (WORKFLOWS / "claude-qore-review.yml").read_text(encoding="utf-8")
        for required in (
            "permission-actions: read",
            'actions/runs/${QG_RUN_ID}',
            'actions/jobs/${QG_JOB_ID}',
            'actions/jobs/${QG_JOB_ID}/logs',
            "scripts/qg_binding.py",
            '--expected-head "$EXPECTED_HEAD"',
            '--expected-synthetic "$EXPECTED_SYNTHETIC"',
            "qore-quality-job-post.log",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)
        for stale in (
            "33260165867",
            "99120615940",
            "871def531b0f1222e6a1e61252af700f4ed204e3",
            "4862 passed",
            "Mypy 740",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)

    def test_claude_read_only_boundary_and_full_postreview_freeze_remain(self) -> None:
        text = (WORKFLOWS / "claude-qore-review.yml").read_text(encoding="utf-8")
        for required in (
            "contents: read",
            "permission-pull-requests: read",
            "persist-credentials: false",
            "--allowedTools Read",
            "--disallowedTools Bash Edit Write NotebookEdit WebFetch WebSearch Task",
            'test -z "$(git -C "$QORE_ROOT" status --porcelain)"',
            'test "$(printf \'%s\' "$PR_JSON" | jq -r \'.base.sha\')" = "$EXPECTED_BASE"',
            'test "$(printf \'%s\' "$PR_JSON" | jq -r \'.head.sha\')" = "$EXPECTED_HEAD"',
            'test "$(printf \'%s\' "$PR_JSON" | jq -r \'.merge_commit_sha\')" = "$EXPECTED_SYNTHETIC"',
            "Post-review BASE/HEAD/SYNTHETIC/QG freeze revalidated.",
            'cmp "$RUNNER_TEMP/qore-quality-gate-binding.md"',
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_auto_dispatch_strictly_validates_and_forwards_qg_contract(self) -> None:
        text = (WORKFLOWS / "claude-auto-dispatch.yml").read_text(encoding="utf-8")
        for required in (
            'keys == ["expected_base", "expected_head", "expected_synthetic", "package_id", "pr_number", "prompt_path", "qg"]',
            '.qg | keys == ["expected", "job_id", "run_id"]',
            ".qg.expected.ruff_passed == true",
            ".qg.expected.mypy_source_files",
            ".qg.expected.pytest_collected",
            ".qg.expected.pytest_passed",
            ".qg.expected.pytest_warnings",
            ".qg.expected.coverage_total_statements",
            ".qg.expected.coverage_missed_statements",
            ".qg.expected.coverage_percent",
            "qg_run_id=${QG_RUN_ID}",
            "qg_job_id=${QG_JOB_ID}",
            "expected_qg_summary=${EXPECTED_QG_SUMMARY}",
            "persist-credentials: false",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
