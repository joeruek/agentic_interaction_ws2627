"""Token bookkeeping for one run: tokens used and the provider's remaining per-minute budget."""

from collections.abc import Mapping
from dataclasses import dataclass

from openai.types import CompletionUsage

# Sent by Groq (and some other OpenAI-compatible providers) on every chat completion;
# the value already accounts for the request it is attached to.
REMAINING_TOKENS_HEADER = "x-ratelimit-remaining-tokens"


@dataclass
class TokenUsage:
    used: int = 0  # sum of total_tokens over all model calls of the run
    remaining: int | None = None  # remaining tokens this minute, as of the last call

    def add(self, usage: CompletionUsage | None, headers: Mapping[str, str]) -> None:
        """Record one model call: its token usage (if any) and the rate-limit header (if sent)."""
        if usage is not None:
            self.used += usage.total_tokens
        raw = headers.get(REMAINING_TOKENS_HEADER)
        if raw is not None:
            try:
                self.remaining = int(raw)
            except ValueError:
                pass

    def summary(self) -> str:
        rest = self.remaining if self.remaining is not None else "unknown"
        return f"Tokens used: {self.used} | remaining this minute: {rest}"
