#!/usr/bin/env python3
"""Run a single agent from the ebook-builder workforce."""

import importlib.util
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE / "agents"


def load_agent(agent_id: str):
    agent_file = AGENTS_DIR / f"{agent_id}.py"
    if not agent_file.exists():
        print(f"ERROR: Agent not found: {agent_file}")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location(agent_id, agent_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_agent.py <agent_id> [context_json]")
        print("\nAvailable agents:")
        for f in sorted(AGENTS_DIR.glob("*.py")):
            print(f"  {f.stem}")
        sys.exit(1)

    agent_id = sys.argv[1]
    context = {}
    if len(sys.argv) > 2:
        context = json.loads(sys.argv[2])

    mod = load_agent(agent_id)
    print(f"=== Running {agent_id} ===")
    print(f"Context: {json.dumps(context, indent=2)}")
    print()

    if not hasattr(mod, "run"):
        print(f"Agent {agent_id} does not implement run(context) yet.")
        print("This is a stub implementation — the agent logic needs to be filled in.")
        sys.exit(0)

    result = mod.run(context)
    print("\n=== Result ===")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
