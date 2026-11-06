"""Small, explainable checks for risky patterns in added diff lines."""

import re

from guardian.schemas import Finding

RULES: list[tuple[str, str, str, str, re.Pattern[str]]] = [
    (
        "OG001",
        "Possible hard-coded secret",
        "An added line appears to contain a password, API key, or access token. Move secrets to a secret manager.",
        "critical",
        re.compile(r"(?i)(api[_-]?key|secret|password|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}"),
    ),
    (
        "OG002",
        "TLS certificate verification disabled",
        "Disabling TLS verification makes connections vulnerable to interception. Keep certificate verification enabled.",
        "high",
        re.compile(r"(?i)(verify\s*=\s*False|CERT_NONE|rejectUnauthorized\s*:\s*false)"),
    ),
    (
        "OG003",
        "Potentially dangerous shell execution",
        "Review shell execution with dynamic input. Prefer argument arrays and validate untrusted values.",
        "high",
        re.compile(r"(?i)(shell\s*=\s*True|os\.system\s*\(|child_process\.exec\s*\()"),
    ),
    (
        "OG004",
        "Overly permissive file mode",
        "World-writable permissions can expose sensitive files. Confirm this permission is necessary.",
        "medium",
        re.compile(r"(?i)(chmod\s+777|0o777|mode\s*=\s*0?777)"),
    ),
]

_DIFF_HEADER = re.compile(r"^\+\+\+ b/(.+)$")


def analyze_diff(diff: str) -> list[Finding]:
    findings: list[Finding] = []
    current_file: str | None = None
    new_line = 0

    for raw_line in diff.splitlines():
        if raw_line.startswith("+++ "):
            match = _DIFF_HEADER.match(raw_line)
            current_file = match.group(1) if match else None
        elif raw_line.startswith("@@"):
            match = re.search(r"\+(\d+)", raw_line)
            if match:
                new_line = int(match.group(1))
        elif raw_line.startswith("+") and not raw_line.startswith("+++"):
            added = raw_line[1:]
            for rule_id, title, description, severity, pattern in RULES:
                if pattern.search(added):
                    findings.append(
                        Finding(
                            rule_id=rule_id,
                            title=title,
                            description=description,
                            severity=severity,  # type: ignore[arg-type]
                            file_path=current_file,
                            line=new_line or None,
                        )
                    )
            new_line += 1
        elif raw_line.startswith(" "):
            new_line += 1

    return findings
