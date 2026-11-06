"""Repository source scanning built on the same explainable rule pack as diff review."""

from guardian.rules import RULES
from guardian.schemas import Finding


def analyze_sources(files: dict[str, str]) -> list[Finding]:
    """Analyze source text and report rule matches with 1-based line numbers."""
    findings: list[Finding] = []
    for file_path, source in files.items():
        for line_number, line in enumerate(source.splitlines(), start=1):
            for rule_id, title, description, severity, pattern in RULES:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            rule_id=rule_id,
                            title=title,
                            description=description,
                            severity=severity,  # type: ignore[arg-type]
                            file_path=file_path,
                            line=line_number,
                        )
                    )
    return findings
