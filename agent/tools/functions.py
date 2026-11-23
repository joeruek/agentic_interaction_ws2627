import json
import re
import unicodedata
import urllib.error
import urllib.request
from datetime import date
from typing import Any

from custom_packages.model_config import Config
from custom_packages.tool import ToolOutcome

HTTP_TIMEOUT_S = 10
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CITY_SLUG = re.compile(r"^[a-z]+(-[a-z]+)*$")
SEPARATORS = re.compile(r"[\s_]+")
# Applied before NFKD: German umlauts are spelled out (ü -> ue, not u), and the
# listed letters have no NFKD decomposition, so the accent stripping would miss them.
LETTER_MAP = str.maketrans(
    {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "ł": "l",
        "ø": "o",
        "æ": "ae",
        "œ": "oe",
        "đ": "d",
        "ı": "i",
        "þ": "th",
    }
)


def _validate_date(day: Any) -> ToolOutcome | None:
    """Return an invalid_input outcome if `day` is not a real YYYY-MM-DD date, else None."""
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
    return None


def _normalize_city(name: Any) -> str | None:
    """
    Turn a city name into a URL slug: 'München' -> 'muenchen', 'Kraków' -> 'krakow',
    'New York' -> 'new-york'. Only the spelling is converted; choosing the German or
    English name is up to the model. Returns None if the result is not a valid slug.
    """
    if not isinstance(name, str):
        return None
    slug = name.strip().lower().translate(LETTER_MAP)
    slug = "".join(
        c for c in unicodedata.normalize("NFKD", slug) if not unicodedata.combining(c)
    )
    slug = SEPARATORS.sub("-", slug)
    return slug if CITY_SLUG.match(slug) else None


def _invalid_city(param: str, value: Any) -> ToolOutcome:
    return ToolOutcome(
        content={
            "error": f"invalid {param} {value!r}; call get_data_coverage for the valid city names"
        },
        status="invalid_input",
        message=f"Invalid {param} argument {value!r}",
    )


