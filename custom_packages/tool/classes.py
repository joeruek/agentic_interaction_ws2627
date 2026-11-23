"""Holds the tool classes for agents to use"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from openai.types.chat import ChatCompletionFunctionToolParam

from custom_packages.model_config.classes import Config


@dataclass
class ToolOutcome:
    content: dict[str, Any]  # what the model sees
    status: str  # success | not_found | invalid_input | failed
    summary: dict[str, Any] = field(default_factory=dict)  # what the log sees
    message: str = ""


@dataclass(frozen=True)
class Tool:
    description: ChatCompletionFunctionToolParam  # OpenAI function-calling description
    run: Callable[[Config, dict[str, Any]], ToolOutcome]
