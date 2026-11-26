---
name: tracelens
description: Project-specific guidance for working on TraceLens.
---

# TraceLens project skill

When helping with TraceLens, preserve original line numbers and distinguish observed facts from hypotheses. Parse and filter locally before sending minimal redacted context to any model. Bound input size. Never execute commands or apply fixes automatically. Keep the CLI useful without an LLM.

## Before changing code

- Read docs/PRD.md, docs/DESIGN.md, and AGENTS.md.
- Prefer the smallest complete implementation of the documented MVP.
- Update documentation when behavior, limitations, or data handling changes.
- Do not add dependencies or services without a concrete MVP need.
