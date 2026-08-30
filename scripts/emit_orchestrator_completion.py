#!/usr/bin/env python3
"""Emit an exact QORE reviewer-completion event to the orchestration control plane."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

ORCHESTRATOR_REPO = "mezas3238-hue/qore-ai-orchestrator"
ORCHESTRATOR_API = f"https://api.github.com/repos/{ORCHESTRATOR_REPO}"
SCHEMA_VERSION = "qore.agent.completion.v1"
EVENT_TYPE = "qore_agent_completion_v1"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PACKAGE_RES = {
    "CLAUDE_CODE": re.compile(r"^QORE-SOL-[0-9a-f]{12}-CLAUDE-R[1-9][0-9]*$"),
    "DEEPSEEK": re.compile(r"^QORE-SOL-[0-9a-f]{12}-DS-(?:EXPERT|CODER)-R[1-9][0-9]*$"),
}
USER_AGENT = "qore-reviewer-completion-callback/1.0"


class CallbackError(RuntimeError):
    pass


def _headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }


def api_json(
    token: str,
    api_base: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> Any:
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(api_base + path, data=data, headers=_headers(token), method=method)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read().decode("utf-8")
            if response.status not in {200, 201, 202, 204}:
                raise CallbackError(f"GitHub API {path} returned unexpected HTTP {response.status}")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raise CallbackError(f"GitHub API {path} failed with HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise CallbackError(f"GitHub API {path} failed: {type(exc).__name__}") from exc


def _decode_content(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("content"), str):
        raise CallbackError("requests/current.json content is unavailable")
    try:
        encoded = "".join(payload["content"].split())
        raw = base64.b64decode(encoded, validate=True).decode("utf-8")
        value = json.loads(raw)
    except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
        raise CallbackError("requests/current.json is invalid") from exc
    if not isinstance(value, dict):
        raise CallbackError("requests/current.json is not an object")
    return value


def _positive_int(value: Any, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise CallbackError(f"{label} must be a positive integer")
    return value


def _package_re(actor: str) -> re.Pattern[str]:
    try:
        return PACKAGE_RES[actor]
    except KeyError as exc:
        raise CallbackError(f"unsupported actor: {actor}") from exc


def package_from_display_title(title: Any, workflow_name: str, actor: str) -> str:
    prefix = f"{workflow_name} · "
    text = str(title or "")
    package_id = text[len(prefix):].strip() if text.startswith(prefix) else ""
    if _package_re(actor).fullmatch(package_id) is None:
        raise CallbackError("workflow display title is not bound to an exact package")
    return package_id


def package_from_artifacts(artifacts: Any, prefix: str, actor: str) -> str:
    if not isinstance(artifacts, dict) or not isinstance(artifacts.get("artifacts"), list):
        raise CallbackError("workflow artifact list is invalid")
    matches: list[str] = []
    for item in artifacts["artifacts"]:
        if not isinstance(item, dict) or item.get("expired") is not False:
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name.startswith(prefix):
            continue
        package_id = name[len(prefix):]
        if _package_re(actor).fullmatch(package_id):
            matches.append(package_id)
    unique = sorted(set(matches))
    if len(unique) != 1:
        raise CallbackError(f"expected one exact package-bound artifact; found {len(unique)}")
    return unique[0]


def validate_run(
    event_run: Any,
    live_run: Any,
    *,
    workflow_name: str,
) -> tuple[int, int, str, str | None]:
    if not isinstance(event_run, dict) or not isinstance(live_run, dict):
        raise CallbackError("workflow_run payload is invalid")
    run_id = _positive_int(event_run.get("id"), "workflow_run.id")
    attempt = _positive_int(event_run.get("run_attempt", 1), "workflow_run.run_attempt")
    for payload in (event_run, live_run):
        if payload.get("id") != run_id:
            raise CallbackError("workflow run ID mismatch")
        if payload.get("name") != workflow_name:
            raise CallbackError("workflow name mismatch")
        if payload.get("event") != "workflow_dispatch":
            raise CallbackError("completion source is not workflow_dispatch")
        if payload.get("status") != "completed":
            raise CallbackError("completion source is not completed")
        if payload.get("head_branch") != "main":
            raise CallbackError("reviewer run did not execute from main")
        head_sha = payload.get("head_sha")
        if not isinstance(head_sha, str) or SHA_RE.fullmatch(head_sha) is None:
            raise CallbackError("reviewer run head SHA is invalid")
        if payload.get("run_attempt", 1) != attempt:
            raise CallbackError("workflow run attempt mismatch")
    if event_run.get("head_sha") != live_run.get("head_sha"):
        raise CallbackError("event/live reviewer HEAD mismatch")
    conclusion = live_run.get("conclusion")
    if conclusion is not None and not isinstance(conclusion, str):
        raise CallbackError("reviewer conclusion is invalid")
    return run_id, attempt, live_run["head_sha"], conclusion


def request_at_head(source_token: str, source_api: str, head_sha: str) -> dict[str, Any]:
    encoded = urllib.parse.quote("requests/current.json", safe="/")
    payload = api_json(source_token, source_api, f"/contents/{encoded}?ref={head_sha}")
    return _decode_content(payload)


def build_callback(
    *,
    repository: str,
    actor: str,
    run_id: int,
    attempt: int,
    package_id: str,
) -> dict[str, Any]:
    if _package_re(actor).fullmatch(package_id) is None:
        raise CallbackError("package ID is invalid for actor")
    return {
        "event_type": EVENT_TYPE,
        "client_payload": {
            "schema_version": SCHEMA_VERSION,
            "repository": repository,
            "actor": actor,
            "workflow_run_id": run_id,
            "workflow_run_attempt": attempt,
            "package_id": package_id,
        },
    }


def _self_test() -> None:
    claude = "QORE-SOL-012345abcdef-CLAUDE-R123"
    deepseek = "QORE-SOL-012345abcdef-DS-EXPERT-R123"
    assert package_from_display_title(
        f"DeepSeek QORE review · {deepseek}", "DeepSeek QORE review", "DEEPSEEK"
    ) == deepseek
    artifacts = {"artifacts": [{"name": f"claude-{claude}", "expired": False}]}
    assert package_from_artifacts(artifacts, "claude-", "CLAUDE_CODE") == claude
    encoded = base64.b64encode(json.dumps({"package_id": claude}).encode()).decode()
    wrapped = encoded[:8] + "\n" + encoded[8:]
    assert _decode_content({"content": wrapped})["package_id"] == claude
    callback = build_callback(
        repository="mezas3238-hue/qore-claude-reviewer",
        actor="CLAUDE_CODE",
        run_id=7,
        attempt=1,
        package_id=claude,
    )
    assert callback["client_payload"]["package_id"] == claude
    try:
        package_from_display_title("DeepSeek QORE review", "DeepSeek QORE review", "DEEPSEEK")
    except CallbackError:
        pass
    else:
        raise AssertionError("unbound title must fail closed")
    print("callback self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event")
    parser.add_argument("--repository")
    parser.add_argument("--workflow-name")
    parser.add_argument("--actor", choices=tuple(PACKAGE_RES))
    parser.add_argument("--binding", choices=("artifact", "run_name"))
    parser.add_argument("--artifact-prefix", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return 0
    if not all((args.event, args.repository, args.workflow_name, args.actor, args.binding)):
        parser.error("event, repository, workflow-name, actor and binding are required")

    source_token = os.environ.get("GITHUB_TOKEN", "").strip()
    callback_token = os.environ.get("QORE_CALLBACK_TOKEN", "").strip()
    if not source_token or not callback_token:
        raise CallbackError("required GitHub tokens are unavailable")

    with open(args.event, encoding="utf-8") as event_file:
        event = json.load(event_file)
    event_run = event.get("workflow_run") if isinstance(event, dict) else None
    source_api = f"https://api.github.com/repos/{args.repository}"
    if not isinstance(event_run, dict):
        raise CallbackError("workflow_run event is missing")
    event_run_id = _positive_int(event_run.get("id"), "workflow_run.id")
    live_run = api_json(source_token, source_api, f"/actions/runs/{event_run_id}")
    run_id, attempt, head_sha, conclusion = validate_run(
        event_run, live_run, workflow_name=args.workflow_name
    )

    request = request_at_head(source_token, source_api, head_sha)
    request_package = request.get("package_id")
    expected_head = request.get("expected_head")
    if not isinstance(request_package, str) or _package_re(args.actor).fullmatch(request_package) is None:
        raise CallbackError("run HEAD request does not contain an autonomous package")
    if not isinstance(expected_head, str) or SHA_RE.fullmatch(expected_head) is None:
        raise CallbackError("run HEAD request expected_head is invalid")

    if args.binding == "run_name":
        package_id = package_from_display_title(
            live_run.get("display_title"), args.workflow_name, args.actor
        )
    else:
        if not args.artifact_prefix:
            raise CallbackError("artifact binding requires an artifact prefix")
        artifact_payload = api_json(
            source_token, source_api, f"/actions/runs/{run_id}/artifacts?per_page=100"
        )
        try:
            package_id = package_from_artifacts(
                artifact_payload, args.artifact_prefix, args.actor
            )
        except CallbackError:
            if conclusion == "success":
                raise
            package_id = request_package
            print("Non-success reviewer used request-at-run-HEAD fallback binding.")

    if package_id != request_package:
        raise CallbackError("run-bound package and requests/current.json disagree")

    payload = build_callback(
        repository=args.repository,
        actor=args.actor,
        run_id=run_id,
        attempt=attempt,
        package_id=package_id,
    )
    api_json(callback_token, ORCHESTRATOR_API, "/dispatches", method="POST", payload=payload)
    print(json.dumps({
        "callback": "accepted",
        "actor": args.actor,
        "repository": args.repository,
        "workflow_run_id": run_id,
        "workflow_run_attempt": attempt,
        "package_id": package_id,
        "reviewer_conclusion": conclusion,
        "reviewer_head_sha": head_sha,
        "candidate_head": expected_head,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CallbackError, json.JSONDecodeError, OSError) as exc:
        print(f"completion callback failed closed: {exc}", file=sys.stderr)
        raise SystemExit(2)
