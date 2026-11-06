from typing import Literal
from pathlib import PurePosixPath

from pydantic import BaseModel, Field, field_validator, model_validator


Severity = Literal["critical", "high", "medium", "low"]


class ReviewRequest(BaseModel):
    diff: str = Field(min_length=1, max_length=200_000)
    use_ai: bool = True


class ScanRequest(BaseModel):
    files: dict[str, str] = Field(min_length=1, max_length=100)

    @field_validator("files")
    @classmethod
    def validate_file_paths(cls, files: dict[str, str]) -> dict[str, str]:
        for path in files:
            parsed = PurePosixPath(path)
            if (
                not path
                or path.startswith(("/", "\\"))
                or "\x00" in path
                or "\n" in path
                or "\r" in path
                or "\\" in path
                or ".." in parsed.parts
            ):
                raise ValueError("file paths must be relative, normalized paths")
        return files

    @model_validator(mode="after")
    def limit_total_source_size(self) -> "ScanRequest":
        if sum(len(source) for source in self.files.values()) > 500_000:
            raise ValueError("combined source content must not exceed 500,000 characters")
        return self


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