def _fetch_json(
    url: str, label: str, not_found: ToolOutcome | None = None
) -> dict[str, Any] | ToolOutcome:
    """
    GET `url` and return the parsed JSON object.
    On failure return a ToolOutcome instead: `not_found` for HTTP 404 (if given),
    otherwise a `failed` outcome.
    """
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_S) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        if err.code == 404 and not_found is not None:
            return not_found
        return ToolOutcome(
            content={"error": f"{label} service returned HTTP {err.code}"},
            status="failed",
            summary={"http_status": err.code},
            message=f"HTTP {err.code} while fetching {label}",
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as err:
        return ToolOutcome(
            content={"error": f"could not read {label}: {err}"},
            status="failed",
            summary={"error_type": type(err).__name__},
            message=f"Fetching {label} failed: {err}",
        )


##


def get_calendar_day(config: Config, arguments: dict[str, Any]) -> ToolOutcome:
    """
    Returns the saved events at calendar by the given day.
    Args:
        config (Config): Holds the model information(model server, model name, API key) and database
            information.

        arguments (dict[str, Any]): `date` string as key and the value should be in `YYYY-MM-DD`
            format.
    """
    day = arguments.get("date")
    if invalid := _validate_date(day):
        return invalid

    data = _fetch_json(
        f"{config.data_base_url}/calendar/{day}.json",
        "calendar",
        not_found=ToolOutcome(
            content={
                "date": day,
                "events": [],
                "note": "no calendar data for this date",
            },
            status="not_found",
            summary={"http_status": 404, "events": 0},
            message=f"No calendar data for {day}",
        ),
    )
    if isinstance(data, ToolOutcome):
        return data

    events = data.get("events", [])
    return ToolOutcome(
        content=data,
        status="success",
        summary={"http_status": 200, "events": len(events)},
        message=f"{len(events)} event(s) on {day}",
    )


##


def get_context(config: Config, _arguments: dict[str, Any]) -> ToolOutcome:
    """
    Function that is used to gather further information about user,
    if user did not provide.

    eg:
    > User: I want to go to Munchen. Check the connections please.

    > Model: User's current location is not known. Check the `context`.

    Args:
        config (Config): Holds the model information(model server, model name, API key) and database
            information.

        _arguments (dict[str, Any]): Empty dict, no argument is needed.
    """
    data = _fetch_json(f"{config.data_base_url}/context.json", "context")
    if isinstance(data, ToolOutcome):
        return data

    user_at = data.get("home", "unknown")
    user_moment = data.get("now", "unknown")
    return ToolOutcome(
        content=data,
        status="success",
        summary={"http_status": 200},
        message=f"User is on {user_moment} at {user_at}",
    )


##


def get_data_coverage(config: Config, _arguments: dict[str, Any]) -> ToolOutcome:
    """
    Reads the data repo's `index.json` and returns what the mock data covers:
    the date range, the cities (slug -> display name) and the train routes.
    The `endpoints` and `version` fields are left out; they are of no use to the model.

    Args:
        config (Config): Holds the model information(model server, model name, API key) and database
            information.

        _arguments (dict[str, Any]): Empty dict, no argument is needed.
    """
    data = _fetch_json(f"{config.data_base_url}/index.json", "data index")
    if isinstance(data, ToolOutcome):
        return data

    days = data.get("days", {})
    cities = data.get("cities", {})
    routes = data.get("routes", [])
    return ToolOutcome(
        content={"days": days, "cities": cities, "routes": routes},
        status="success",
        summary={"http_status": 200, "cities": len(cities), "routes": len(routes)},
        message=(
            f"{len(cities)} cities, {len(routes)} routes, "
            f"{days.get('first', '?')} to {days.get('last', '?')}"
        ),
    )


##


def get_connections(config: Config, arguments: dict[str, Any]) -> ToolOutcome:
    """
    Finds the train connections between two given location depending on given date.

    Args:
        config (Config): Holds the model information(model server, model name, API key) and database
            information.

        arguments (dict[str, Any]):
            > Keys: "from", "to", "date"

            > Values: city, city, date. Cities will be normalized,
                date should conform the ISO format
    """
    raw_from = arguments.get("from")
    raw_to = arguments.get("to")
    day = arguments.get("date")

    departure = _normalize_city(raw_from)
    if departure is None:
        return _invalid_city("from", raw_from)
    destination = _normalize_city(raw_to)
    if destination is None:
        return _invalid_city("to", raw_to)
    if invalid := _validate_date(day):
        return invalid

    data = _fetch_json(
        f"{config.data_base_url}/transit/{departure}/{destination}/{day}.json",
        "connections",
        not_found=ToolOutcome(
            content={
                "from": departure,
                "to": destination,
                "date": day,
                "connections": [],
                "note": (
                    "no connection data for this route and date; call get_data_coverage "
                    "to check the valid city names and routes"
                ),
            },
            status="not_found",
            summary={"http_status": 404, "connections": 0},
            message=f"No connection data from {departure} to {destination} on {day}",
        ),
    )
    if isinstance(data, ToolOutcome):
        return data

    connections = data.get("connections", [])
    return ToolOutcome(
        content=data,
        status="success",
        summary={"http_status": 200, "connections": len(connections)},
        message=f"{len(connections)} connection(s) from {departure} to {destination} on {day}",
    )


##


def get_weather(config: Config, arguments: dict[str, Any]) -> ToolOutcome:
    raw_city = arguments.get("city")
    day = arguments.get("date")

    city = _normalize_city(raw_city)
    if city is None:
        return _invalid_city("city", raw_city)
    if invalid := _validate_date(day):
        return invalid

    data = _fetch_json(
        f"{config.data_base_url}/weather/{city}/{day}.json",
        "weather",
        not_found=ToolOutcome(
            content={
                "city": city,
                "date": day,
                "note": (
                    "no weather data for this city and date; call get_data_coverage "
                    "to check the valid city names"
                ),
            },
            status="not_found",
            summary={"http_status": 404},
            message=f"No weather data on {day} for {city}",
        ),
    )
    if isinstance(data, ToolOutcome):
        return data

    weather_condition = data.get("condition", "unknown")
    return ToolOutcome(
        content=data,
        status="success",
        summary={"http_status": 200},
        message=f"Weather will be like {weather_condition} at {city} on {day}",
    )
