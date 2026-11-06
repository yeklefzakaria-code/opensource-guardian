# Contributing

Thanks for helping improve OpenSource Guardian.

## Development setup

Use Python 3.11 or newer:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
pytest
```

## Adding a detection rule

1. Give the rule a stable identifier (`OG###`); do not reuse retired identifiers.
2. Match only added diff lines and keep the pattern understandable.
3. Choose severity conservatively. A heuristic is not proof of exploitability.
4. Explain the risk and a concrete mitigation in plain language.
5. Add positive and negative tests, including file path and line mapping where relevant.
6. Update the detection table in the README.

Prefer high-signal checks over broad patterns that flood maintainers with false positives.

## Pull requests

- Explain the problem and the behavior change.
- Include tests for bug fixes and new behavior.
- Do not include credentials, private data, or generated artifacts.
- Keep changes focused and document limitations.

All automated findings are advisory. Human review remains required.
