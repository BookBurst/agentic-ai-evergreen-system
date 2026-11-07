import json
import tiktoken

enc = tiktoken.get_encoding("o200k_base")  # a local estimate

def tokens(system, tools):
    # What every call of the agent sends before any question
    return len(enc.encode(system + json.dumps(tools)))

def tool(name, description):
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": {}}}}

ALL = [tool("read_invoice", "Read one invoice file by name."),
       tool("list_invoices", "List the invoices of a month."),
       tool("send_email", "Send an email to a client."),
       tool("search_web", "Search the web and return pages."),
       tool("make_chart", "Draw a chart from a table."),
       tool("translate", "Translate a text into a language.")]

LONG = ("You are a helpful, careful and friendly assistant "
        "who works for a small company. Your job is to help "
        "with anything the user asks, and in particular with "
        "invoices. Always be polite, always be thorough, think "
        "step by step, double-check your work and explain "
        "your reasoning in detail before you give your final "
        "answer to the user.")
SHORT = ("Check the invoices of the month the user names. "
         "List unpaid ones as: client, amount, days late. "
         "No advice.")

before, after = tokens(LONG, ALL), tokens(SHORT, ALL[:2])
print(f"before: {before} tokens on every call")
print(f"after:  {after} tokens on every call")
print(f"saved over 200 calls: {(before - after) * 200} tokens")
