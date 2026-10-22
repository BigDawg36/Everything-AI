"""Text interface. Run with:  python -m koa.cli"""

import sys

from .brain import Brain
from .config import load_config, load_dotenv
from .persona import build_system_prompt
from .providers import ProviderError, make_provider

EXIT_WORDS = {"exit", "quit", "bye"}


def main() -> int:
    load_dotenv()
    config = load_config()
    name = config["assistant"]["name"]
    brain = Brain(make_provider(config), build_system_prompt(config))

    print(f"{name} is here. Type to talk; 'exit' to leave.\n")
    while True:
        try:
            user_text = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_text:
            continue
        if user_text.lower() in EXIT_WORDS:
            break

        print(f"{name.lower()} > ", end="", flush=True)
        try:
            reply = brain.take_turn(user_text, on_text=lambda t: print(t, end="", flush=True))
        except ProviderError as e:
            print(f"\n[{e.message}]\n")
            continue
        except KeyboardInterrupt:
            print("\n[stopped]\n")
            continue
        if reply.stop_reason == "refusal":
            print(reply.text, end="")
        print("\n")

    print(f"{name}: Talk soon.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
