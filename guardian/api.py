from fastapi import FastAPI, HTTPException

from guardian.config import settings
from guardian.reviewer import ai_review
from guardian.rules import analyze_diff
from guardian.schemas import ReviewRequest, ReviewResponse

app = FastAPI(
    title="OpenSource Guardian",
    description="AI-assisted code review for open-source maintainers.",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "ai_enabled": bool(settings.openai_api_key)}


@app.post("/v1/review", response_model=ReviewResponse)
def review(request: ReviewRequest) -> ReviewResponse:
    findings = analyze_diff(request.diff)
    ai_reviewed = False

    if request.use_ai and settings.openai_api_key:
        try:
            findings.extend(ai_review(request.diff))
            ai_reviewed = True
        except Exception as exc:
            raise HTTPException(status_code=502, detail="AI review provider failed") from exc

    # Stable ordering makes API responses and tests predictable.
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda item: (order[item.severity], item.file_path or "", item.line or 0))

    if not findings:
        summary = "No actionable findings detected. This is not a guarantee that the diff is safe."
    else:
        summary = f"Found {len(findings)} potential issue(s). Please validate each finding before merging."

    return ReviewResponse(summary=summary, findings=findings, ai_reviewed=ai_reviewed)
