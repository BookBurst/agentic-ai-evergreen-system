import json, os, urllib.request

for line in open(".env"):
    if "=" in line and not line.startswith("#"):
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

TOKEN = os.environ["BOT_TOKEN"]
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
for update in json.load(urllib.request.urlopen(URL))["result"]:
    print(update["message"]["from"]["id"])
