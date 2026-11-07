import json

def tool(name, description, props, required):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": props,
                       "required": required}}}

TOOLS = [
    tool("list_events", "List the events of one day",
         {"day": {"type": "string"}}, ["day"]),
    tool("add_event", "Add an event to the calendar",
         {"title": {"type": "string"},
          "minutes": {"type": "integer"}},
         ["title", "minutes"]),
]
IMPL = {"list_events": lambda day: {"day": day, "events": []},
        "add_event": lambda title, minutes: {"added": title}}
PYTHON_TYPE = {"string": str, "integer": int, "boolean": bool,
               "number": (int, float)}

def check_call(name, args, tools=TOOLS):
    # Returns None when the call is fine, else a message that
    # says what is wrong and what would be right
    specs = {t["function"]["name"]: t["function"]
             for t in tools}
    if name not in specs:
        return (f"No tool named {name}. "
                f"Available: {', '.join(sorted(specs))}.")
    schema = specs[name]["parameters"]
    allowed = list(schema["properties"])
    for key in schema["required"]:
        if key not in args:
            return f"{name} needs the parameter {key}."
    for key, value in args.items():
        if key not in allowed:
            return (f"{name} has no parameter {key}. "
                    f"Allowed: {', '.join(allowed)}.")
        kind = schema["properties"][key]["type"]
        wrong = not isinstance(value, PYTHON_TYPE[kind])
        if kind != "boolean" and isinstance(value, bool):
            wrong = True
        if wrong:
            return (f"{key} must be {kind}, "
                    f"got {type(value).__name__}.")

MAX_BAD = 2   # bad calls in a row before the agent is stopped

def execute(name, args, bad_in_a_row):
    problem = check_call(name, args)
    if problem:
        bad_in_a_row += 1
        if bad_in_a_row > MAX_BAD:
            raise RuntimeError("stopped: " + problem)
        return json.dumps({"error": problem}), bad_in_a_row
    return json.dumps(IMPL[name](**args)), 0

if __name__ == "__main__":
    calls = [
        ("add_evnt", {"title": "Team sync", "minutes": 30}),
        ("add_event", {"title": "Team sync"}),
        ("add_event", {"title": "Team sync", "minutes": 30}),
        ("list_events", {"day": "Friday", "timezone": "CET"}),
        ("add_event", {"title": "Team sync", "minutes": "ten"}),
        ("add_event", {"title": "Team sync", "minutes": True}),
    ]
    bad = 0
    for name, args in calls:
        try:
            result, bad = execute(name, args, bad)
            result = json.loads(result)
            result = result.get("error", result)
        except RuntimeError as error:
            result = error
        print(name, args)
        print("   ->", result)
