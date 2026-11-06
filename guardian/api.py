from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from guardian.config import settings
from guardian.reviewer import ai_review
from guardian.rules import analyze_diff
from guardian.schemas import ReviewRequest, ReviewResponse
from guardian.sarif import to_sarif

app = FastAPI(
    title="OpenSource Guardian",
    description="AI-assisted code review for open-source maintainers.",
    version="0.2.0",
)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "ai_enabled": bool(settings.openai_api_key)}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> HTMLResponse:
    with open("guardian/dashboard.html", encoding="utf-8") as page:
        return HTMLResponse(page.read())


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

    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda item: (order[item.severity], item.file_path or "", item.line or 0))

    if not findings:
        summary = "No actionable findings detected. This is not a guarantee that the diff is safe."
    else:
        summary = f"Found {len(findings)} potential issue(s). Please validate each finding before merging."

    return ReviewResponse(summary=summary, findings=findings, ai_reviewed=ai_reviewed)


@app.post("/v1/review/sarif")
def review_sarif(request: ReviewRequest) -> JSONResponse:
    findings = analyze_diff(request.diff)
    if request.use_ai and settings.openai_api_key:
        try:
            findings.extend(ai_review(request.diff))
        except Exception as exc:
            raise HTTPException(status_code=502, detail="AI review provider failed") from exc
    return JSONResponse(content=to_sarif(findings), media_type="application/sarif+json")
