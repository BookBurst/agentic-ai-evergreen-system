from mask import mask, restore, look_at

EMAIL_TEXT = (
    "Hi Tomas,\n"
    "Alicia Moreno asked me to forward this. Call her at "
    "555-014-2345\nor write to alicia.moreno@example.com. "
    "Tomas Berger signed\nthe order, and Wen Zhao will deliver "
    "it. Alicia Moreno agrees."
)

masked, table = mask(EMAIL_TEXT)
print(masked)
print()
for placeholder, original in table.items():
    print(placeholder, "=", original)
print("look at:", look_at(masked))

# A stand-in for the model's answer, written with the labels
reply = "Thanks, PERSON_1. Writing to EMAIL_1."
print()
print(restore(reply, table))
