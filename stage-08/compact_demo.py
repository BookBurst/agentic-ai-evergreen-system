from compact import compact, count

def say(role, text):
    return {"role": role, "content": text}

HISTORY = [
    say("system", "You help plan a workshop."),
    say("user", "A workshop for 40 people on 12 March, budget "
        "2,400 dollars."),
    say("assistant", "Understood. Venue, caterer and projector "
        "are the main costs. Which first?"),
    say("user", "Venue. The hall near the station costs 900 "
        "dollars."),
    say("assistant", "That leaves 1,500 dollars. Ask a caterer "
        "for a quote for 40 people."),
    say("user", "18 dollars per person, so 720 for 40. "
        "Decision: we take the hall and this caterer."),
    say("assistant", "Good. Total 1,620 dollars, 780 left for "
        "the projector and a margin."),
    say("user", "Projector rental is 150 dollars. What else "
        "is on the list?"),
    say("assistant", "Name tags, a sign-in sheet and a backup "
        "extension cord."),
    say("user", "I have name tags. List what is still open."),
]

def good_summary(old):
    return ("Workshop for 40 people on 12 March, budget 2400 "
            "dollars. The hall near the station costs 900, "
            "which leaves 1500. A caterer quoted 18 dollars "
            "per person, 720 for 40. Decision: take the hall "
            "and this caterer.")

def lossy_summary(old):
    return ("The user is planning a workshop, has chosen a "
            "hall and a caterer, and needs a projector and "
            "some small items.")

print("before:", count(HISTORY), "tokens,", len(HISTORY),
      "messages")
for summarize in (lossy_summary, good_summary):
    result = compact(HISTORY, summarize)
    print(summarize.__name__, "->", count(result), "tokens,",
          len(result), "messages")
