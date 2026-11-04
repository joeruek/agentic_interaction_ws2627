"""Entry point: python -m agent "<question>"."""

import sys
import time

from .config import ConfigError, load_config
from .logging_jsonl import RunLogger
from .loop import AgentError, run


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print('usage: python -m agent "<question>"', file=sys.stderr)
        return 2
    question = sys.argv[1]

    try:
        config = load_config()
    except ConfigError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    logger = RunLogger()
    started = time.monotonic()
    logger.log(
        "run_start",
        "Run started",
        question=question,
        model=config.model,
        base_url=config.base_url,
    )
    try:
        answer = run(config, question, logger)
        logger.log(
            "run_end",
            "Run finished",
            status="success",
            duration_ms=round((time.monotonic() - started) * 1000),
            answer_preview=answer[:200],
        )
    except AgentError as err:
        logger.log(
            "run_end",
            "Run failed",
            status="failed",
            duration_ms=round((time.monotonic() - started) * 1000),
            detail=str(err),
        )
        print(f"error: {err}", file=sys.stderr)
        return 1
    finally:
        logger.close()

    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
