"""Claude via the official Anthropic SDK."""

from typing import Callable

import anthropic

from .base import ProviderError, Reply

FALLBACK_BETA = "server-side-fallback-2026-07-01"
NO_KEY_MESSAGE = "I can't reach my brain: the API key is missing or invalid. Check ANTHROPIC_API_KEY in koa/.env."


class AnthropicProvider:
    def __init__(self, model_config: dict):
        self.model = model_config["name"]
        self.effort = model_config.get("effort", "medium")
        self.max_tokens = model_config.get("max_tokens", 16000)
        self.refusal_fallback = model_config.get("refusal_fallback", True)
        # Reads ANTHROPIC_API_KEY (or an `ant auth login` profile). Retries 429/5xx twice.
        self.client = anthropic.Anthropic(
            timeout=model_config.get("timeout_seconds", 90), max_retries=2
        )

    def send(self, system, messages, on_text: Callable[[str], None] | None = None) -> Reply:
        params = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=messages,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
        )
        if self.refusal_fallback:
            params.update(betas=[FALLBACK_BETA], fallbacks="default")

        try:
            with self.client.beta.messages.stream(**params) as stream:
                for text in stream.text_stream:
                    if on_text:
                        on_text(text)
                final = stream.get_final_message()
        except anthropic.AuthenticationError:
            raise ProviderError(NO_KEY_MESSAGE, retryable=False)
        except TypeError as e:
            # The SDK raises TypeError before sending when no credentials are configured at all.
            if "authentication" not in str(e):
                raise
            raise ProviderError(NO_KEY_MESSAGE, retryable=False)
        except anthropic.RateLimitError:
            raise ProviderError("I'm being rate limited. Give me a minute and try again.")
        except anthropic.APIConnectionError:
            raise ProviderError("I can't reach the model right now. Check your internet connection and try again.")
        except anthropic.APIStatusError as e:
            if e.status_code >= 500:
                raise ProviderError("The model service is having trouble. Try again in a moment.")
            raise ProviderError(f"The model rejected that request ({e.status_code}): {e.message}", retryable=False)

        if final.stop_reason == "refusal":
            return Reply(
                text="I can't help with that one. Try rephrasing, or ask me something else.",
                stop_reason="refusal",
            )

        text = "".join(block.text for block in final.content if block.type == "text")
        return Reply(
            text=text,
            stop_reason=final.stop_reason or "end_turn",
            input_tokens=final.usage.input_tokens,
            output_tokens=final.usage.output_tokens,
        )
