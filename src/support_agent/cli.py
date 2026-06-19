from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import SupportAgent
from .config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Persona-adaptive customer support agent")
    parser.add_argument("--ingest", action="store_true", help="Rebuild the knowledge index and exit")
    parser.add_argument("--json", action="store_true", help="Print full responses as JSON")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    agent = SupportAgent(Settings.from_env(root))
    if args.ingest:
        print(f"Indexed {agent.ingest()} knowledge chunks.")
        return
    print("Support agent ready. Type /quit to exit or /reset to clear conversation memory.")
    while True:
        try:
            message = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if message == "/quit":
            break
        if message == "/reset":
            agent.reset()
            print("Conversation reset.")
            continue
        if not message:
            continue
        result = agent.ask(message)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
            continue
        print(f"Persona: {result.persona.value} ({result.persona_confidence:.0%})")
        print(f"Sources: {', '.join(item.chunk.citation for item in result.retrieved)}")
        print(f"Agent: {result.response}")
        print("Escalation:", "YES" if result.escalation_status else "No")
        if result.escalation_reasons:
            print("Reasons:", "; ".join(result.escalation_reasons))
        if result.handoff_summary:
            print("Handoff summary:\n" + json.dumps(result.handoff_summary, indent=2))


if __name__ == "__main__":
    main()

