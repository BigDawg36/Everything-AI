"""Model providers. The rest of Koa only talks to `make_provider()` and the `Provider` interface."""

from .base import Provider, ProviderError, Reply


def make_provider(config: dict) -> Provider:
    name = config["model"]["provider"]
    if name == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(config["model"])
    raise ValueError(f"Unknown model provider in config.toml: {name!r}")


__all__ = ["Provider", "ProviderError", "Reply", "make_provider"]
