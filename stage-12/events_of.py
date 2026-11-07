import json
from pathlib import Path

def events_of(run, log="audit.jsonl"):
    # Every event of one run, in the order it happened
    found = []
    for line in Path(log).read_text("utf-8").splitlines():
        event = json.loads(line)
        if event["run"] == run:
            found.append(event)
    return found

if __name__ == "__main__":
    # A made-up log with three runs, for the demo
    rows = [
        ("09:00:02", "tidier", "run7", "scan_folder", "after"),
        ("09:00:05", "reporter", "run8", "write_note", "after"),
        ("09:00:09", "tidier", "run7", "move_files", "before"),
        ("09:00:11", "tidier", "run7", "move_files", "after"),
        ("09:00:12", "tidier", "run7", "send_message", "after"),
    ]
    with open("sample_log.jsonl", "w", encoding="utf-8") as f:
        for time, agent, run, action, phase in rows:
            event = {"time": time, "agent": agent, "run": run,
                     "action": action, "phase": phase}
            f.write(json.dumps(event) + "\n")
    for e in events_of("run7", "sample_log.jsonl"):
        print(e["time"], e["agent"], e["action"], e["phase"])
