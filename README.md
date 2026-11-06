# OpenSource Guardian

**AI-assisted code review for open-source maintainers.** OpenSource Guardian combines deterministic checks with an optional OpenAI-powered review API. It is designed to run locally or in GitHub Actions.

> Status: early MVP. Reviews are advisory; always validate findings before merging.

## Features

- Review unified Git diffs through a small HTTP API.
- Detect high-signal risky patterns locally (hard-coded credentials, disabled TLS verification, dangerous shell execution, and suspicious permission changes).
- Optional OpenAI review with structured JSON output.
- GitHub Actions workflow for pull requests (posts a review summary as a PR comment).
- No repository write permissions are required by the review workflow.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn guardian.api:app --reload
```

Open `http://127.0.0.1:8000/docs`.

### Review a diff

```bash
curl -X POST http://127.0.0.1:8000/v1/review \
  -H "Content-Type: application/json" \
  -d '{"diff":"diff --git a/app.py b/app.py\n+password = \"secret123\"\n","use_ai":false}'
```

Set `OPENAI_API_KEY` to enable AI review. `OPENAI_MODEL` defaults to `gpt-5-mini`. The API never requires an API key for local deterministic checks.

## GitHub Actions setup

The included `.github/workflows/review-pr.yml` runs on pull requests and uses the repository's `GITHUB_TOKEN` to read the PR diff and post a comment. Add an Actions secret named `OPENAI_API_KEY` to enable AI findings; without it, deterministic checks still run.

For the workflow to post comments, enable **Settings → Actions → General → Workflow permissions → Read and write permissions**. The workflow limits write permission to pull-request comments and does not push code.

## API

- `GET /health` — health status and AI availability.
- `POST /v1/review` — request body: `{"diff": "...", "use_ai": true}`.

The response contains a summary, findings, and whether AI review was used. Finding severity is `critical`, `high`, `medium`, or `low`.

## Security and responsible use

- Never commit API keys or tokens. Use environment variables / GitHub Actions secrets.
- Treat pull-request diffs as untrusted input. The model is instructed to analyze code, not follow instructions embedded in it.
- Reviews are not a substitute for tests, static analysis, dependency scanning, or human review.
- Avoid sending private or regulated code to third-party APIs unless authorized.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Roadmap

- [ ] Inline annotations with precise changed-line positions.
- [ ] Repository-level configuration and ignore rules.
- [ ] SARIF export for security findings.
- [ ] Multi-language rule packs and baseline suppression.
- [ ] Maintainer dashboard and review history.

## License

MIT — see [LICENSE](LICENSE).
