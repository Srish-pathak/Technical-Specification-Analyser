"""Pydantic request/response models for the HTTP API."""
from typing import Optional

from pydantic import BaseModel, Field


class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to analyse (never executed).")
    language: Optional[str] = Field("auto", description="python, javascript, ... or 'auto'")
    filename: Optional[str] = Field(None, max_length=120)


class GithubAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=5, description="GitHub repository URL (e.g. https://github.com/owner/repo)")
    branch: Optional[str] = Field(None, description="Optional branch or commit to inspect (defaults to default branch)")
    token: Optional[str] = Field(None, description="Optional personal access token for private repositories")


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
