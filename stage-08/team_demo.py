from agent_run import run_agent
from tracing import TRACE

DOCS = {
    "index": "Topics: refunds, shipping, warranty.",
    "refunds": (
        "Refunds. A customer may ask for a refund within 14 "
        "days of delivery. The product must be unused and in "
        "its original packaging. Refunds go back to the "
        "original payment method within 5 business days of "
        "the return arriving. Digital goods cannot be "
        "refunded once downloaded. Shipping fees are not "
        "refunded unless the product arrived damaged."),
    "shipping": (
        "Shipping. Orders ship within 2 business days. "
        "Standard delivery takes 3 to 7 business days and "
        "express delivery takes 1 to 2. Orders over 50 "
        "dollars ship free with standard delivery. "
        "Tracking numbers are sent by email when the order "
        "leaves the warehouse. We ship only inside the "
        "country."),
    "warranty": (
        "Warranty. Products carry a one year warranty "
        "against defects. Damage caused by misuse is not "
        "covered. To claim, send the order number and a "
        "photo of the defect to support."),
}

def lookup(topic):
    return DOCS.get(topic.lower().strip(), "No such topic.")

TOOLS = [{"type": "function", "function": {
    "name": "lookup",
    "description": "Read one topic from the company handbook. "
                   "Use the topic 'index' to see the topics.",
    "parameters": {"type": "object",
                   "properties": {"topic": {"type": "string"}},
                   "required": ["topic"]}}}]

RESEARCHER = (
    "You are the researcher. Read the handbook with the lookup "
    "tool, starting with the index. Open only the topics the "
    "task needs. Reply with the facts that answer the task, in "
    "short bullet points, and nothing else. Never state a fact "
    "that is not in the handbook.")
WRITER = ("You write one short, friendly paragraph from the "
          "notes.")
REVIEWER = (
    "You review a draft against the notes. Reply with OK if "
    "every claim in the draft appears in the notes, or list "
    "each claim that does not.")

if __name__ == "__main__":
    TRACE.unlink(missing_ok=True)
    task = ("Explain how refunds and shipping work for a new "
            "customer.")
    notes = run_agent("researcher", RESEARCHER, task, TOOLS,
                      {"lookup": lookup})
    draft = run_agent("writer", WRITER,
                      f"{task}\nNotes:\n{notes}")
    verdict = run_agent("reviewer", REVIEWER,
                        f"Notes:\n{notes}\nDraft:\n{draft}")
    print(draft)
    print("Review:", verdict)
