# Agent instructions

You are the TraceLens project agent. Build a safe, evidence-linked log analysis CLI. Read docs/PRD.md and docs/DESIGN.md before implementation. Parsing, redaction, limits, and line references must be deterministic. LLM output is advisory and schema-validated. Never commit .env or sample logs containing secrets.

## Repository conventions

- Treat docs/PRD.md as the scope boundary and docs/DESIGN.md as the current technical plan.
- Keep changes focused and explain any departure from those documents.
- Do not add secrets, private user data, or generated large artifacts.
- Do not claim features work until they are implemented and verified.

## Current owner preference

Do not add or run tests or make live model calls unless the owner requests them. Keep the untested status visible in README and STATUS.md until actual verification occurs. Synthetic examples are allowed; never commit user input or real personal data.
