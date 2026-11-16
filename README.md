# agentic-interaction-ws2627

Tool-calling agent for the _Agentic Interaction_ exercises (Ulm University, WS 2026/27).

## Setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env   # then fill in OPENAI_API_KEY
```

Configuration is read from the environment; `.env` is only a fallback (environment variables win).

| Variable          | Meaning                                                                      |
| ----------------- | ---------------------------------------------------------------------------- |
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint (default: Groq, `https://api.groq.com/openai/v1`) |
| `MODEL`           | model name (default: `openai/gpt-oss-20b`)                                   |
| `OPENAI_API_KEY`  | API key                                                                      |
| `DATA_BASE_URL`   | mock data, `https://jhbelz.github.io/agentic-interaction-data/v1`            |

## Run

```bash
uv run python -m agent "Was steht am 29.10.2026 im Kalender?"
uv run python -m agent "What is on 29 Oct 2026 and on 30 Oct 2026?"
```

The answer is printed to stdout with exit code 0. Errors go to stderr: exit code 1 if the run
failed (model call failed or step limit reached), 2 for a usage or configuration error.

## How the loop works

Each step is one model call. If the model requests tools, they are executed and their results are
sent back to the model in the next step.

The run ends when the model answers without requesting a tool, or as an error after `max_steps`
(default: 5) steps without an answer.

Errors a tool reports (invalid date, no data for a day, HTTP failure, malformed arguments, unknown
tool) are passed back to the model as the tool result instead of aborting the run.

The system prompt is in `agent/SYSTEM_PROMPT.md`.

## Layout

| File                           | Purpose                                                                         |
| ------------------------------ | ------------------------------------------------------------------------------- |
| `agent/__main__.py`            | entry point, exit codes, run start/end logging                                  |
| `agent/config.py`              | environment / `.env` loading                                                    |
| `agent/loop.py`                | agent loop: model → tools → model until an answer or the step limit             |
| `agent/SYSTEM_PROMPT.md`       | system prompt                                                                   |
| `agent/tools/__init__.py`      | tool registry (`TOOLS_SCHEMAS`): description for the model + function per tool  |
| `agent/tools/functions.py`     | tool functions; `get_calendar_day` reads `{DATA_BASE_URL}/calendar/{date}.json` |
| `custom_packages/model_config` | `Config`, `ConfigError`                                                         |
| `custom_packages/tool`         | `Tool`, `ToolOutcome`                                                           |
| `custom_packages/jsonl_logger` | `RunLogger`: per-run JSONL log file                                             |

## Adding a tool

1. Write the function in `agent/tools/functions.py`. It takes `(config: Config, arguments: dict)`
   and returns a `ToolOutcome`:
   - `content`: what the model sees (include an `error` key on failure)
   - `status`: `success`, `not_found`, `invalid_input` or `failed`
   - `summary`: extra fields for the log
   - `message`: one line for the log
2. Register it in `TOOLS_SCHEMAS` in `agent/tools/__init__.py` with a `Tool(description=..., run=...)`.
   The description is the OpenAI function-calling schema (name, purpose, JSON-schema parameters);
   its `name` must match the dictionary key.
3. If the model needs guidance on when to use it, extend `agent/SYSTEM_PROMPT.md`.

The loop picks up every registered tool automatically.

## Logs

Each run writes `logs/<UTC timestamp>-<run id>.jsonl` (not committed). One JSON object per line:

```json
{
  "timestamp": "...",
  "level": "INFO",
  "run_id": "bd13ab",
  "task": "tool_result",
  "tool": "get_calendar_day",
  "options": { "status": "success", "events": 3 },
  "message": "3 event(s) on 2026-10-29"
}
```

`task` is the step (`run_start`, `llm_request`, `llm_response`, `tool_call`, `tool_result`, `error`,
`run_end`); `options.status` is `success`, `not_found`, `invalid_input` or `failed` and determines
`level`. The last line of a run is `run_end`, and its `options.status` shows whether the run ended
with an answer (`success`) or an error (`failed`). Hitting the step limit is also logged as `error`
with `error_type: StepLimit`.

## Dependencies

Managed with uv. After changing dependencies, regenerate `requirements.txt`:

```bash
uv export --no-dev --no-hashes -o requirements.txt
```
