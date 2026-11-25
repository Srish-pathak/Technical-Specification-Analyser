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


class GithubPushAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=5, description="GitHub repository URL (e.g. https://github.com/owner/repo)")
    commit_sha: Optional[str] = Field(None, description="Commit SHA or ref to analyze (defaults to latest commit)")
    branch: Optional[str] = Field(None, description="Optional branch name")
    token: Optional[str] = Field(None, description="Optional personal access token for private repositories")


class GithubCommitsRequest(BaseModel):
    url: str = Field(..., min_length=5, description="GitHub repository URL")
    branch: Optional[str] = Field(None, description="Optional branch name")
    token: Optional[str] = Field(None, description="Optional personal access token")
    limit: Optional[int] = Field(10, ge=1, le=30, description="Max commits to return")


class GithubRepoConnectRequest(BaseModel):
    url: str = Field(..., min_length=5, description="GitHub repository URL (e.g. https://github.com/owner/repo)")
    default_branch: Optional[str] = Field("main", description="Default branch to track")
    auto_analysis: Optional[bool] = Field(True, description="Whether to automatically run analysis on incoming push events")
    webhook_secret: Optional[str] = Field(None, description="Optional per-repository webhook secret")


class GithubRepoUpdateRequest(BaseModel):
    default_branch: Optional[str] = Field(None, description="Updated branch")
    auto_analysis: Optional[bool] = Field(None, description="Enable or disable automatic push analysis")
    is_active: Optional[bool] = Field(None, description="Connection active flag")
    webhook_secret: Optional[str] = Field(None, description="Optional updated webhook secret")


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
