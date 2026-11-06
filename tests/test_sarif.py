from guardian.sarif import to_sarif
from guardian.schemas import Finding


def test_exports_findings_as_sarif_21():
    finding = Finding(
        rule_id="OG002",
        title="TLS verification disabled",
        description="Keep TLS verification enabled.",
        severity="high",
        file_path="src/client.py",
        line=12,
    )
    report = to_sarif([finding])
    assert report["version"] == "2.1.0"
    result = report["runs"][0]["results"][0]
    assert result["ruleId"] == "OG002"
    assert result["level"] == "error"
    assert result["locations"][0]["physicalLocation"]["region"]["startLine"] == 12


def test_sarif_handles_findings_without_file_location():
    finding = Finding(
        rule_id="OG001",
        title="Possible secret",
        description="Rotate the exposed secret.",
        severity="critical",
    )
    result = to_sarif([finding])["runs"][0]["results"][0]
    assert "locations" not in result
