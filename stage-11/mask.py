import re

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"\b\d{3}[-. ]\d{3}[-. ]\d{4}\b")
KNOWN_NAMES = ["Tomas Berger", "Alicia Moreno"]  # your list

def mask(text):
    # Returns the masked text and the table that undoes it.
    # The table stays on this computer and is never sent.
    table, counts = {}, {}
    def swap(kind, original):
        for placeholder, value in table.items():
            if value == original:
                return placeholder    # same thing, same label
        counts[kind] = counts.get(kind, 0) + 1
        placeholder = f"{kind}_{counts[kind]}"
        table[placeholder] = original
        return placeholder

    for name in KNOWN_NAMES:
        if name in text:
            text = text.replace(name, swap("PERSON", name))
    text = EMAIL.sub(lambda m: swap("EMAIL", m.group()), text)
    text = PHONE.sub(lambda m: swap("PHONE", m.group()), text)
    return text, table

def restore(text, table):
    # Put the real values back into the model's answer
    for placeholder, original in table.items():
        pattern = r"\b" + re.escape(placeholder) + r"\b"
        text = re.sub(pattern, lambda m: original, text)
    return text

def look_at(masked):
    # Pairs of capitalized words are possible names left behind
    return re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", masked)
