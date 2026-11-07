import re
from datetime import date

SYMBOLS = {"£": "GBP", "$": "USD", "€": "EUR"}

def parse_money(text):
    # An amount is only usable with its currency attached
    m = re.fullmatch(r"\s*([£$€]|[A-Z]{3})?\s*"
                     r"([\d,]+(?:\.\d+)?)\s*"
                     r"([A-Z]{3})?\s*", text)
    currency = m and (m[1] or m[3])
    if not currency:
        raise ValueError(f"no currency in {text!r}")
    amount = float(m[2].replace(",", ""))
    return amount, SYMBOLS.get(currency, currency)

def parse_date(text, order=None):
    # Dates travel as YYYY-MM-DD, other forms need a known order
    text = text.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return date.fromisoformat(text)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if not m:
        raise ValueError(f"unknown date format: {text!r}")
    a, b, year = int(m[1]), int(m[2]), int(m[3])
    if order == "DMY" or (order is None and a > 12):
        day, month = a, b
    elif order == "MDY" or (order is None and b > 12):
        month, day = a, b
    else:
        raise ValueError(
            f"{text} could be day or month first")
    return date(year, month, day)

if __name__ == "__main__":
    for text in ["GBP 50,000", "50,000", "$50,000"]:
        try:
            print(text, "->", parse_money(text))
        except ValueError as error:
            print(text, "-> rejected:", error)
    cases = [("2026-12-03", None), ("03/12/2026", None),
             ("03/12/2026", "DMY"), ("25/12/2026", None)]
    for text, order in cases:
        label = f"{text} {order}" if order else text
        try:
            print(label, "->", parse_date(text, order))
        except ValueError as error:
            print(label, "-> rejected:", error)
