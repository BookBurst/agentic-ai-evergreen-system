from corrections import FILE, save, build_prompt

FILE.unlink(missing_ok=True)    # start the demo clean

BASE = "You write short messages for a small design studio."

save("Write a status update about the website redesign",
     "We are almost done!! A few things left.",
     "Done: homepage. In progress: pricing page.")
save("Write a status update about the invoice system",
     "Everything is going great, no problems.",
     "Two of three steps done. One waits for the bank.")
save("Thank the venue for the space",
     "Thanks so much!!!", "Thank you for hosting us.")

print(build_prompt(BASE, "Write a status update about the app"))
print("-" * 20)
print(build_prompt(BASE, "Plan the budget"))
