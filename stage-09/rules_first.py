from cost import cost_of
from tracing import call

MESSAGES = [
    ("I want my money back for order 5521.", "refund"),
    ("When will my package arrive?", "shipping"),
    ("The blender stopped working after three months.", "warranty"),
    ("Can I return the shoes? They don't fit.", "refund"),
    ("Where is my tracking number?", "shipping"),
    ("Do you sell gift cards?", "other"),
    ("This thing is a dud, I want to send it back.", "refund"),
    ("My order never showed up.", "shipping"),
    ("How long is the guarantee on the kettle?", "warranty"),
    ("Please cancel my newsletter.", "other"),
    ("Refund?", "refund"),
    ("Do you ship to Canada?", "shipping"),
]

RULES = {
    "refund": ["refund", "money back", "return"],
    "shipping": ["ship", "tracking", "arrive", "delivery"],
    "warranty": ["warranty", "stopped working"],
}

def by_rules(text):
    # Return a label when a keyword matches, or None when none does
    lower = text.lower()
    for label, words in RULES.items():
        if any(word in lower for word in words):
            return label
    return None

def by_model(text):
    prompt = ("Label this customer message as refund, shipping, "
              "warranty or other. Reply with the label only.\n\n"
              + text)
    messages = [{"role": "user", "content": prompt}]
    reply = call("labeler", messages, max_completion_tokens=5)
    return reply.content.strip()

if __name__ == "__main__":
    right, asked = 0, 0
    for text, truth in MESSAGES:
        label = by_rules(text)
        if label is None:
            label = by_model(text)  # only the leftovers cost money
            asked += 1
        right += label == truth
    print(f"{right} of {len(MESSAGES)} right,",
          f"{asked} messages sent to the model")
