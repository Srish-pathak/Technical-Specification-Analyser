"""Gemini AI Code Review Agent for TechSpecAnalyser."""
import os
import json
import logging
from typing import Optional, Dict, Any, List
import httpx

logger = logging.getLogger("techspecanalyser.ai")

def review_code_with_gemini(
    code: str,
    language: str,
    findings: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    api_key: str,
    model: str = "gemini-3.8-flash"
) -> Dict[str, Any]:
    if not api_key:
        return {
            "available": False,
            "ran": False,
            "error": "No Gemini API key configured.",
            "note": "AI review skipped because no API key was provided."
        }

    prompt = f"""You are an expert software architect and security reviewer.
Analyze this {language} code snippet and its static analysis findings.

Source Code:
```{language}
{code[:8000]}
```

Deterministic Static Findings:
{json.dumps(findings[:10], indent=2)}

Complexity & Metrics:
- Cyclomatic Complexity: {metrics.get('avg_complexity', 1)}
- Maintainability Index: {metrics.get('maintainability_index_avg', 80)}

Provide an insightful, helpful review in JSON format with:
1. "summary": 2-3 sentences overview of architecture, bugs, and security.
2. "ai_score": An integer score out of 100 representing overall code health.
3. "suggestions": A list of items, each with:
   - "category": ("Security", "Code Quality", "Performance", or "Maintainability")
   - "severity": ("Critical", "Warning", or "Informational")
   - "title": Short descriptive title
   - "description": Explanation
   - "recommendation": Concrete fix
4. "improved_code": Clean refactored version of the code.

Output strictly valid JSON with no markdown backticks."""

    # Fast working models
    models = ["gemini-3.8-flash", "gemini-flash-latest"]

    last_error = ""
    for target_model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={api_key}"
        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.2,
                            "responseMimeType": "application/json"
                        }
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    candidate = data.get("candidates", [{}])[0]
                    content_text = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                    if content_text:
                        raw = content_text.strip()
                        if raw.startswith("```"):
                            raw = raw.strip("`")
                            if raw.startswith("json"):
                                raw = raw[4:]
                            raw = raw.strip()
                        parsed = json.loads(raw)
                        return {
                            "available": True,
                            "ran": True,
                            "model": target_model,
                            "summary": parsed.get("summary", "Analysis completed."),
                            "ai_score": parsed.get("ai_score", 85),
                            "suggestions": parsed.get("suggestions", []),
                            "improved_code": parsed.get("improved_code", ""),
                            "error": None
                        }
                elif resp.status_code == 404:
                    # Model not available, try next model
                    last_error = f"Model {target_model} not available (HTTP 404)"
                    continue
                else:
                    last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            last_error = str(e)
            continue

    return {
        "available": True,
        "ran": False,
        "error": last_error,
        "note": f"Gemini review encountered: {last_error}"
    }
