"""The provider seam: one small interface every model backend implements.

Messages use a neutral shape, {"role": "user" | "assistant", "content": str},
so swapping Claude for another provider never touches the brain or the CLI.
"""

from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass
class Reply:
    text: str
    stop_reason: str = "end_turn"
    input_tokens: int = 0
    output_tokens: int = 0


class ProviderError(Exception):
    """A failure the user should hear about in plain language. `message` is safe to show."""

    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message)
        self.message = message
        self.retryable = retryable


class Provider(Protocol):
    def send(
        self,
        system: str,
        messages: list[dict],
        on_text: Callable[[str], None] | None = None,
    ) -> Reply:
        """Send the whole conversation, stream text chunks to `on_text`, return the final reply."""
        ...
