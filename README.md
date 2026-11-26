# TraceLens

> Turn noisy application logs into a clear incident trail.

Developers spend too long scanning large log files to find the event sequence, likely failure point, and next useful debugging step.

## Why this project

Individual developers and small engineering teams debugging local applications.

TraceLens is a portfolio project focused on a narrow, demonstrable workflow: useful AI assistance with visible evidence, predictable limits, and a clear local-first story.

## Product snapshot

- **Input:** Plain-text application logs and an optional short incident question.
- **Output:** Timeline, likely error cluster, cited log lines, and suggested next diagnostic checks clearly marked as hypotheses.
- **MVP:** Ingest a local log file, normalize common timestamp and severity formats, group related events, summarize the incident timeline with an LLM, and link every observation to exact line numbers.

## Planned architecture

CLI accepts a path and optional question. A bounded reader enforces size limits and redacts common secrets before model calls. Parsers normalize timestamps/levels while preserving original line numbers. Deterministic grouping selects relevant windows. The summarizer emits schema-validated claims, each with line references. Output supports readable Markdown and JSON. The tool never executes suggested commands.

## Current status

**Planning scaffold.** The product requirements, design, project skill, and agent guidance are in place. Application implementation has not started.

## Getting started

The MVP is planned for Python 3.11+. Clone this repository and review the product and design docs before implementation. Runtime setup instructions will be added with the first working release.

For local LLM configuration, copy the variable names from .env and add your own values. .env is intentionally ignored by Git; never commit API keys.

## Roadmap

1. Implement the smallest end-to-end MVP described in the PRD.
2. Add representative fixtures and quality checks.
3. Document setup, limitations, and a short demo.
4. Revisit optional integrations only when they solve a demonstrated need.

## Safety and privacy

Secrets in logs, malformed formats, hallucinated causes, huge files, and accidental destructive remediation suggestions.

The design defaults to local processing where practical and minimizes what is sent to external model providers. Do not use real sensitive data in examples or screenshots.

## Project documents

- [Product requirements](docs/PRD.md)
- [Technical design](docs/DESIGN.md)
- [Project skill](.agents/skills/tracelens/SKILL.md)
- [Agent guidance](AGENTS.md)

## License

License not selected yet.
