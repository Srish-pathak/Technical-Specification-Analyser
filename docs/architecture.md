# Architecture notes (Phases 2-4)

## Severity rationale
| Level | Meaning | Examples |
|---|---|---|
| Critical | Certain to break or directly exploitable | reserved (no rule assigns it yet) |
| High | Unparsable code, or dangerous construct | syntax error, `eval(var)`, `shell=True` with variable input |
| Medium | Likely defect / risky pattern | bare except, mutable default, hardcoded secret, unsafe deserialisation, CC > 20 |
| Low | Maintainability/style | unused import/variable, CC 11-20, long function |
| Informational | Observation | naming conventions |

Complexity is a maintainability signal rather than a defect, so it is capped at Low/Medium except CC > 30.

## Why static analysis comes first
The AI agents (Phase 5) receive only these structured findings and extracted structure as evidence; they may
interpret them but not invent locations. Deterministic findings keep `source != ai_agent` end to end.

## Security model for inputs
Validate extension, MIME, size, encoding, binary content; reject unsafe ZIP paths; bound declared and actual
decompressed sizes; skip symlinks/encrypted/duplicate members; external tools run via argument lists
(`shell=False`) on a private temp copy with numbered file names, with a timeout.
Tests prove: a canary file/import is never triggered by analysis; the app source contains no
`eval/exec/compile/__import__/os.system`; `subprocess` is confined to `tool_runner.py` with `shell=False`.
