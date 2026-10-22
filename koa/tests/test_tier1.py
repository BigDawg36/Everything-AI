"""Tier 1 checks. Run from koa/:  python -m unittest discover tests"""

import unittest
from types import SimpleNamespace
from unittest import mock

import anthropic
import httpx2 as httpx

from koa.brain import Brain
from koa.config import load_config
from koa.persona import build_system_prompt
from koa.providers import ProviderError, Reply
from koa.providers.anthropic_provider import AnthropicProvider


class FakeProvider:
    """Records what it was sent; replies with scripted results."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def send(self, system, messages, on_text=None):
        self.calls.append([dict(m) for m in messages])
        result = self.script.pop(0)
        if isinstance(result, Exception):
            raise result
        if on_text:
            on_text(result.text)
        return result


class BrainTests(unittest.TestCase):
    def test_history_is_sent_back_every_turn(self):
        provider = FakeProvider([Reply("Nice to meet you, Mike."), Reply("Your name is Mike.")])
        brain = Brain(provider, "system")
        brain.take_turn("My name is Mike.")
        brain.take_turn("What's my name?")
        second_call = provider.calls[1]
        self.assertEqual([m["role"] for m in second_call], ["user", "assistant", "user"])
        self.assertEqual(second_call[0]["content"], "My name is Mike.")

    def test_streams_text_to_callback(self):
        chunks = []
        Brain(FakeProvider([Reply("hello")]), "s").take_turn("hi", on_text=chunks.append)
        self.assertEqual(chunks, ["hello"])

    def test_failed_turn_is_rolled_back_and_next_turn_works(self):
        provider = FakeProvider([ProviderError("offline"), Reply("back online")])
        brain = Brain(provider, "s")
        with self.assertRaises(ProviderError):
            brain.take_turn("first try")
        self.assertEqual(brain.history, [])
        brain.take_turn("second try")
        self.assertEqual(len(brain.history), 2)

    def test_refusal_is_not_kept_in_history(self):
        brain = Brain(FakeProvider([Reply("declined", stop_reason="refusal")]), "s")
        brain.take_turn("x")
        self.assertEqual(brain.history, [])


class PersonaTests(unittest.TestCase):
    def test_prompt_carries_name_owner_and_rails(self):
        prompt = build_system_prompt(load_config())
        self.assertIn("You are Koa", prompt)
        self.assertIn("Mike", prompt)
        self.assertIn("explicit approval", prompt)
        self.assertNotIn("—", prompt)  # no em dashes


def _fake_stream(texts, final):
    stream = mock.MagicMock()
    stream.__enter__.return_value = stream
    stream.text_stream = iter(texts)
    stream.get_final_message.return_value = final
    return stream


def _final(text, stop_reason="end_turn"):
    return SimpleNamespace(
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=10, output_tokens=5),
    )


class AnthropicProviderTests(unittest.TestCase):
    def setUp(self):
        with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test"}):
            self.provider = AnthropicProvider(load_config()["model"])
        self.stream = mock.MagicMock()
        self.provider.client = mock.MagicMock()
        self.provider.client.beta.messages.stream = self.stream

    def test_request_shape_and_streaming(self):
        self.stream.return_value = _fake_stream(["Hel", "lo"], _final("Hello"))
        chunks = []
        reply = self.provider.send("sys", [{"role": "user", "content": "hi"}], on_text=chunks.append)
        self.assertEqual(reply.text, "Hello")
        self.assertEqual(chunks, ["Hel", "lo"])
        kwargs = self.stream.call_args.kwargs
        self.assertEqual(kwargs["model"], "claude-opus-5-5")
        self.assertEqual(kwargs["thinking"], {"type": "adaptive"})
        self.assertEqual(kwargs["output_config"], {"effort": "medium"})
        self.assertEqual(kwargs["fallbacks"], "default")

    def test_refusal_becomes_plain_message(self):
        self.stream.return_value = _fake_stream([], _final("", stop_reason="refusal"))
        reply = self.provider.send("sys", [{"role": "user", "content": "x"}])
        self.assertEqual(reply.stop_reason, "refusal")

    def test_network_failure_becomes_friendly_error(self):
        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        self.stream.side_effect = anthropic.APIConnectionError(request=request)
        with self.assertRaises(ProviderError) as ctx:
            self.provider.send("sys", [{"role": "user", "content": "x"}])
        self.assertIn("internet", ctx.exception.message)

    def test_bad_key_is_not_retryable(self):
        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        response = httpx.Response(401, request=request)
        self.stream.side_effect = anthropic.AuthenticationError("bad key", response=response, body=None)
        with self.assertRaises(ProviderError) as ctx:
            self.provider.send("sys", [{"role": "user", "content": "x"}])
        self.assertFalse(ctx.exception.retryable)

    def test_missing_credentials_is_friendly(self):
        self.stream.side_effect = TypeError('"Could not resolve authentication method."')
        with self.assertRaises(ProviderError) as ctx:
            self.provider.send("sys", [{"role": "user", "content": "x"}])
        self.assertIn("ANTHROPIC_API_KEY", ctx.exception.message)


if __name__ == "__main__":
    unittest.main()
