# OpenSource Guardian

**AI-assisted security review for open-source maintainers.** OpenSource Guardian combines deterministic checks with optional OpenAI-powered analysis and GitHub Actions integration.

> **MVP status:** Reviews are advisory, not a proof that code is safe. Validate every finding before acting on it.

## What it does

- Analyze unified Git diffs through a REST API and browser dashboard.
- Scan batches of source files through a repository-scan API, returning file paths and 1-based line numbers.
- Detect likely hard-coded secrets, disabled TLS verification, risky shell execution, permissive file modes, dynamic evaluation, insecure random-number generation, unsafe deserialization, and weak hashes.
- Optionally add an OpenAI review when `OPENAI_API_KEY` is configured for diff reviews.
- Export diff-review findings as **SARIF 2.1.0** for security tooling.
- Review pull requests in GitHub Actions without checking out or executing pull-request code.
- Audit declared Python runtime dependencies against the Python Packaging Advisory Database with scheduled and on-demand GitHub Actions runs.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn guardian.api:app --reload
```

Open `http://127.0.0.1:8000` for the dashboard or `http://127.0.0.1:8000/docs` for the interactive API documentation.

## API

### `GET /health`

Returns service health and whether an OpenAI key is configured.

### `POST /v1/review`

Analyze a unified Git diff. Request:

```json
{
  "diff": "+++ b/app.py\\n@@ -0,0 +1 @@\\n+requests.get(url, verify=False)",
  "use_ai": false
}
```

Returns a summary, structured findings, and an `ai_reviewed` flag.

### `POST /v1/review/sarif`

Accepts the same request and returns a SARIF 2.1.0 document with the `application/sarif+json` media type.

### `POST /v1/scan`

Scan source files directly without constructing a Git diff. Example:

```json
{
  "files": {
    "src/client.py": "import requests\\nrequests.get(url, verify=False)",
    "src/auth.py": "token = random.random()"
  }
}
```

The response uses the same finding schema as diff review, including file paths and 1-based line numbers. Requests are limited to 100 files and 500,000 combined source characters; file paths must be relative and normalized. This endpoint runs deterministic rules only and does not transmit source code to an AI provider.

## Optional AI review

Set `OPENAI_API_KEY` in the environment to enable AI review. `OPENAI_MODEL` defaults to `gpt-5-mini`. Deterministic checks work without an API key.

Do not send private, regulated, or otherwise sensitive source code to a third-party model unless you are authorized to do so.

## GitHub Actions

The repository includes:
- **CI** — Ruff linting and pytest.
- **Dependency Security Audit** — runs `pip-audit` against `requirements-audit.txt` on pushes, pull requests, weekly, and on manual dispatch. It resolves transitive dependencies and checks known advisories from the Python Packaging Advisory Database; the JSON report is retained as a workflow artifact for 14 days. Keep `requirements-audit.txt` in sync with runtime dependencies in `pyproject.toml`.
- **OpenSource Guardian PR Review** — analyzes the PR diff using trusted base-branch code. It does not execute code supplied by the pull request.

The PR review workflow uses the GitHub token to read the diff and, for same-repository pull requests, publish a summary comment. Fork pull requests are handled without posting a comment. Add an Actions secret named `OPENAI_API_KEY` only if you want AI review in the workflow; GitHub does not expose repository secrets to workflows triggered by fork pull requests.

## Detection rules

| Rule | Description | Default severity |
| --- | --- | --- |
| OG001 | Possible hard-coded secret | Critical |
| OG002 | TLS certificate verification disabled | High |
| OG003 | Potentially dangerous shell execution | High |
| OG004 | Overly permissive file mode | Medium |
| OG005 | Dynamic code evaluation | High |
| OG006 | Potentially insecure random number generation | Medium |
| OG007 | Potentially unsafe pickle/marshal deserialization | High |
| OG008 | Weak MD5/SHA-1 cryptographic hash | Low |

These are pattern-based heuristics. They can produce false positives and will not detect every vulnerability.

Dependency auditing is a separate, network-backed workflow. It reports advisories known to the upstream database at scan time; it is not a guarantee that every dependency or vulnerability is covered. The audit manifest lists direct runtime dependencies, while `pip-audit` resolves their transitive dependencies.

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## Security and responsible use

- Never commit API keys, tokens, or credentials.
- Treat pull-request diffs as untrusted input.
- Use least-privilege GitHub Actions permissions.
- Review findings manually; this tool is not a replacement for tests, dependency auditing, static analysis, or expert review.

## Roadmap

- Inline annotations on changed lines.
- Multi-language rule packs and baseline suppression.
- Maintainer dashboard with review history.

## License

MIT — see [LICENSE](LICENSE).
