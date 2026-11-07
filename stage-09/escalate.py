import json
import re

# Example prices in dollars per 1 million tokens, November 2026
PRICES = {"small": (0.40, 1.60), "large": (2.00, 8.00)}
CALL = (150, 30)   # tokens in and out per call: an assumption

def cost(size):
    price_in, price_out = PRICES[size]
    total = CALL[0] * price_in + CALL[1] * price_out
    return total / 1_000_000

def numbers_in(text):
    # Every number written in the text, "1,200" -> 1200.0
    found = re.findall(r"\d[\d,]*\.?\d*", text)
    return {float(n.replace(",", "")) for n in found}

def passes_check(text, reply):
    # Plain tests the code runs on the model's reply
    try:
        data = json.loads(reply)
    except ValueError:
        return False
    if not isinstance(data, dict):
        return False
    quantity = data.get("quantity")
    if not isinstance(quantity, (int, float)):
        return False
    if quantity != int(quantity):
        return False                  # not a whole number
    return quantity in numbers_in(text)

def answer(text, models):
    # Try the models in order, stop at the first good reply
    for size, ask in models:
        reply = ask(text)
        if passes_check(text, reply):
            return size, reply
    return None, None     # no reply passed: give it to a person
