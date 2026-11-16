"""The agent loop: ask the model, run requested tools, feed results back, repeat until it answers."""

import json
import time
from os import path
from typing import Any

from openai import OpenAI, OpenAIError

from custom_packages.jsonl_logger import RunLogger
from custom_packages.model_config import Config
from custom_packages.tool import ToolOutcome

from .tools import TOOLS_SCHEMAS, get_tool_descriptions


class AgentError(Exception):
    pass


def run(config: Config, question: str, logger: RunLogger) -> str:
    # Model definition
    client = OpenAI(base_url=config.base_url, api_key=config.api_key)
    # Tool definition
    schemas = get_tool_descriptions()
    # Prompt definition
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": _get_system_prompt()},
        {"role": "user", "content": question},
    ]
    # Loop start
    for step in range(1, config.max_steps + 1):
        logger.log(
            "llm_request",
            "Calling model",
            step=step,
            message_count=len(messages),
            tools=[s["function"]["name"] for s in schemas],
        )
        started = time.monotonic()
        try:
            response = client.chat.completions.create(
                model=config.model, messages=messages, tools=schemas
            )
        except OpenAIError as err:
            logger.log(
                "llm_response",
                f"Model call failed: {err}",
                status="failed",
                step=step,
                error_type=type(err).__name__,
            )
            raise AgentError(f"model call failed: {err}") from err
        choice = response.choices[0]
        message = choice.message
        usage = response.usage
        logger.log(
            "llm_response",
            "Model responded",
            status="success",
            step=step,
            finish_reason=choice.finish_reason,
            tool_calls=len(message.tool_calls or []),
            tokens={
                "prompt": usage.prompt_tokens,
                "completion": usage.completion_tokens,
            }
            if usage
            else None,
            duration_ms=round((time.monotonic() - started) * 1000),
        )

        if not message.tool_calls:
            return message.content or ""

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {
                            "name": c.function.name,
                            "arguments": c.function.arguments,
                        },
                    }
                    for c in message.tool_calls
                ],
            }
        )
        for call in message.tool_calls:
            name = call.function.name
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except ValueError:
                arguments = call.function.arguments
            logger.log(
                "tool_call", "Calling tool", tool=name, step=step, arguments=arguments
            )
            started = time.monotonic()
            outcome = _execute(config, name, call.function.arguments)
            logger.log(
                "tool_result",
                outcome.message,
                tool=name,
                status=outcome.status,
                step=step,
                duration_ms=round((time.monotonic() - started) * 1000),
                **outcome.summary,
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(outcome.content),
                }
            )

    logger.log(
        "error",
        f"No final answer after {config.max_steps} steps",
        status="failed",
        error_type="StepLimit",
    )
    raise AgentError(f"no final answer after {config.max_steps} steps")


def _execute(config: Config, name: str, raw_arguments: str) -> ToolOutcome:
    tool = TOOLS_SCHEMAS.get(name)
    if tool is None:
        return ToolOutcome(
            {"error": f"unknown tool {name!r}"},
            "invalid_input",
            message=f"Unknown tool {name!r}",
        )
    try:
        arguments = json.loads(raw_arguments or "{}")
        if not isinstance(arguments, dict):
            raise TypeError
    except ValueError:
        return ToolOutcome(
            {"error": "arguments must be a JSON object"},
            "invalid_input",
            message="Unparsable tool arguments",
        )
    return tool.run(config, arguments)


def _get_system_prompt() -> str:
    sys_prompt = ""
    current_path = path.dirname(path.abspath(__file__))
    prompt_path = path.join(current_path, "SYSTEM_PROMPT.md")
    with open(prompt_path, "r") as f:
        sys_prompt = f.read()
    return sys_prompt
