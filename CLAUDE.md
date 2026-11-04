# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working agreement

- **Never implement directly.** For any task, first present a plan and the intended structure, and explain the implementation details. The user will then ask questions: answer them first, and **wait for an explicit "go" before writing or changing code.**
- Package management is **uv only** (`uv add`, `uv remove`, `uv sync`). No `pip install`. Remove any dependency that is no longer used.
- Keep `requirements.txt` always up to date with the project's dependencies. Regenerate it whenever dependencies change (e.g. `uv export --no-dev --no-hashes -o requirements.txt`).

## Project context

Coursework repo for "Agentic Interaction" (Ulm University, WS 2026/27). This is a **multi-step project that grows over several exercise sheets**; each sheet's task description covers only that step and is not the full project frame. Design so later exercises can build on earlier ones rather than treating the current sheet as the final scope.

The sheets are kept in `temp/` (gitignored). The Moodle interface specification is binding but is not in the repo; the data repo README (github.com/jhbelz/agentic-interaction-data) documents endpoints and examples.

### Exercise 1 — "First Tool Call" (due Tue 3 Nov 2026, 12:00; repo state is assessed)

An agent answers a calendar question by having the model call one tool (model → tool → model, a single pass).

- Repo must be public on GitHub, named `agentic-interaction-ws2627`, with `README.md`, `requirements.txt`, `.gitignore`, and an `agent/` package containing `__main__.py` (at the repo root), run as `python -m agent "<question>"`.
- One tool reads `{DATA_BASE_URL}/calendar/{YYYY-MM-DD}.json` (e.g. `https://jhbelz.github.io/agentic-interaction-data/v1/calendar/2026-10-29.json`); name, purpose and parameters are passed to the model as a description. Must work for every day of the mock calendar. Answer goes to stdout, exit code 0.
- Use the `openai` library or plain HTTP, **not** the `groq` package, so the agent works against any OpenAI-compatible endpoint. Default model: `openai/gpt-oss-20b` via Groq (`https://api.groq.com/openai/v1`).
- Config comes from the environment with a `.env` file as fallback (environment variables take precedence): `OPENAI_BASE_URL`, `MODEL`, `OPENAI_API_KEY`, `DATA_BASE_URL` (`https://jhbelz.github.io/agentic-interaction-data/v1`). Endpoint, model and data URL must not be hardcoded.
- Every run writes its own JSONL log file (e.g. `logs/`) with the fields from the Moodle spec.
- Never commit `.env`, API keys, or logs (add `.env` and `logs/` to `.gitignore`; currently only `temp/`, venvs and build artifacts are ignored).

## Current state and commands

Exercise 1 is implemented. The root-level `agent/` package is the app (uv project with `package = false`, no `src/`, no build backend); dependencies are `openai` and `python-dotenv`. No tests, linter or formatter are configured.

- `agent/config.py` (env + `.env`), `agent/tools.py` (tool registry; each tool returns a `ToolOutcome` with model-facing `content`, a `status`, and a log `summary`), `agent/loop.py` (bounded model → tools → model loop, `max_steps=5`), `agent/logging_jsonl.py` (`RunLogger`, one file per run in `logs/`).
- Log lines: `{timestamp, level, run_id, task, tool, options, message}`; `task` is the step name, `options.status` (`success`/`not_found`/`invalid_input`/`failed`) determines `level`. The Moodle log field spec was not available, so this format is our own choice.
- Python 3.13 (`.python-version`).
- `uv sync` — create/refresh `.venv`
- `uv run python -m agent "<question>"` — run the agent
