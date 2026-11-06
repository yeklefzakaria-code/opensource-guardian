from guardian.rules import analyze_diff


def test_detects_hardcoded_secret_with_file_and_line():
    diff = """diff --git a/app.py b/app.py
index 123..456 100644
--- a/app.py
+++ b/app.py
@@ -1,2 +1,3 @@
 import os
+API_KEY = "sk_test_123456789"
 print("hello")
"""
    findings = analyze_diff(diff)
    assert len(findings) == 1
    assert findings[0].rule_id == "OG001"
    assert findings[0].file_path == "app.py"
    assert findings[0].line == 2


def test_ignores_removed_lines():
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-password = "not-an-added-line-secret"
+password = os.environ["PASSWORD"]
"""
    assert analyze_diff(diff) == []


def test_detects_multiple_risky_patterns():
    diff = """diff --git a/client.py b/client.py
--- a/client.py
+++ b/client.py
@@ -0,0 +1,2 @@
+requests.get(url, verify=False)
+os.system(user_input)
"""
    findings = analyze_diff(diff)
    assert {item.rule_id for item in findings} == {"OG002", "OG003"}
