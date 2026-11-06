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


def test_detects_dynamic_eval_and_insecure_random():
    diff = """diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -0,0 +1,2 @@
+eval(user_input)
+token = random.random()
"""
    findings = analyze_diff(diff)
    assert {item.rule_id for item in findings} == {"OG005", "OG006"}


def test_detects_world_writable_file_permissions():
    diff = """diff --git a/deploy.py b/deploy.py
--- a/deploy.py
+++ b/deploy.py
@@ -0,0 +1 @@
+os.chmod(path, 0o777)
"""
    findings = analyze_diff(diff)
    assert len(findings) == 1
    assert findings[0].rule_id == "OG004"
    assert findings[0].severity == "medium"


def test_tracks_added_line_numbers_after_context():
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -10,2 +10,3 @@
 existing_call()
+requests.get(url, verify=False)
 another_call()
"""
    findings = analyze_diff(diff)
    assert len(findings) == 1
    assert findings[0].file_path == "app.py"
    assert findings[0].line == 11


def test_detects_unsafe_deserialization():
    diff = """diff --git a/cache.py b/cache.py
--- a/cache.py
+++ b/cache.py
@@ -0,0 +1 @@
+payload = pickle.loads(user_supplied_bytes)
"""
    findings = analyze_diff(diff)
    assert len(findings) == 1
    assert findings[0].rule_id == "OG007"
    assert findings[0].severity == "high"


def test_detects_weak_hash_without_overstating_severity():
    diff = """diff --git a/checksum.py b/checksum.py
--- a/checksum.py
+++ b/checksum.py
@@ -0,0 +1 @@
+digest = hashlib.md5(data)
"""
    findings = analyze_diff(diff)
    assert len(findings) == 1
    assert findings[0].rule_id == "OG008"
    assert findings[0].severity == "low"
