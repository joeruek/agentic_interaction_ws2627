import json
import re
import urllib.error
import urllib.request
from datetime import date
from typing import Any

from custom_packages.model_config import Config
from custom_packages.tool import ToolOutcome

HTTP_TIMEOUT_S = 10
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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
