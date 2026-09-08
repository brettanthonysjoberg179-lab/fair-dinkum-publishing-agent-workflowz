#!/usr/bin/env python3
"""Orchestrator agent runner for the ebook-builder workforce."""

import importlib.util
import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"
WORKFLOW_FILE = Path(__file__).resolve().parent / "orchestrator.yaml"


def load_agent(agent_id: str):
    """Dynamically load an agent module by agent_id."""
    agent_file = AGENTS_DIR / f"{agent_id}.py"
    if not agent_file.exists():
        raise FileNotFoundError(f"Agent file not found: {agent_file}")
    spec = importlib.util.spec_from_file_location(agent_id, agent_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_agent(agent_id: str, context: dict) -> dict:
    """Run a single agent with the given context."""
    mod = load_agent(agent_id)
    if not hasattr(mod, "run"):
        raise NotImplementedError(f"Agent {agent_id} does not implement run(context)")
    return mod.run(context)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 orchestrator.py <agent_id> [context_json]")
        sys.exit(1)
    agent_id = sys.argv[1]
    context = {}
    if len(sys.argv) > 2:
        import json
        context = json.loads(sys.argv[2])
    result = run_agent(agent_id, context)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
