# TechSpecAnalyser
**A Static-Analysis-Grounded Multi-Agent System for Automated Code Review and Documentation Generation**

TechSpecAnalyser accepts source code, files and ZIP projects, performs *deterministic* static analysis, and
(in later phases) hands that evidence to specialised AI agents whose output is validated and synthesised into
reports and documentation. **Uploaded code is only parsed, never executed.**

## Status
| Component | State |
|---|---|
| Secure input (paste, file, ZIP) | Implemented, **tested** |
| Python static analysis (syntax, AST, complexity, quality, security) | Implemented, **tested** |
| Ruff / Bandit / Radon adapters | Implemented; **parsing and runner tested with fake executables and sample JSON only. Not yet run against the real tools.** |
| SQLite history + dashboard statistics | Implemented, **tested** |
| FastAPI endpoints | Written, **not yet run** (FastAPI was unavailable in the build sandbox) |
| Frontend integration | **Not started**: `frontend/index.html` is still the original prototype (fake progress bars) |
| Six AI agents, orchestrator, synthesis | Not started |
| Documentation generation, Markdown/JSON/PDF reports | Not started |
| GitHub repository review | Not started |
| PDF analysis | Out of scope for now (page stays marked unavailable) |
| Academic evaluation (A/B/C comparison) | Not started; methodology to be written, results only from real runs |

## Run the tests (no third-party packages needed)
```bash
cd backend
python -m unittest discover -s tests -t .
```
## Run the app
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload      # http://127.0.0.1:8000
```
Without an AI key the app still performs full static analysis and states that AI review is unavailable.

## Architecture (implemented part)
```
paste / file / ZIP --> file_manager / archive_manager (validate, never execute)
                   --> analysis_service
                         ast.parse -> syntax findings
                         ast_analyzer   -> functions, classes, imports, calls, docstrings
                         complexity     -> Radon if installed, else built-in McCabe (labelled)
                         quality        -> Ruff if installed, else built-in AST rules (labelled)
                         security       -> built-in AST rules + Bandit if installed (de-duplicated)
                   --> SQLite (derived results only) --> dashboard / history
```
Every finding has: finding_id, rule_id, category, severity, file_path, line_number, column_number,
description, evidence, recommended_correction, source (`static_analyzer` | `deterministic_rule` | `ai_agent` |
`human_verification`), confidence. Reports list which tools ran, which did not, and why.

## Key design decisions
* **ZIPs are read in memory, never extracted to disk**, so ZIP-slip/overwrite is impossible by construction; member
  paths are still validated, and any traversal attempt rejects the whole archive.
* **Tools are fallbacks, never faked**: if Ruff/Bandit/Radon are missing, built-ins are used and the result says so.
* **No double reporting**: built-in quality rules run only when Ruff did not; built-in security duplicates of Bandit are dropped.
* **Secrets are never echoed** into findings or the database.
* **Only Python has deterministic analysis.** Other languages are inventoried and reported as not analysed.

## Known limitations
Complexity from the built-in counter is close to, not identical with, Radon. Built-in rules are pattern-based and can
produce false positives (confidence is recorded). See `docs/phase_reports.md`.

## Reference material
The GitHub reference repositories could not be accessed during development (no network in the build sandbox), so
**no code or design was taken from them**; everything here is original.

