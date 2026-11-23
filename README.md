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
uv run python -m agent "How do I get to Munich on 29 Oct 2026, and do I need an umbrella?"
```

The answer is printed to stdout with exit code 0. Errors go to stderr: exit code 1 if the run
failed (model call failed or step limit reached), 2 for a usage or configuration error.

## How the loop works

Each step is one model call. If the model requests tools, they are executed and their results are
sent back to the model in the next step.

The run ends when the model answers without requesting a tool, or as an error after `max_steps`
(default: 8) steps without an answer.

Errors a tool reports (invalid date, invalid or unknown city, no data for a day, HTTP failure,
malformed arguments, unknown tool) are passed back to the model as the tool result instead of
aborting the run.

The system prompt is in `agent/SYSTEM_PROMPT.md`.

After the answer (or the error), a token summary is printed to **stderr**, so stdout stays the
answer only:

```
Tokens used: 3412 | remaining this minute: 4588
```

`used` is the sum of `usage.total_tokens` over all model calls of the run. `remaining` is the
`x-ratelimit-remaining-tokens` response header of the last model call (Groq's free tier: 8000
tokens per minute, refilled continuously, so it is a snapshot). No extra API call is made. Providers
that do not send the header show `unknown`. Both values are also logged in `run_end`.

## Tools

All data is read via HTTP GET from `DATA_BASE_URL`. HTTP 404 means "no data" and is returned to the
model as a `not_found` result, never as a crash.

| Tool                | Reads (under `DATA_BASE_URL`)     | Used for                                                                    |
| ------------------- | --------------------------------- | --------------------------------------------------------------------------- |
| `get_calendar_day`  | `calendar/{date}.json`            | appointments of one day                                                     |
| `get_weather`       | `weather/{city}/{date}.json`      | forecast for one city and day (temperature, condition, rain, wind)          |
| `get_connections`   | `transit/{from}/{to}/{date}.json` | train connections between two cities on one day                             |
| `get_context`       | `context.json`                    | current date/time, home city, quiet hours (relative dates, unknown start)   |
| `get_data_coverage` | `index.json`                      | which cities, routes and date range exist (`endpoints`, `version` left out) |

Weather and connections exist only for some days; a city or day listed by `get_data_coverage` does
not guarantee data for every day.

### City names

The data repo identifies cities by a short name (`ulm`, `muenchen`) but defines no rule for other
cities. This project uses the following convention:

- German cities by their German name, all other cities by their English name
- lowercase; umlauts become `ae`/`oe`/`ue`/`ss`, other accents are dropped (`Kraków` → `krakow`)
- spaces become `-` (`New York` → `new-york`)

The model is told this rule in the tool descriptions (`CITY_DESCRIPTION`). The tool functions only
convert the spelling (`_normalize_city`); they do not translate names, so `Munich` becomes `munich`
and returns `not_found`. That result tells the model to check `get_data_coverage` for the valid names
and retry. Names that cannot be turned into a valid short name (e.g. containing `/` or `.`) are
rejected as `invalid_input`.

## Adding a tool

1. Write the function in `agent/tools/functions.py`. It takes `(config: Config, arguments: dict)`
   and returns a `ToolOutcome`:
   - `content`: what the model sees (include an `error` key on failure)
   - `status`: `success`, `not_found`, `invalid_input` or `failed`
   - `summary`: extra fields for the log
   - `message`: one line for the log

   Reuse the helpers: `_fetch_json(url, label, not_found=...)` for the HTTP request and error
   handling, `_validate_date` for `YYYY-MM-DD` arguments, `_normalize_city` for city arguments.
   A tool without arguments still takes `arguments` (name it `_arguments`).

2. Register it in `TOOLS_SCHEMAS` in `agent/tools/tool_schema.py` with a `Tool(description=..., run=...)`.
   The description is the OpenAI function-calling schema (name, purpose, JSON-schema parameters);
   its `name` must match the dictionary key. Use `DATE_DESCRIPTION` / `CITY_DESCRIPTION` for date and
   city parameters; a tool without arguments uses `{"type": "object", "properties": {}}`.
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

- `task` is the step (`run_start`, `llm_request`, `llm_response`, `tool_call`, `tool_result`, `error`,
  `run_end`);
- `options.status` is `success`, `not_found`, `invalid_input` or `failed`
- `level` (`INFO`, `WARNING`, `ERROR`, `ERROR`; a line without status is `INFO`, an unknown status `WARNING`).
- The last line of a run is `run_end`, and its `options.status` shows whether the run ended with an answer (`success`) or an error (`failed`).
- Hitting the step limit is also logged as `error` with `error_type: StepLimit`.

## Dependencies

Managed with uv. After changing dependencies, regenerate `requirements.txt`:

```bash
uv export --no-dev --no-hashes -o requirements.txt
```
