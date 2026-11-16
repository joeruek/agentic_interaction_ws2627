"""Entry point: python -m agent "<question>"."""

import sys
import time

from custom_packages.jsonl_logger import RunLogger
from custom_packages.model_config import ConfigError

from .config import REPO_ROOT, load_config
from .loop import AgentError, run

LOG_DIR = REPO_ROOT / "logs"


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

    logger = RunLogger(log_dir=LOG_DIR)
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
