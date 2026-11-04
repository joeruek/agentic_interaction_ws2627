"""Tools the model can call: a schema for the model plus a Python implementation."""

import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .config import Config

HTTP_TIMEOUT_S = 10
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class ToolOutcome:
    content: dict[str, Any]  # what the model sees
    status: str  # success | not_found | invalid_input | failed
    summary: dict[str, Any] = field(default_factory=dict)  # what the log sees
    message: str = ""


def get_calendar_day(config: Config, arguments: dict[str, Any]) -> ToolOutcome:
    day = arguments.get("date")
    try:
        if not isinstance(day, str) or not ISO_DATE.match(day):
            raise ValueError
        date.fromisoformat(day)
    except ValueError:
        return ToolOutcome(
            content={"error": f"invalid date {day!r}; expected YYYY-MM-DD"},
            status="invalid_input",
            message=f"Invalid date argument {day!r}",
        )

    url = f"{config.data_base_url}/calendar/{day}.json"
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_S) as response:
            data = json.load(response)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return ToolOutcome(
                content={
                    "date": day,
                    "events": [],
                    "note": "no calendar data for this date",
                },
                status="not_found",
                summary={"http_status": 404, "events": 0},
                message=f"No calendar data for {day}",
            )
        return ToolOutcome(
            content={"error": f"calendar service returned HTTP {err.code}"},
            status="failed",
            summary={"http_status": err.code},
            message=f"HTTP {err.code} while fetching {day}",
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
        return ToolOutcome(
            content={"error": f"could not read calendar: {err}"},
            status="failed",
            summary={"error_type": type(err).__name__},
            message=f"Fetching {day} failed: {err}",
        )

    events = data.get("events", [])
    return ToolOutcome(
        content=data,
        status="success",
        summary={"http_status": 200, "events": len(events)},
        message=f"{len(events)} event(s) on {day}",
    )


@dataclass(frozen=True)
class Tool:
    schema: dict[str, Any]  # OpenAI function-calling description
    run: Callable[[Config, dict[str, Any]], ToolOutcome]


TOOLS: dict[str, Tool] = {
    "get_calendar_day": Tool(
        schema={
            "type": "function",
            "function": {
                "name": "get_calendar_day",
                "description": (
                    "Return all appointments of one calendar day (title, start and end time, "
                    "location). Use this whenever the user asks what is scheduled on a specific date."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The day to look up in ISO format YYYY-MM-DD, e.g. 2026-10-29. "
                            "Convert dates like 29.10.2026 to this format.",
                        }
                    },
                    "required": ["date"],
                },
            },
        },
        run=get_calendar_day,
    )
}


def tool_schemas() -> list[dict[str, Any]]:
    return [tool.schema for tool in TOOLS.values()]
