"""
Tools schemas the model can call:
a schema for the model plus a Python implementation.
"""

from openai.types.chat import ChatCompletionFunctionToolParam

from custom_packages.tool import Tool

from .functions import (
    get_calendar_day,
    get_connections,
    get_context,
    get_data_coverage,
    get_weather,
)

DATE_DESCRIPTION = (
    "Day in ISO format YYYY-MM-DD, e.g. 2026-10-29. Convert dates like 29.10.2026 or "
    "'29 Oct 2026' to this format. For relative dates (today, tomorrow) get the current "
    "date from get_context first."
)
CITY_DESCRIPTION = (
    "City name: the German name for German cities, the English name for all other cities. "
    "Umlauts become ae/oe/ue/ss, other accents are dropped, spaces become '-'. "
    "Examples: München/Munich -> 'muenchen', Köln/Cologne -> 'koeln', "
    "New York -> 'new-york', Kraków -> 'krakow'."
)

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
                        "date": {"type": "string", "description": DATE_DESCRIPTION},
                    },
                    "required": ["date"],
                },
            },
        },
        run=get_calendar_day,
    ),
    "get_connections": Tool(
        description={
            "type": "function",
            "function": {
                "name": "get_connections",
                "description": (
                    "Return the train connections from one city to another on one day (departure "
                    "and arrival time, train, number of changes, price). Use this when the user asks "
                    "how to get or travel somewhere, or about trains or connections. If the user does "
                    "not say where they start, call get_context and use their home city. If there is "
                    "no data, the result says so; **never invent connections**."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "from": {"type": "string", "description": CITY_DESCRIPTION},
                        "to": {"type": "string", "description": CITY_DESCRIPTION},
                        "date": {"type": "string", "description": DATE_DESCRIPTION},
                    },
                    "required": ["from", "to", "date"],
                },
            },
        },
        run=get_connections,
    ),
    "get_context": Tool(
        description={
            "type": "function",
            "function": {
                "name": "get_context",
                "description": (
                    "Return the user's current situation: the current date and time ('now'), home "
                    "city, quiet hours and hints about the schedule. Call this before working out "
                    "relative dates like 'today' or 'tomorrow', or when the user does not say where "
                    "they start from."
                ),
                "parameters": {"type": "object", "properties": {}},
            },
        },
        run=get_context,
    ),
    "get_data_coverage": Tool(
        description={
            "type": "function",
            "function": {
                "name": "get_data_coverage",
                "description": (
                    "Return which cities (city name -> display name), train routes and date range "
                    "the data covers. Call this when unsure which city name to use, or after a "
                    "not_found result to check whether the city or route exists at all. A listed "
                    "city, route or date does not mean weather or connections exist for every day."
                ),
                "parameters": {"type": "object", "properties": {}},
            },
        },
        run=get_data_coverage,
    ),
    "get_weather": Tool(
        description={
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": (
                    "Return the weather forecast for one city on one day (temperature in °C, "
                    "condition, rain probability, wind in km/h). Use this when the user asks about "
                    "the weather or whether they need an umbrella, warm clothes, etc. If there is no "
                    "data, the result says so; **never invent weather values**."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": CITY_DESCRIPTION},
                        "date": {"type": "string", "description": DATE_DESCRIPTION},
                    },
                    "required": ["city", "date"],
                },
            },
        },
        run=get_weather,
    ),
}


def get_tool_descriptions() -> list[ChatCompletionFunctionToolParam]:
    return [tool.description for tool in TOOLS_SCHEMAS.values()]


def get_schemas() -> dict[str, Tool]:
    return TOOLS_SCHEMAS
