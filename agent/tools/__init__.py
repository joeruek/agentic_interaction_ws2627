"""
Tools schemas the model can call:
a schema for the model plus a Python implementation.
"""

from typing import Any

from custom_packages.tool import Tool

from .functions import get_calendar_day

TOOLS_SCHEMAS: dict[str, Tool] = {
    "get_calendar_day": Tool(
        description={
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


def get_tool_descriptions() -> list[dict[str, Any]]:
    return [tool.description for tool in TOOLS_SCHEMAS.values()]
