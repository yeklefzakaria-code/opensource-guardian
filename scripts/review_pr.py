"""GitHub Actions entry point: review a PR diff and publish a summary comment."""

import os
import sys
from urllib.request import Request, urlopen

from openai import APIError

from guardian.config import settings
from guardian.reviewer import ai_review
from guardian.rules import analyze_diff


def github_api(path: str, token: str, method: str = "GET", body: bytes | None = None) -> bytes:
    request = Request(
        f"https://api.github.com{path}",
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read()


def main() -> int:
    token = os.environ["GH_TOKEN"]
    repository = os.environ["REPOSITORY"]
    number = os.environ["PR_NUMBER"]

    diff_request = Request(
        f"https://api.github.com/repos/{repository}/pulls/{number}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.diff",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urlopen(diff_request, timeout=30) as response:
        diff = response.read().decode("utf-8", errors="replace")

    findings = analyze_diff(diff)
    if settings.openai_api_key:
        findings.extend(ai_review(diff))

    if findings:
        lines = ["## 🛡️ OpenSource Guardian review", "", f"Found **{len(findings)} potential issue(s)**:"]
        for finding in findings:
            location = f"`{finding.file_path or 'unknown file'}"
            if finding.line:
                location += f":{finding.line}"
            location += "`"
            lines.append(
                f"- **{finding.severity.upper()} · {finding.rule_id} — {finding.title}** "
                f"({location})\n  {finding.description}"
            )
    else:
        lines = [
            "## 🛡️ OpenSource Guardian review",
            "",
            "No actionable findings detected by the enabled checks.",
            "",
            "_This is an advisory review, not a guarantee that the change is safe._",
        ]

    import json

    body = json.dumps({"body": "\n".join(lines)}).encode("utf-8")
    if os.environ.get("CAN_COMMENT", "false").lower() == "true":
        github_api(f"/repos/{repository}/issues/{number}/comments", token, "POST", body)
    else:
        print("Fork pull request: review output is logged; no write token is used.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, APIError) as exc:
        print(f"Review failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
