from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low"]


class ReviewRequest(BaseModel):
    diff: str = Field(min_length=1, max_length=200_000)
    use_ai: bool = True


class Finding(BaseModel):
    rule_id: str
    title: str
    description: str
    severity: Severity
    file_path: str | None = None
    line: int | None = None
    source: Literal["guardian", "openai"] = "guardian"


class ReviewResponse(BaseModel):
    summary: str
    findings: list[Finding]
    ai_reviewed: bool
