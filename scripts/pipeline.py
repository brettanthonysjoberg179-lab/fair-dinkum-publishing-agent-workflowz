#!/usr/bin/env python3
"""End-to-end pipeline runner for a single book track."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE / "agents"


def load_agent(agent_id: str):
    agent_file = AGENTS_DIR / f"{agent_id}.py"
    spec = __import__("importlib.util").util.spec_from_file_location(agent_id, agent_file)
    mod = __import__("importlib.util").util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_pipeline(track: str, book_slug: str):
    """Run the full build pipeline for one book."""
    print(f"=== EBOOK PIPELINE: Track {track} — {book_slug} ===")

    context = {
        "track": track,
        "book_slug": book_slug,
        "business_objective": "Build and publish a profitable ebook",
        "target_market": "Australian authors and small publishers",
        "available_resources": "MCP workforce + GitHub + Obsidian + Stripe",
    }

    build_agents = [
        "opportunity_scout",
        "product_strategist",
        "research_agent",
        "outline_architect",
        "author_agent",
        "google_docs_editor",
        "editorial_qa",
        "ebook_production",
        "product_packaging",
    ]

    results = {}
    for agent_id in build_agents:
        print(f"\n--- Agent: {agent_id} ---")
        try:
            mod = load_agent(agent_id)
            if hasattr(mod, "run"):
                result = mod.run(context)
                results[agent_id] = result
                print(f"  Status: completed")
            else:
                print(f"  Status: stub (no run() implementation)")
                results[agent_id] = {"status": "stub", "agent": agent_id}
        except Exception as e:
            print(f"  Status: ERROR — {e}")
            results[agent_id] = {"status": "error", "error": str(e)}

    # Save results
    out_path = BASE / "builds" / book_slug / "pipeline_result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n=== PIPELINE COMPLETE ===")
    print(f"Results saved to: {out_path}")
    return results


def run_marketing(track: str, book_slug: str):
    """Run marketing for an already-built book."""
    print(f"=== MARKETING PIPELINE: Track {track} — {book_slug} ===")

    context = {
        "track": track,
        "book_slug": book_slug,
    }

    marketing_agents = ["stripe_revenue", "marketing_agent", "customer_feedback"]

    results = {}
    for agent_id in marketing_agents:
        print(f"\n--- Agent: {agent_id} ---")
        try:
            mod = load_agent(agent_id)
            if hasattr(mod, "run"):
                result = mod.run(context)
                results[agent_id] = result
                print(f"  Status: completed")
            else:
                print(f"  Status: stub (no run() implementation)")
                results[agent_id] = {"status": "stub", "agent": agent_id}
        except Exception as e:
            print(f"  Status: ERROR — {e}")
            results[agent_id] = {"status": "error", "error": str(e)}

    out_path = BASE / "builds" / book_slug / "marketing_result.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n=== MARKETING COMPLETE ===")
    print(f"Results saved to: {out_path}")
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 pipeline.py build <track> <book-slug>")
        print("  python3 pipeline.py market <track> <book-slug>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "build":
        if len(sys.argv) < 4:
            print("Usage: python3 pipeline.py build <track> <book-slug>")
            sys.exit(1)
        run_pipeline(sys.argv[2], sys.argv[3])
    elif cmd == "market":
        if len(sys.argv) < 4:
            print("Usage: python3 pipeline.py market <track> <book-slug>")
            sys.exit(1)
        run_marketing(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
