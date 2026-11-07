recent = []

def repeated(call, limit=3):
    # True when the same call was made `limit` times in a row
    recent.append(call)
    return recent[-limit:] == [call] * limit

for call in ["search cats", "search cats", "search cats"]:
    if repeated(call):
        print("stop: same call three times in a row")
        break
    print("ok:", call)
