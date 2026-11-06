"""SARIF 2.1.0 serialization for GitHub code scanning integrations."""

from guardian.schemas import Finding

LEVELS = {"critical": "error", "high": "error", "medium": "warning", "low": "note"}


def to_sarif(findings: list[Finding]) -> dict[str, object]:
    rules_by_id: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []

    for finding in findings:
        rules_by_id.setdefault(
            finding.rule_id,
            {
                "id": finding.rule_id,
                "name": finding.title,
                "shortDescription": {"text": finding.title},
                "help": {"text": finding.description},
                "defaultConfiguration": {"level": LEVELS[finding.severity]},
            },
        )
        result: dict[str, object] = {
            "ruleId": finding.rule_id,
            "level": LEVELS[finding.severity],
            "message": {"text": finding.description},
            "properties": {"severity": finding.severity, "source": finding.source},
        }
        if finding.file_path:
            physical: dict[str, object] = {
                "artifactLocation": {"uri": finding.file_path.replace("\\", "/")}
            }
            if finding.line and finding.line > 0:
                physical["region"] = {"startLine": finding.line}
            result["locations"] = [{"physicalLocation": physical}]
        results.append(result)

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "OpenSource Guardian",
                        "informationUri": "https://github.com/yeklefzakaria-code/opensource-guardian",
                        "rules": list(rules_by_id.values()),
                    }
                },
                "results": results,
            }
        ],
    }
