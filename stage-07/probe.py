import json

ROOMS = ["Orion", "Vega", "Lyra"]
BASE = "Reply with only the room name: Orion, Vega or Lyra."
STYLE = "Write in a warm, friendly tone, in full sentences."

def build_messages(request):
    # The instructions come from two places and are joined
    system = BASE + "\n" + STYLE
    return [{"role": "system", "content": system},
            {"role": "user", "content": request}]

def room_from(reply):
    # The check after the model: a known room name, or nothing
    name = reply.strip().rstrip(".")
    return name if name in ROOMS else None

def answer(request, ask):
    messages = build_messages(request)
    with open("last_call.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)   # what was sent
    return room_from(ask(messages))

def good(messages):
    return "Vega"                    # a stand-in for the model

def chatty(messages):
    return "Sure! Vega is free at 3."    # another stand-in

if __name__ == "__main__":
    for ask in (good, chatty):
        result = answer("Book a room at 3.", ask)
        print(ask.__name__, "->", result)
    with open("last_call.json", encoding="utf-8") as f:
        print(json.load(f)[0]["content"])
