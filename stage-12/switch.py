import json
import time
from pathlib import Path

# One file for all agents: every program imports this module
STATE = Path(__file__).with_name("team_state.json")

class Paused(Exception):
    pass

def set_paused(paused, reason=""):
    state = {"paused": paused, "reason": reason,
             "since": time.strftime("%Y-%m-%d %H:%M:%S")}
    temp = STATE.with_suffix(".tmp")
    temp.write_text(json.dumps(state), "utf-8")
    temp.replace(STATE)           # never half-written

def check_switch():
    # Called by every agent before every step
    if not STATE.exists():
        return
    try:
        state = json.loads(STATE.read_text("utf-8"))
        paused, reason = state["paused"], state["reason"]
    except (ValueError, KeyError, TypeError):
        raise Paused("team paused: state file unreadable")
    if paused:
        raise Paused(f"team paused: {reason}")

def command(text):
    # The reply for a phone command, or None for any other text
    if text == "/pause":
        set_paused(True, "from phone")
        return "Team paused."
    if text == "/resume":
        set_paused(False)
        return "Team running."
    return None
