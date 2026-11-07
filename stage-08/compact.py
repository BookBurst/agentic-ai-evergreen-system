import re
import tiktoken

ENC = tiktoken.get_encoding("o200k_base")
LIMIT = 140      # small for the demo; use a share of the window
KEEP_LAST = 4    # the newest messages always stay as they are

def count(messages):
    # An estimate: the tokens of the text, enough for a limit
    return sum(len(ENC.encode(m["content"])) for m in messages)

def numbers(text):
    # "2,400" and "2400" count as the same number
    found = re.findall(r"\d[\d,.]*\d|\d", text)
    return {n.replace(",", "") for n in found}

def compact(messages, summarize):
    if count(messages) <= LIMIT:
        return messages
    old = messages[1:-KEEP_LAST]      # keep system and newest
    summary = summarize(old)
    before = numbers(" ".join(m["content"] for m in old))
    lost = before - numbers(summary)
    if lost:
        print("lost numbers:", sorted(lost))
        return messages               # better long than wrong
    note = {"role": "user", "content":
            "Summary of the earlier conversation:\n" + summary}
    return [messages[0], note] + messages[-KEEP_LAST:]
