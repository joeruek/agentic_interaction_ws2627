# agentic-interaction-ws2627

Tool-calling agent for the *Agentic Interaction* exercises (Ulm University, WS 2026/27).
Exercise 1: the model answers calendar questions by calling a tool (model → tool → model).

## Setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env   # then fill in OPENAI_API_KEY
```

Configuration is read from the environment; `.env` is only a fallback (environment variables win).

| Variable | Meaning |
|---|---|
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint (default: Groq, `https://api.groq.com/openai/v1`) |
| `MODEL` | model name (default: `openai/gpt-oss-20b`) |
| `OPENAI_API_KEY` | API key |
| `DATA_BASE_URL` | mock data, `https://jhbelz.github.io/agentic-interaction-data/v1` |

## Run

```bash
uv run python -m agent "Was steht am 29.10.2026 im Kalender?"
```

The answer is printed to stdout (exit code 0). Errors go to stderr with a non-zero exit code.

## Layout

| File | Purpose |
|---|---|
| `agent/__main__.py` | entry point |
| `agent/config.py` | environment / `.env` loading |
| `agent/tools.py` | tool registry; `get_calendar_day` reads `{DATA_BASE_URL}/calendar/{YYYY-MM-DD}.json` |
| `agent/loop.py` | bounded loop: model → tools → model, at most 5 steps |
| `agent/logging_jsonl.py` | per-run JSONL logger |

## Logs

Each run writes `logs/<UTC timestamp>-<run id>.jsonl` (not committed). One JSON object per line:

```json
{"timestamp": "...", "level": "INFO", "run_id": "bd13ab", "task": "tool_result", "tool": "get_calendar_day", "options": {"status": "success", "events": 3}, "message": "3 event(s) on 2026-10-29"}
```

`task` is the step (`run_start`, `llm_request`, `llm_response`, `tool_call`, `tool_result`, `run_end`);
`options.status` is `success`, `not_found`, `invalid_input` or `failed` and determines `level`.

## Dependencies

Managed with uv. After changing dependencies, regenerate `requirements.txt`:

```bash
uv export --no-dev --no-hashes -o requirements.txt
```
