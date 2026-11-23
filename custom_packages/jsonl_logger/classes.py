"""One JSONL log file per run: one JSON object per line, flushed immediately."""

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Outcome of a step -> log level
LEVEL_BY_STATUS = {
    "success": "INFO",
    "not_found": "WARNING",
    "invalid_input": "ERROR",
    "failed": "ERROR",
}


class RunLogger:
    def __init__(self, log_dir: Path) -> None:
        self.run_id = uuid.uuid4().hex[:6]
        log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.path = log_dir / f"{stamp}-{self.run_id}.jsonl"
        self._file = self.path.open("a", encoding="utf-8")

    def log(
        self,
        task: str,
        message: str,
        *,
        tool: str | None = None,
        status: str | None = None,
        level: str | None = None,
        **options: Any,
    ) -> None:
        """Write one line. `task` is the step name; `status` goes into options and sets the level."""
        if status is not None:
            options = {"status": status, **options}
        if level is None:
            # No status -> plain progress line; an unknown status is suspicious -> WARNING
            level = (
                LEVEL_BY_STATUS.get(status, "WARNING") if status is not None else "INFO"
            )

        record = {
            "timestamp": datetime.now(UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": level,
            "run_id": self.run_id,
            "task": task,
            "tool": tool,
            "options": options,
            "message": message,
        }
        self._file.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()
