#!/usr/bin/env python3
"""Daily scheduler for the ebook-builder workforce.

Cycle: 5 days build → 2 days market, alternating between Track A and Track B.
State persisted to ~/book-builder/state/scheduler.json
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path.home() / "book-builder"
STATE_FILE = BASE / "state" / "scheduler.json"

# Alternating tracks
TRACKS = ["A", "B"]

# 7-day cycle: 0-4 = build, 5-6 = market
BUILD_DAYS = 5
MARKET_DAYS = 2
CYCLE_LENGTH = BUILD_DAYS + MARKET_DAYS  # 7


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "current_cycle": 0,
        "current_day": 0,
        "current_track": "A",
        "last_run": None,
        "completed_books": [],
        "marketing_campaigns": [],
        "history": [],
    }


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_today_action(state):
    """Determine what action to take today based on cycle position."""
    cycle_day = state["current_day"]
    track = state["current_track"]

    if cycle_day < BUILD_DAYS:
        phase = "BUILD"
        day_num = cycle_day + 1
        action = f"Track {track} — Build Day {day_num}/{BUILD_DAYS}"
        agents = get_build_agents(cycle_day)
    else:
        phase = "MARKET"
        day_num = cycle_day - BUILD_DAYS + 1
        action = f"Track {track} — Market Day {day_num}/{MARKET_DAYS}"
        agents = get_market_agents(cycle_day - BUILD_DAYS)

    return {
        "phase": phase,
        "day": day_num,
        "track": track,
        "action": action,
        "agents": agents,
        "date": datetime.now().isoformat(),
    }


def get_build_agents(day):
    """Map build day to primary agents."""
    mapping = {
        0: ["opportunity_scout", "product_strategist"],
        1: ["research_agent"],
        2: ["outline_architect"],
        3: ["author_agent", "google_docs_editor"],
        4: ["editorial_qa", "ebook_production", "product_packaging"],
    }
    return mapping.get(day, [])


def get_market_agents(day):
    """Map market day to primary agents."""
    mapping = {
        0: ["stripe_revenue", "marketing_agent"],
        1: ["customer_feedback", "marketing_agent"],
    }
    return mapping.get(day, [])


def advance(state):
    """Advance the scheduler by one day."""
    state["current_day"] += 1
    state["last_run"] = datetime.now().isoformat()

    # End of cycle
    if state["current_day"] >= CYCLE_LENGTH:
        state["current_day"] = 0
        state["current_cycle"] += 1

        # Alternate track
        current_idx = TRACKS.index(state["current_track"])
        next_idx = (current_idx + 1) % len(TRACKS)
        state["current_track"] = TRACKS[next_idx]

    return state


def run_today():
    """Execute today's scheduled action."""
    state = load_state()
    action = get_today_action(state)

    print(f"=== EBOOK BUILDER — DAILY RUN ===")
    print(f"Date: {action['date'][:10]}")
    print(f"Track: {action['track']}")
    print(f"Phase: {action['phase']} (Day {action['day']})")
    print(f"Action: {action['action']}")
    print(f"Agents: {', '.join(action['agents'])}")
    print()

    # Log to history
    state["history"].append(action)
    if len(state["history"]) > 100:
        state["history"] = state["history"][-100:]

    # Advance state
    state = advance(state)
    save_state(state)

    print(f"Next run: Track {state['current_track']} — {get_today_action(state)['action']}")
    print(f"State saved to: {STATE_FILE}")

    return action


def status():
    """Show current scheduler status."""
    state = load_state()
    action = get_today_action(state)

    print("=== EBOOK BUILDER SCHEDULER STATUS ===")
    print(f"Current cycle: {state['current_cycle'] + 1}")
    print(f"Current track: {state['current_track']}")
    print(f"Current day: {state['current_day'] + 1} of {CYCLE_LENGTH}")
    print(f"Phase: {action['phase']}")
    print(f"Today: {action['action']}")
    print(f"Primary agents: {', '.join(action['agents'])}")
    print(f"Books completed: {len(state['completed_books'])}")
    print(f"Marketing campaigns: {len(state['marketing_campaigns'])}")
    print(f"Last run: {state.get('last_run', 'never')}")
    print(f"\nState file: {STATE_FILE}")

    # Show upcoming schedule
    print("\n=== UPCOMING 7-DAY CYCLE ===")
    temp_state = dict(state)
    for i in range(CYCLE_LENGTH):
        a = get_today_action(temp_state)
        marker = " ← TODAY" if i == 0 else ""
        print(f"  Day {i+1}: {a['action']}{marker}")
        temp_state = advance(temp_state)


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scheduler.py run     — execute today's action")
        print("  python3 scheduler.py status  — show current status")
        print("  python3 scheduler.py reset   — reset state to day 0")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "run":
        run_today()
    elif cmd == "status":
        status()
    elif cmd == "reset":
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        print("State reset. Next run will start from Day 1, Track A.")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
