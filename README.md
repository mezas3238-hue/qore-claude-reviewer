# QORE Claude Reviewer

Independent, read-only Claude review infrastructure for QORE Core.

## Security posture

- QORE Core is the sole source of truth for candidate code and pull-request state.
- This repository must never become a runtime dependency of QORE Core.
- Claude reviews frozen QORE Core commits and may publish review evidence only.
- No push, merge, deployment, Production, provider credential, or real-capital authority is granted to Claude.
- Anthropic API credentials and GitHub App private keys belong only in GitHub Actions Secrets and must never be committed.

## Intended review chain

1. Integration Authority freezes BASE / HEAD / synthetic / Quality Gate evidence.
2. DeepSeek Expert review is completed and independently adjudicated.
3. DeepSeek Coder review is completed and independently adjudicated.
4. Claude runs independently against the same exact frozen QORE Core HEAD.
5. Claude re-verifies the frozen HEAD before publishing its review.
6. Integration Authority independently adjudicates Claude's evidence before any integration decision.
