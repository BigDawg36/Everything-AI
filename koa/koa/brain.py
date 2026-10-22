"""The brain: one conversation loop shared by every way in (typed, spoken, heartbeat)."""

from typing import Callable

from .providers import Provider, ProviderError, Reply


class Brain:
    def __init__(self, provider: Provider, system_prompt: str):
        self.provider = provider
        self.system_prompt = system_prompt
        self.history: list[dict] = []

    def take_turn(self, user_text: str, on_text: Callable[[str], None] | None = None) -> Reply:
        """Run one turn. On failure, the user's turn is rolled back so history stays valid."""
        self.history.append({"role": "user", "content": user_text})
        try:
            reply = self.provider.send(self.system_prompt, self.history, on_text=on_text)
        except ProviderError:
            self.history.pop()
            raise
        if reply.stop_reason == "refusal" or not reply.text:
            # Don't keep a turn the model declined or left empty; it would poison later turns.
            self.history.pop()
            return reply
        self.history.append({"role": "assistant", "content": reply.text})
        return reply
