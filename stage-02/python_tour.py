import json

DAY = "Fri"
# Three JSON notes; one is missing a comma
raw = ['{"title": "Car service", "day": "Mon"}',
       '{"title": "Rent", "day": "Fri"}',
       '{"title": "Piano lesson" "day": "Sat"}']

def parse_note(text):
    # JSON text in, dictionary out
    return json.loads(text)

notes = []
for text in raw:
    try:
        notes.append(parse_note(text))
    except json.JSONDecodeError as err:
        print(f"Skipped a bad note: {err.msg}")

for note in notes:
    if note["day"] == DAY:
        print(f"{note['title']} is due on {DAY}")
print(f"{len(notes)} of {len(raw)} notes read")
