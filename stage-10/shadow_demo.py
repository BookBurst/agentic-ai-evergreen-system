from shadow import trial, NEEDED

REQUESTS = [
    "The website is down and customers cannot log in.",
    "Please update the footer text next week.",
    "The checkout page shows an error.",
    "Can you add a link to the pricing page?",
    "The app crashes when I open settings.",
    "Reset the password for the new intern.",
    "Not urgent, but please review the new logo.",
    "Whenever you can, rename the old folders.",
    "Cannot print from the shared printer.",
    "Add the team photo to the about page.",
]

agreement, differ = trial(REQUESTS)
print(f"agreement {agreement:.0%}, needed {NEEDED:.0%}")
for request, live, new in differ:
    print(f"  {request}")
    print(f"    live {live}, new {new}")
if agreement >= NEEDED:
    print("the new agent may start on a few real tasks")
else:
    print("the new agent stays in shadow")
