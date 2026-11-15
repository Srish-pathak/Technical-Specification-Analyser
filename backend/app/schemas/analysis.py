"""Pydantic request/response models for the HTTP API."""
from typing import Optional

from pydantic import BaseModel, Field


class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to analyse (never executed).")
    language: Optional[str] = Field("auto", description="python, javascript, ... or 'auto'")
    filename: Optional[str] = Field(None, max_length=120)


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
