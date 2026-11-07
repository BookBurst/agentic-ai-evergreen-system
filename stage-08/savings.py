from tracing import client, MODEL
from team_demo import DOCS

def trim(text, limit=300):
    # Keep the start of a long result and say what was cut
    if len(text) <= limit:
        return text
    cut = len(text) - limit
    return text[:limit] + f" [... {cut} more characters cut]"

def tokens_in(text):
    prompt = "Summarize:\n" + text
    messages = [{"role": "user", "content": prompt}]
    reply = client.chat.completions.create(
        model=MODEL, messages=messages, max_completion_tokens=1)
    return reply.usage.prompt_tokens

page = DOCS["refunds"] * 12  # stands in for a long web page
print("full result    ", tokens_in(page), "tokens")
print("trimmed result ", tokens_in(trim(page)), "tokens")
